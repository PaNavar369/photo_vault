from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import generate_blob_sas
from azure.storage.blob import BlobSasPermissions
from datetime import datetime, timedelta
import bcrypt
import jwt
import hashlib
import os
import uuid

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb+srv://leo564945_db_user:aru6pwXwzSPBU5OG@imagevault.wm0tbws.mongodb.net/?appName=imagevault"
)

try:
    client = MongoClient(MONGO_URL)
    db = client["imagevault"]
    galleries_collection = db["galleries"]
    users_collection = db["users"]
    images_collection = db["images"]
    # Test connection
    client.admin.command('ping')
    print(" MongoDB connected successfully!")
except Exception as e:
    print(f" MongoDB connection failed: {e}")

# JWT Settings
JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "change_this_to_a_long_random_secret_key_123456789"
)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Azure Blob Storage (Local Emulator)
connection_string = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

try:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_name = "images"
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
        print(" Azure Blob container created/connected")
    except Exception:
        print(" Azure Blob container already exists")
except Exception as e:
    print(f" Azure Blob connection failed: {e}")
    blob_service_client = None
    container_name = "images"

# Helper Functions
def create_token(user):
    payload = {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    token = None
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token:
        token = request.cookies.get("token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def serialize_user(user):
    return {
        "id": str(user["_id"]),
        "first_name": user.get("first_name", ""),
        "last_name": user.get("last_name", ""),
        "email": user.get("email", "")
    }

def serialize_gallery(gallery):
    return {
        "id": str(gallery["_id"]),
        "gallery_name": gallery.get("gallery_name", ""),
        "cover_image": gallery.get("cover_image"),
        "created_at": gallery.get("created_at").isoformat() if gallery.get("created_at") else None
    }

def serialize_image(image):
    return {
        "id": str(image["_id"]),
        "gallery_id": str(image["gallery_id"]),
        "image_name": image.get("image_name", ""),
        "blob_url": image.get("blob_url", ""),
        "uploaded_at": image.get("uploaded_at").isoformat() if image.get("uploaded_at") else None
    }

# Root Endpoint
@app.get("/")
async def root():
    return {"message": "Image Vault API is running"}

# Health Check
@app.get("/health")
async def health():
    return {"success": True, "message": "API is running"}


@app.post("/register")
async def register(request: Request):
    try:
        data = await request.json()
        
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        
        # Validation
        if not first_name:
            raise HTTPException(status_code=400, detail="First name is required")
        if not last_name:
            raise HTTPException(status_code=400, detail="Last name is required")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        if not password or len(password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Check if user exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        try:
            hashed_password = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
        except Exception as e:
            print(f"Hashing error: {e}")
            raise HTTPException(status_code=500, detail="Error hashing password")
        
        # Create user
        new_user = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow()
        }
        
        result = users_collection.insert_one(new_user)
        new_user["_id"] = result.inserted_id
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": serialize_user(new_user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/login")
async def login(request: Request):
    try:
        data = await request.json()
        
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        
        
        user = users_collection.find_one({"email": email})
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        stored_password = user.get("password")
        
        if not stored_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        
        try:
            password_valid = bcrypt.checkpw(
                password.encode('utf-8'),
                stored_password.encode('utf-8')
            )
        except Exception as e:
            print(f"Password verification error: {e}")
            raise HTTPException(status_code=500, detail="Error verifying password")
        
        if not password_valid:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create token
        token = create_token(user)
        
        return {
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": serialize_user(user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/user")
async def get_user(request: Request):
    try:
        user = get_current_user(request)
        return {
            "success": True,
            "user": serialize_user(user)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get user error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")



@app.get("/api/galleries")
async def get_galleries(request: Request):
    try:
        user = get_current_user(request)
        
        galleries = list(
            galleries_collection.find({
                "user_id": str(user["_id"])
            }).sort("created_at", -1)
        )
        
        gallery_list = []
        
        for gallery in galleries:
            first_image = images_collection.find_one(
                {"gallery_id": gallery["_id"]},
                sort=[("uploaded_at", 1)]
            )
            
            if first_image:
                gallery["cover_image"] = first_image["blob_url"]
            else:
                gallery["cover_image"] = None
            
            gallery_list.append(serialize_gallery(gallery))
        
        return {
            "success": True,
            "galleries": gallery_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get galleries error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/create-gallery")
async def create_gallery(request: Request):
    try:
        user = get_current_user(request)
        
        data = await request.json()
        gallery_name = data.get("gallery_name", "").strip()
        
        if not gallery_name:
            raise HTTPException(status_code=400, detail="Gallery name is required")
        
        # Check if gallery exists
        existing_gallery = galleries_collection.find_one({
            "user_id": str(user["_id"]),
            "gallery_name": gallery_name
        })
        
        if existing_gallery:
            return {
                "success": False,
                "message": "Gallery name already exists."
            }
        
        result = galleries_collection.insert_one({
            "user_id": str(user["_id"]),
            "gallery_name": gallery_name,
            "created_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "message": "Gallery created successfully.",
            "gallery_id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create gallery error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.put("/update-gallery/{gallery_id}")
async def update_gallery(gallery_id: str, request: Request):
    try:
        user = get_current_user(request)
        
        if not ObjectId.is_valid(gallery_id):
            raise HTTPException(status_code=400, detail="Invalid gallery ID")
        
        data = await request.json()
        gallery_name = data.get("gallery_name", "").strip()
        
        if not gallery_name:
            raise HTTPException(status_code=400, detail="Gallery name is required")
        
        gallery = galleries_collection.find_one({
            "_id": ObjectId(gallery_id),
            "user_id": str(user["_id"])
        })
        
        if not gallery:
            raise HTTPException(status_code=404, detail="Gallery not found")
        
        # Check if name exists for another gallery
        existing_gallery = galleries_collection.find_one({
            "user_id": str(user["_id"]),
            "gallery_name": gallery_name,
            "_id": {"$ne": ObjectId(gallery_id)}
        })
        
        if existing_gallery:
            return {
                "success": False,
                "message": "Gallery name already exists."
            }
        
        galleries_collection.update_one(
            {"_id": ObjectId(gallery_id)},
            {"$set": {"gallery_name": gallery_name}}
        )
        
        return {
            "success": True,
            "message": "Gallery updated successfully."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update gallery error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.delete("/delete-gallery/{gallery_id}")
async def delete_gallery(gallery_id: str, request: Request):
    try:
        user = get_current_user(request)
        
        if not ObjectId.is_valid(gallery_id):
            raise HTTPException(status_code=400, detail="Invalid gallery ID")
        
        gallery = galleries_collection.find_one({
            "_id": ObjectId(gallery_id),
            "user_id": str(user["_id"])
        })
        
        if not gallery:
            raise HTTPException(status_code=404, detail="Gallery not found")
        
        # Delete all images in the gallery
        images = list(images_collection.find({"gallery_id": ObjectId(gallery_id)}))
        
        for image in images:
            blob_name = image.get("blob_name")
            if blob_name and blob_service_client:
                try:
                    blob_client = blob_service_client.get_blob_client(
                        container=container_name,
                        blob=blob_name
                    )
                    blob_client.delete_blob()
                except Exception:
                    pass
        
        images_collection.delete_many({"gallery_id": ObjectId(gallery_id)})
        galleries_collection.delete_one({"_id": ObjectId(gallery_id)})
        
        return {
            "success": True,
            "message": "Gallery deleted successfully."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete gallery error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/gallery/{gallery_id}")
async def get_gallery(gallery_id: str, request: Request):
    try:
        user = get_current_user(request)
        
        if not ObjectId.is_valid(gallery_id):
            raise HTTPException(status_code=400, detail="Invalid gallery ID")
        
        gallery = galleries_collection.find_one({
            "_id": ObjectId(gallery_id),
            "user_id": str(user["_id"])
        })
        
        if not gallery:
            raise HTTPException(status_code=404, detail="Gallery not found")
        
        images = list(
            images_collection.find({
                "gallery_id": ObjectId(gallery_id)
            }).sort("uploaded_at", -1)
        )
        
        return {
            "success": True,
            "gallery": {
                "id": str(gallery["_id"]),
                "gallery_name": gallery["gallery_name"]
            },
            "images": [serialize_image(image) for image in images]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get gallery error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# ==================== IMAGE ENDPOINTS ====================

@app.post("/upload-image/{gallery_id}")
async def upload_image(gallery_id: str, request: Request, image: UploadFile = File(...)):
    try:
        user = get_current_user(request)
        
        if not ObjectId.is_valid(gallery_id):
            raise HTTPException(status_code=400, detail="Invalid gallery ID")
        
        gallery = galleries_collection.find_one({
            "_id": ObjectId(gallery_id),
            "user_id": str(user["_id"])
        })
        
        if not gallery:
            raise HTTPException(status_code=404, detail="Gallery not found")
        
        # Check file type
        if not image.filename.lower().endswith((".jpg", ".jpeg")):
            return {
                "success": False,
                "message": "Only JPG and JPEG images are allowed."
            }
        
        # Read image
        image_bytes = await image.read()
        image_hash = hashlib.md5(image_bytes).hexdigest()
        
        # Check for duplicates
        duplicate = images_collection.find_one({
            "gallery_id": ObjectId(gallery_id),
            "image_hash": image_hash
        })
        
        if duplicate:
            return {
                "success": False,
                "message": "Image already exists in this gallery."
            }
        
        duplicate_other = images_collection.find_one({
            "user_id": str(user["_id"]),
            "image_hash": image_hash,
            "gallery_id": {"$ne": ObjectId(gallery_id)}
        })
        
        if duplicate_other:
            return {
                "success": False,
                "message": "Image already exists in another gallery."
            }
        
        if not blob_service_client:
            return {
                "success": False,
                "message": "Azure Blob Storage not available."
            }
        
        # Upload to Azure Blob
        file_extension = os.path.splitext(image.filename)[1]
        blob_name = f"{uuid.uuid4()}{file_extension}"
        
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name
        )
        blob_client.upload_blob(image_bytes, overwrite=True)
        
        # Generate SAS URL
        sas_token = generate_blob_sas(
            account_name="devstoreaccount1",
            container_name=container_name,
            blob_name=blob_name,
            account_key="Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(days=365)
        )
        
        blob_url = f"{blob_client.url}?{sas_token}"
        
        # Save to database
        result = images_collection.insert_one({
            "gallery_id": ObjectId(gallery_id),
            "user_id": str(user["_id"]),
            "image_name": image.filename,
            "blob_name": blob_name,
            "blob_url": blob_url,
            "image_hash": image_hash,
            "uploaded_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "message": "Image uploaded successfully.",
            "image_id": str(result.inserted_id),
            "blob_url": blob_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload image error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.delete("/delete-image/{image_id}")
async def delete_image(image_id: str, request: Request):
    try:
        user = get_current_user(request)
        
        if not ObjectId.is_valid(image_id):
            raise HTTPException(status_code=400, detail="Invalid image ID")
        
        image = images_collection.find_one({
            "_id": ObjectId(image_id),
            "user_id": str(user["_id"])
        })
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        blob_name = image.get("blob_name")
        if blob_name and blob_service_client:
            try:
                blob_client = blob_service_client.get_blob_client(
                    container=container_name,
                    blob=blob_name
                )
                blob_client.delete_blob()
            except Exception:
                pass
        
        images_collection.delete_one({"_id": ObjectId(image_id)})
        
        return {
            "success": True,
            "message": "Image deleted successfully."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete image error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# ==================== SHARING ENDPOINTS ====================

@app.get("/api/users")
async def get_users(request: Request):
    try:
        current_user = get_current_user(request)
        
        users = list(
            users_collection.find(
                {"_id": {"$ne": current_user["_id"]}},
                {"password": 0}
            )
        )
        
        return {
            "success": True,
            "users": [serialize_user(user) for user in users]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get users error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/shareGallery/{gallery_id}")
async def share_gallery(gallery_id: str, request: Request):
    try:
        current_user = get_current_user(request)
        
        if not ObjectId.is_valid(gallery_id):
            raise HTTPException(status_code=400, detail="Invalid gallery ID")
        
        data = await request.json()
        emails = data.get("emails", [])
        
        if not emails:
            return {
                "success": False,
                "message": "No users selected."
            }
        
        gallery = galleries_collection.find_one({
            "_id": ObjectId(gallery_id),
            "user_id": str(current_user["_id"])
        })
        
        if not gallery:
            raise HTTPException(status_code=404, detail="Gallery not found")
        
        original_images = list(
            images_collection.find({"gallery_id": ObjectId(gallery_id)})
        )
        
        shared_count = 0
        
        for email in emails:
            user = users_collection.find_one({"email": email.lower()})
            
            if not user or user["_id"] == current_user["_id"]:
                continue
            
            existing_shared = galleries_collection.find_one({
                "user_id": str(user["_id"]),
                "shared_from": str(gallery["_id"])
            })
            
            if existing_shared:
                continue
            
            # Create shared gallery
            new_gallery = {
                "user_id": str(user["_id"]),
                "gallery_name": gallery["gallery_name"],
                "created_at": datetime.utcnow(),
                "shared_from": str(gallery["_id"]),
                "shared_by": str(current_user["_id"])
            }
            
            result = galleries_collection.insert_one(new_gallery)
            new_gallery_id = result.inserted_id
            
            # Share images
            for image in original_images:
                new_image = {
                    "gallery_id": new_gallery_id,
                    "user_id": str(user["_id"]),
                    "image_name": image["image_name"],
                    "blob_name": image.get("blob_name"),
                    "blob_url": image["blob_url"],
                    "image_hash": image["image_hash"],
                    "uploaded_at": image["uploaded_at"]
                }
                images_collection.insert_one(new_image)
            
            shared_count += 1
        
        return {
            "success": True,
            "message": f"Gallery shared with {shared_count} user(s)."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Share gallery error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# ==================== DEBUG ENDPOINTS ====================

@app.get("/debug/users")
async def debug_users():
    try:
        users = list(users_collection.find({}, {"password": 1, "email": 1}))
        result = []
        for user in users:
            result.append({
                "id": str(user["_id"]),
                "email": user.get("email"),
                "has_password": bool(user.get("password")),
                "password_length": len(user.get("password", ""))
            })
        return {
            "total_users": len(result),
            "users": result
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/debug/reset-password")
async def reset_password(request: Request):
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        new_password = data.get("new_password", "")
        
        if not email or not new_password:
            raise HTTPException(status_code=400, detail="Email and new_password are required")
        
        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        user = users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        hashed_password = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        users_collection.update_one(
            {"email": email},
            {"$set": {"password": hashed_password}}
        )
        
        return {
            "success": True,
            "message": f"Password reset for {email}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}

