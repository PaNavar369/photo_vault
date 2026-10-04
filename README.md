# 📸 Image Vault

Image Vault is a full-stack image gallery application that allows users to create galleries, upload and manage images, and share galleries with other registered users.

The project uses a React/Vite frontend and a FastAPI backend, with MongoDB for application data and Azure Blob Storage/Azurite for image storage.

## ✨ Features

### 🔐 Authentication
- User registration
- User login
- JWT-based authentication
- Password hashing with bcrypt
- Protected API endpoints

### 🗂️ Gallery Management
- Create galleries
- View galleries
- Rename galleries
- Delete galleries
- Gallery cover images
- Prevent duplicate gallery names

### 🖼️ Image Management
- Upload JPG and JPEG images
- Store images in Azure Blob Storage
- Generate SAS URLs for image access
- View images inside galleries
- Delete images
- Detect duplicate images using image hashes
- Prevent the same image from being added to multiple galleries

### 🤝 Gallery Sharing
- View registered users
- Share galleries with other users
- Share gallery images with selected users
- Prevent duplicate shared galleries

## 🛠️ Technology Stack

### Frontend
- React
- Vite
- JavaScript
- HTML5
- CSS

### Backend
- Python
- FastAPI
- Uvicorn
- JWT
- bcrypt
- python-multipart

### Database
- MongoDB
- PyMongo

### Storage
- Azure Blob Storage
- Azurite / Azure Storage Emulator for local development

## 📁 Project Structure

A typical project structure is:

```text
Image_gallery/
├── frontend/
│   ├── src/
│   │   └── main.jsx
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── .env
├── .env.example
├── .gitignore
└── README.md
```

Adjust the structure above if your local folder names are different.

## ⚙️ Requirements

Before running the project, install:

- Python 3.x
- Node.js and npm
- MongoDB
- Azurite (for local Azure Blob Storage development)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/PaNavar369/photo_vault.git
cd photo_vault
```

## 🐍 Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

### Windows PowerShell

```powershell
python -m venv env
```

Activate it:

```powershell
.\env\Scripts\Activate.ps1
```

If PowerShell prevents script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then activate the environment again:

```powershell
.\env\Scripts\Activate.ps1
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

### Backend Dependencies

The backend uses packages including:

```text
fastapi
uvicorn
pymongo
azure-storage-blob
google-auth
Jinja2
python-multipart
requests
```

## 🔐 Environment Variables

Do not place database passwords, storage keys, or JWT secrets directly in the source code.

Create a local `.env` file:

```env
MONGO_URL=your_mongodb_connection_string
JWT_SECRET=your_long_random_secret
AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string
AZURE_ACCOUNT_KEY=your_azure_account_key
```

The `.env` file should not be committed to GitHub.

You can provide an `.env.example` file containing only placeholders:

```env
MONGO_URL=
JWT_SECRET=
AZURE_STORAGE_CONNECTION_STRING=
AZURE_ACCOUNT_KEY=
```

## ▶️ Run the Backend

From the backend directory:

```bash
python -m uvicorn main:app --reload
```

The API normally runs at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## ⚛️ Frontend Setup

Open a second terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install the frontend dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend normally runs at:

```text
http://localhost:5173
```

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Register a new user |
| POST | `/login` | Login |
| GET | `/api/user` | Get the authenticated user |

### Galleries

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/galleries` | Get the user's galleries |
| POST | `/create-gallery` | Create a gallery |
| PUT | `/update-gallery/{gallery_id}` | Rename a gallery |
| DELETE | `/delete-gallery/{gallery_id}` | Delete a gallery |
| GET | `/api/gallery/{gallery_id}` | Get a gallery and its images |

### Images

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload-image/{gallery_id}` | Upload an image |
| DELETE | `/delete-image/{image_id}` | Delete an image |

### Sharing

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/users` | Get users available for sharing |
| POST | `/shareGallery/{gallery_id}` | Share a gallery |

### Health

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |

## 🖼️ Image Upload

The application currently accepts:

- `.jpg`
- `.jpeg`

During upload, the backend:

1. Authenticates the user.
2. Checks that the gallery belongs to the user.
3. Validates the image type.
4. Reads the image.
5. Generates an image hash.
6. Checks for duplicate images.
7. Uploads the image to Blob Storage.
8. Generates a SAS URL.
9. Stores image metadata in MongoDB.

## 🗄️ MongoDB

The application uses MongoDB collections for:

- `users`
- `galleries`
- `images`

User passwords are hashed using bcrypt before being stored.

## ☁️ Azure Blob Storage

Images are stored in an Azure Blob Storage container named:

```text
images
```

For local development, the project can use an Azure Storage emulator such as Azurite.

## 🔒 Security Notes

Never commit the following to GitHub:

- MongoDB connection strings containing passwords
- Azure storage account keys
- JWT secrets
- `.env` files
- Other API keys or credentials

Keep secrets in environment variables and add `.env` to `.gitignore`.

If a credential has previously been exposed or committed, rotate/revoke it before making the repository public.

## 🧪 Development

Start the backend in one terminal:

```bash
python -m uvicorn main:app --reload
```

Start the frontend in another terminal:

```bash
npm run dev
```

Then open the frontend in your browser:

```text
http://localhost:5173
```

## 📌 Future Improvements

Potential future improvements include:

- PNG and WebP support
- Image search and filtering
- Image tags and categories
- Pagination
- Drag-and-drop uploads
- Image compression
- More granular sharing permissions
- Responsive mobile improvements
- Automated testing
- Production deployment

## 👨‍💻 Author

**PaNavar369**

GitHub:  
https://github.com/PaNavar369

## 📄 License

This project is for educational and personal development purposes.
