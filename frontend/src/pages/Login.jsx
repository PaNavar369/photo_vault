import { useState } from "react";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (event) => {
    event.preventDefault();

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            password: password,
          }),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        alert(result.detail || "Login failed");
        return;
      }

      localStorage.setItem("token", result.token);

      localStorage.setItem(
        "user",
        JSON.stringify(result.user)
      );

      alert("Login successful!");

      window.location.href = "/Home";

    } catch (error) {
      console.error(error);
      alert("Unable to connect to server");
    }
  };

  return (
    <div className="auth-container">

      <div className="auth-card">

        <h1>Image Vault</h1>

        <h2>Welcome Back</h2>

        <p className="subtitle">
          Sign in to manage your galleries
        </p>

        <form onSubmit={handleLogin}>

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
            Login
          </button>

        </form>

        <p className="auth-link">

          Don't have an account?

          <a href="/register">
            {" "}Create Account
          </a>

        </p>

      </div>

    </div>
  );
}

export default Login;