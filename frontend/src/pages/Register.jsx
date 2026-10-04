import { useState } from "react";

function Register() {

  const [firstName, setFirstName] = useState("");

  const [lastName, setLastName] = useState("");

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const handleRegister = async (event) => {

    event.preventDefault();

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/register",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({

            first_name: firstName,

            last_name: lastName,

            email: email,

            password: password

          })

        }
      );

      const result = await response.json();

      if (!response.ok) {

        alert(
          result.detail ||
          "Registration failed"
        );

        return;

      }

      alert("Account created successfully!");

      window.location.href = "/";

    }

    catch (error) {

      console.error(error);

      alert("Unable to connect to server");

    }

  };

  return (

    <div className="auth-container">

      <div className="auth-card">

        <h1>Image Vault</h1>

        <h2>Create Account</h2>

        <p className="subtitle">

          Create an account to manage your galleries

        </p>

        <form onSubmit={handleRegister}>

          <div className="form-group">

            <label>First Name</label>

            <input

              type="text"

              placeholder="Enter your first name"

              value={firstName}

              onChange={(event) =>
                setFirstName(event.target.value)
              }

              required

            />

          </div>

          <div className="form-group">

            <label>Last Name</label>

            <input

              type="text"

              placeholder="Enter your last name"

              value={lastName}

              onChange={(event) =>
                setLastName(event.target.value)
              }

              required

            />

          </div>

          <div className="form-group">

            <label>Email Address</label>

            <input

              type="email"

              placeholder="Enter your email"

              value={email}

              onChange={(event) =>
                setEmail(event.target.value)
              }

              required

            />

          </div>

          <div className="form-group">

            <label>Password</label>

            <input

              type="password"

              placeholder="Enter your password"

              value={password}

              onChange={(event) =>
                setPassword(event.target.value)
              }

              required

            />

          </div>

          <button
            type="submit"
            className="primary-btn"
          >
            Create Account
          </button>

        </form>

        <p className="auth-link">

          Already have an account?

          <a href="/">
            Login
          </a>

        </p>

      </div>

    </div>

  );

}

export default Register;