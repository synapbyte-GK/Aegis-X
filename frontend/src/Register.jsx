import { useState } from "react";

const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:8002`;

function Register({ onRegistered, onBackToLogin }) {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (
      !fullName.trim() ||
      !email.trim() ||
      !password
    ) {
      setError("Please complete all fields.");
      return;
    }

    if (password.length < 8) {
      setError(
        "Password must contain at least 8 characters."
      );
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/auth/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            full_name: fullName.trim(),
            email: email.trim(),
            password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Registration failed."
        );
      }

      setSuccess(
        "Account created successfully. Redirecting to login..."
      );

      setTimeout(() => {
        onRegistered();
      }, 1200);
    } catch (registerError) {
      setError(
        registerError.message ||
          "Unable to create account."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-screen">
      <div className="login-grid" />
      <div className="login-noise" />

      <div className="login-orb orb-one" />
      <div className="login-orb orb-two" />
      <div className="login-orb orb-three" />

      <div className="login-scanline" />

      <div className="login-corner corner-tl" />
      <div className="login-corner corner-tr" />
      <div className="login-corner corner-bl" />
      <div className="login-corner corner-br" />

      <section className="login-layout register-layout">
        <div className="login-info">
          <div className="login-brand">
            <div className="brand-mark login-mark">
              <span />
              <span />
              <span />
            </div>

            <div>
              <div className="brand-name">
                AEGIS-X
              </div>

              <div className="brand-sub">
                SECURITY OPERATIONS CENTER
              </div>
            </div>
          </div>

          <div className="login-info-copy">
            <div className="login-eyebrow">
              <span className="login-live-dot" />
              SECURE IDENTITY LAYER
            </div>

            <h1>
              Create your
              <br />
              <span>security identity.</span>
            </h1>

            <p>
              Create an Aegis-X account to access
              your authorized security operations
              workspace and monitored assets.
            </p>
          </div>

          <div className="login-status-grid">
            <div className="login-status-card">
              <span>IDENTITY</span>
              <strong>VERIFIED</strong>
            </div>

            <div className="login-status-card">
              <span>ACCESS</span>
              <strong>CONTROLLED</strong>
            </div>

            <div className="login-status-card">
              <span>SESSION</span>
              <strong>SECURE</strong>
            </div>
          </div>
        </div>

        <div className="login-panel-wrap">
          <div className="login-ring ring-one" />
          <div className="login-ring ring-two" />

          <div className="login-card">
            <div className="login-card-top">
              <div className="login-lock">
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path d="M12 3a4 4 0 0 0-4 4v3" />
                  <rect
                    x="5"
                    y="10"
                    width="14"
                    height="10"
                    rx="2"
                  />
                  <path d="M12 14v2" />
                  <path d="M16 7a4 4 0 0 0-4-4" />
                </svg>
              </div>

              <div className="login-security-state">
                <span />
                <span>SECURE CHANNEL</span>
              </div>
            </div>

            <div className="login-heading">
              <span className="panel-kicker">
                CREATE ACCOUNT
              </span>

              <h2>Get started</h2>

              <p>
                Create your Aegis-X security
                operations account.
              </p>
            </div>

            <form
              className="login-form"
              onSubmit={handleSubmit}
            >
              <label className="login-field">
                <span>Full name</span>

                <div className="login-input-wrap">
                  <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <circle
                      cx="12"
                      cy="8"
                      r="4"
                    />
                    <path d="M4 20a8 8 0 0 1 16 0" />
                  </svg>

                  <input
                    type="text"
                    value={fullName}
                    onChange={(event) =>
                      setFullName(
                        event.target.value
                      )
                    }
                    placeholder="Your full name"
                    autoComplete="name"
                  />
                </div>
              </label>

              <label className="login-field">
                <span>Email address</span>

                <div className="login-input-wrap">
                  <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <rect
                      x="3"
                      y="5"
                      width="18"
                      height="14"
                      rx="2"
                    />
                    <path d="m3 7 9 6 9-6" />
                  </svg>

                  <input
                    type="email"
                    value={email}
                    onChange={(event) =>
                      setEmail(
                        event.target.value
                      )
                    }
                    placeholder="name@example.com"
                    autoComplete="email"
                  />
                </div>
              </label>

              <label className="login-field">
                <span>Password</span>

                <div className="login-input-wrap">
                  <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <rect
                      x="5"
                      y="10"
                      width="14"
                      height="10"
                      rx="2"
                    />
                    <path d="M8 10V7a4 4 0 0 1 8 0v3" />
                  </svg>

                  <input
                    type="password"
                    value={password}
                    onChange={(event) =>
                      setPassword(
                        event.target.value
                      )
                    }
                    placeholder="Minimum 8 characters"
                    autoComplete="new-password"
                  />
                </div>
              </label>

              {error && (
                <div className="login-error">
                  <span>!</span>
                  {error}
                </div>
              )}

              {success && (
                <div className="login-success">
                  <span>✓</span>
                  {success}
                </div>
              )}

              <button
                className="login-submit"
                type="submit"
                disabled={loading}
              >
                <span className="login-submit-glow" />

                <span className="login-submit-content">
                  {loading
                    ? "CREATING ACCOUNT..."
                    : "CREATE ACCOUNT"}

                  {!loading && (
                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path d="M5 12h14" />
                      <path d="m13 6 6 6-6 6" />
                    </svg>
                  )}
                </span>
              </button>
            </form>

            <button
              type="button"
              className="auth-switch"
              onClick={onBackToLogin}
            >
              <span>
                Already have an account?
              </span>

              <strong>
                SIGN IN
              </strong>
            </button>

            <div className="login-card-footer">
              <div>
                <span className="footer-dot" />
                Protected environment
              </div>

              <span>AEGIS-X v1.0</span>
            </div>
          </div>
        </div>
      </section>

      <div className="login-bottom-bar">
        <span>
          AUTHORIZED ACCESS ONLY
        </span>

        <span className="login-bottom-line" />

        <span>
          SOC ENGINE / IDENTITY CONTROL
        </span>
      </div>
    </main>
  );
}

export default Register;