import { useEffect, useState } from "react";

function Home() {
  const [user, setUser] = useState(null);
  const [galleries, setGalleries] = useState([]);
  const [galleryName, setGalleryName] = useState("");
  const [showForm, setShowForm] = useState(false);

  const getToken = () => {
    return localStorage.getItem("token");
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/";
  };

  const loadUser = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/user", {
        headers: {
          Authorization: `Bearer ${getToken()}`
        }
      });

      if (!response.ok) {
        logout();
        return;
      }

      const result = await response.json();
      setUser(result.user);
    } catch (error) {
      console.error("Error loading user:", error);
    }
  };

  const loadGalleries = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/galleries", {
        headers: {
          Authorization: `Bearer ${getToken()}`
        }
      });

      if (!response.ok) {
        return;
      }

      const result = await response.json();
      setGalleries(result.galleries);
    } catch (error) {
      console.error("Error loading galleries:", error);
    }
  };

  const createGallery = async () => {
    if (!galleryName.trim()) {
      alert("Please enter a gallery name");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/create-gallery", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getToken()}`
        },
        body: JSON.stringify({
          gallery_name: galleryName
        })
      });

      const result = await response.json();

      if (!result.success) {
        alert(result.message);
        return;
      }

      setGalleryName("");
      setShowForm(false);
      loadGalleries();
    } catch (error) {
      console.error("Error creating gallery:", error);
      alert("Failed to create gallery");
    }
  };

  const deleteGallery = async (galleryId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this gallery?"
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/delete-gallery/${galleryId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      const result = await response.json();

      if (!result.success) {
        alert(result.message || "Unable to delete gallery");
        return;
      }

      loadGalleries();
    } catch (error) {
      console.error("Error deleting gallery:", error);
      alert("Failed to delete gallery");
    }
  };

  const editGallery = async (gallery) => {
    const newName = window.prompt(
      "Enter new gallery name",
      gallery.gallery_name
    );

    if (!newName) {
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/update-gallery/${gallery.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getToken()}`
          },
          body: JSON.stringify({
            gallery_name: newName
          })
        }
      );

      const result = await response.json();

      if (!result.success) {
        alert(result.message);
        return;
      }

      loadGalleries();
    } catch (error) {
      console.error("Error editing gallery:", error);
      alert("Failed to update gallery");
    }
  };

  const openGallery = (galleryId) => {
    window.location.href = `/gallery/${galleryId}`;
  };

  useEffect(() => {
    loadUser();
    loadGalleries();
  }, []);

  return (
    <div className="home-page">
      {/* Navbar */}
      <nav className="navbar">
        <div className="logo">Image Vault</div>
        <div className="welcome">
          Welcome {user ? user.first_name : ""}
        </div>
        <button className="logout-btn" onClick={logout}>
          Logout
        </button>
      </nav>

      {/* Main Content */}
      <div className="container">
        <h2>Your Galleries</h2>

        <div className="button-container">
          <button
            className="add-gallery-btn"
            onClick={() => setShowForm(!showForm)}
          >
            + Add Gallery
          </button>
        </div>

        {/* Create Gallery Form */}
        {showForm && (
          <div className="gallery-form">
            <input
              type="text"
              placeholder="Enter Gallery Name"
              value={galleryName}
              onChange={(event) => setGalleryName(event.target.value)}
            />
            <button onClick={createGallery}>Create Gallery</button>
          </div>
        )}

        {/* Galleries Grid */}
        <div className="gallery-container">
          {galleries.length > 0 ? (
            galleries.map((gallery) => (
              <div className="gallery-card" key={gallery.id}>
                {gallery.cover_image ? (
                  <img
                    src={gallery.cover_image}
                    className="gallery-cover"
                    alt="Gallery Cover"
                  />
                ) : (
                  <div className="gallery-placeholder">No Image</div>
                )}

                <h3
                  className="gallery-title"
                  onClick={() => openGallery(gallery.id)}
                >
                  {gallery.gallery_name}
                </h3>

                <div className="gallery-actions">
                  <button
                    className="edit-btn"
                    onClick={() => editGallery(gallery)}
                  >
                    Edit
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => deleteGallery(gallery.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          ) : (
            <p>No galleries created yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Home;