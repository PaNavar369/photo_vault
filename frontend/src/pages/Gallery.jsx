import { useEffect, useState } from "react";

function Gallery() {

  const [gallery,setGallery] = useState(null);
  const [images, setImages] = useState([]);


  const getToken = () => {

    return localStorage.getItem(
      "token"
    );

  };


  const getGalleryId = () => {
    const path =
      window.location.pathname;
    const parts =
      path.split("/");
    return parts[2];

  };


  const loadGallery = async () => {

    const galleryId =getGalleryId();

    try {

      const response = await fetch(
        `http://127.0.0.1:8000/api/gallery/${galleryId}`,

        {
          headers: {
            Authorization:
              `Bearer ${getToken()}`
          }
        }
      );
      if (!response.ok) {
        alert(
          "Unable to load gallery"
        );
        return;
      }
      const result =
        await response.json();
      setGallery(result.gallery );
      setImages(result.images);
    }
    catch (error) {
      console.error(error);
    }

  };

  useEffect(() => {
    loadGallery();
  }, []);

  const uploadImage = async (
    event
  ) => {
    const file = event.target.files[0];
    if (!file) {
      return;
    }
    const fileName =
      file.name.toLowerCase();
    if (
      !fileName.endsWith(".jpg") &&
      !fileName.endsWith(".jpeg")
    ) {
      alert(
        "Only JPG and JPEG images are allowed."
      );
      event.target.value = "";
      return;
    }


    const formData =new FormData();
    formData.append( "image", file);

    const galleryId =getGalleryId();
    try {
      const response = await fetch(

        `http://127.0.0.1:8000/upload-image/${galleryId}`,

        {

          method: "POST",

          headers: {
            Authorization:
              `Bearer ${getToken()}`
          },
          body: formData
        }
      );
      const result = await response.json();
      if (!result.success) {
        alert(result.message);
        return;
      }
      event.target.value = "";
      loadGallery();
    }

    catch (error) {
      console.error(error);
      alert(
        "Unable to upload image"
      );
    }

  };
  const deleteImage = async (
    imageId
  ) => {
    const confirmed =
      window.confirm(
        "Are you sure you want to delete this image?"
      );
    if (!confirmed) {
      return;
    }

    try {

      const response = await fetch(

        `http://127.0.0.1:8000/delete-image/${imageId}`,

        {
          method: "DELETE",
          headers: {
            Authorization:
              `Bearer ${getToken()}`
          }

        }

      );
      const result =
        await response.json();

      if (!result.success) {
        alert(
          result.message ||
          "Unable to delete image"
        );
        return;
      }
    loadGallery();

    }

    catch (error) {
      console.error(error);
    }

  };

  const goBack = () => {
    window.location.href =
      "/home";

  };
  return (

    <div>

      <nav className="navbar">
        <h1>
          {
            gallery
              ? gallery.gallery_name
              : "Gallery"
          }
        </h1>
        <button className="back-btn" onClick={goBack} >
          Back
          </button>
      </nav>
      <div className="container">
        <div className="upload-section">
          <label className="upload-btn">
            Upload Image
            <input
              type="file"
              accept=".jpg,.jpeg,image/jpeg"
              onChange={uploadImage}
              style={{
                display: "none"
              }}
            />
          </label>

        </div>
        <div className="images-container">
          {images.length > 0 ? (
            images.map(
              (image) => (
                <div
                  className="image-card"
                  key={image.id} >
                  <img
                    src={
                      image.blob_url
                    }
                    alt={
                      image.image_name
                    }
                  />
                  <button className="delete-btn" onClick={() =>
                      deleteImage(
                        image.id
                      )
                    }
                  >
                    Delete
                  </button>
                </div>

              )

            )

          ) : (

            <p>

              No images uploaded yet.

            </p>

          )}

        </div>

      </div>

    </div>

  );

}

export default Gallery;