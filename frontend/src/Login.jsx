import { useState } from "react";

const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:8002`;

function Login({ onLogin, onRegister }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(event) {
        event.preventDefault();

        setError("");

        if (!email.trim() || !password) {
            setError("Enter your email and password.");
            return;
        }

        setLoading(true);

        try {
            const response = await fetch(
                `${API_BASE_URL}/auth/login`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        email: email.trim(),
                        password,
                    }),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Authentication failed."
                );
            }

            localStorage.setItem(
                "aegis_x_token",
                data.access_token
            );

            localStorage.setItem(
                "aegis_x_user",
                JSON.stringify(data.user)
            );

            onLogin(data.user, data.access_token);
        } catch (loginError) {
            setError(
                loginError.message ||
                "Unable to connect to Aegis-X."
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

            <section className="login-layout">
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
                            DEFENSE SYSTEM ONLINE
                        </div>

                        <h1>
                            Secure control
                            <br />
                            for your
                            <span> digital perimeter.</span>
                        </h1>

                        <p>
                            Monitor devices, detect anomalies,
                            investigate threats and operate your
                            security environment from one unified
                            SOC workspace.
                        </p>
                    </div>

                    <div className="login-status-grid">
                        <div className="login-status-card">
                            <span>NETWORK</span>
                            <strong>PROTECTED</strong>
                        </div>

                        <div className="login-status-card">
                            <span>DETECTION</span>
                            <strong>ACTIVE</strong>
                        </div>

                        <div className="login-status-card">
                            <span>ENGINE</span>
                            <strong>ONLINE</strong>
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
                                    <rect
                                        x="5"
                                        y="10"
                                        width="14"
                                        height="10"
                                        rx="2"
                                    />
                                    <path d="M8 10V7a4 4 0 0 1 8 0v3" />
                                    <path d="M12 14v2" />
                                </svg>
                            </div>

                            <div className="login-security-state">
                                <span />
                                <span>SECURE CHANNEL</span>
                            </div>
                        </div>

                        <div className="login-heading">
                            <span className="panel-kicker">
                                AUTHENTICATION
                            </span>

                            <h2>Welcome back</h2>

                            <p>
                                Sign in to access your Aegis-X
                                security workspace.
                            </p>
                        </div>

                        <form
                            className="login-form"
                            onSubmit={handleSubmit}
                        >
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
                                            setEmail(event.target.value)
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
                                        type={
                                            showPassword
                                                ? "text"
                                                : "password"
                                        }
                                        value={password}
                                        onChange={(event) =>
                                            setPassword(event.target.value)
                                        }
                                        placeholder="Enter your password"
                                        autoComplete="current-password"
                                    />

                                    <button
                                        type="button"
                                        className="password-toggle"
                                        onClick={() =>
                                            setShowPassword(
                                                (current) => !current
                                            )
                                        }
                                        aria-label={
                                            showPassword
                                                ? "Hide password"
                                                : "Show password"
                                        }
                                    >
                                        {showPassword ? "HIDE" : "SHOW"}
                                    </button>
                                </div>
                            </label>

                            {error && (
                                <div className="login-error">
                                    <span>!</span>
                                    {error}
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
                                        ? "AUTHENTICATING..."
                                        : "SIGN IN"}

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
                            onClick={onRegister}
                        >
                            <span>
                                New to Aegis-X?
                            </span>

                            <strong>
                                CREATE ACCOUNT
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
                    SOC ENGINE / ENCRYPTED SESSION
                </span>
            </div>
        </main>
    );
}

export default Login;