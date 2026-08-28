/**
 * ============================================================================
 * LOGIN FORM COMPONENT — Smart Gym Authentication
 * ============================================================================
 *
 * State-managed React component that handles the login form.
 * Integrates with authService.js for API calls (mock or real).
 *
 * ─── FORM FIELDS → DATABASE MAPPING ───
 *   Form "Username"  →  API payload "username"  →  DB column "users.email"
 *   Form "Password"  →  API payload "password"  →  Backend bcrypt-compares against "users.password_hash"
 *
 * ─── ROLE DETECTION ───
 *   No checkbox needed. The backend looks up the user by email,
 *   verifies the password, and returns the role from the DB (`users.role`).
 *   Admin accounts simply have role='admin' in the database.
 *
 * ─── REDIRECT LOGIC ───
 *   On success: role === 'admin'  → navigate('/admin/dashboard')
 *               role === 'member' → navigate('/user/dashboard')
 *
 * ─── TEST ACCOUNTS ───
 *   Admin:  admin_test@smartgym.com  / admin123
 *   Member: user_test@smartgym.com   / user123
 *
 * ============================================================================
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser, saveAuthData } from "../../services/authService";
import "./LoginForm.css";

// Lucide icons for the form fields
import { Mail, Lock, Eye, EyeOff, Loader2 } from "lucide-react";

/**
 * @param {Object} props
 * @param {Function} props.onSwitchToRegister - Callback to trigger the slide animation
 *                                              to the Register form view
 */
export default function LoginForm({ onSwitchToRegister }) {
  const navigate = useNavigate();

  // ── Form State ──
  // `username` maps to the `email` column in PostgreSQL `users` table
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  // ── UI State ──
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  /**
   * Handle form submission.
   * Constructs the API payload and calls the auth service.
   *
   * Payload sent to POST /api/auth/login:
   * {
   *   "username": "user@email.com",     ← maps to users.email
   *   "password": "plaintext"            ← backend compares against users.password_hash
   * }
   *
   * The backend determines the role automatically from the `users.role` column.
   * No role_request field is needed — just enter the correct email + password.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    // ── Basic client-side validation ──
    if (!username.trim() || !password.trim()) {
      setErrorMessage("Please fill in all fields.");
      return;
    }

    setIsLoading(true);

    try {
      // ── Call auth service (mock or real, configured in authService.js) ──
      // The backend auto-detects role from the user's DB record
      const response = await loginUser(username, password);

      // ── On success, the response matches the backend contract: ──
      // { success: true, token: "jwt...", user_id: "uuid...", role: "member"|"admin" }

      // ── Store token and user data in localStorage ──
      saveAuthData(response);

      setSuccessMessage(`Welcome! Redirecting to your ${response.role} dashboard...`);

      // ── Redirect based on role returned by backend ──
      setTimeout(() => {
        if (response.role === "admin") {
          navigate("/admin/dashboard");
        } else {
          navigate("/user/dashboard");
        }
      }, 1000);

    } catch (error) {
      // ── Error response matches: { success: false, message: "..." } ──
      setErrorMessage(error.message || "Login failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form className="login-form" onSubmit={handleSubmit} noValidate>
      {/* ── Form Header ── */}
      <div className="login-form__header">
        <h1 className="login-form__title">WELCOME TO SMART GYM</h1>
        <p className="login-form__subtitle">
          Log in to access your personalized fitness dashboard.
        </p>
      </div>

      {/* ── Error Message ── */}
      {errorMessage && (
        <div className="login-form__alert login-form__alert--error" role="alert">
          <span className="login-form__alert-icon">⚠</span>
          {errorMessage}
        </div>
      )}

      {/* ── Success Message ── */}
      {successMessage && (
        <div className="login-form__alert login-form__alert--success" role="alert">
          <span className="login-form__alert-icon">✓</span>
          {successMessage}
        </div>
      )}

      {/* ── Username (Email) Field ──
           This field maps to: API payload "username" → DB column "users.email" (VARCHAR 255)
      */}
      <div className="login-form__field">
        <div className="login-form__input-wrapper">
          <Mail className="login-form__input-icon" size={20} />
          <input
            id="login-username"
            type="email"
            className="login-form__input"
            placeholder="Email Address"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="email"
            disabled={isLoading}
            aria-label="Email address"
          />
        </div>
      </div>

      {/* ── Password Field ──
           This field maps to: API payload "password" → Backend compares against DB "users.password_hash"
           NOTE: The raw password is NEVER stored. The backend hashes it with bcrypt.
      */}
      <div className="login-form__field">
        <div className="login-form__input-wrapper">
          <Lock className="login-form__input-icon" size={20} />
          <input
            id="login-password"
            type={showPassword ? "text" : "password"}
            className="login-form__input"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            disabled={isLoading}
            aria-label="Password"
          />
          <button
            type="button"
            className="login-form__toggle-password"
            onClick={() => setShowPassword(!showPassword)}
            tabIndex={-1}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
      </div>

      {/* ── Submit Button ── */}
      <button
        id="login-submit-btn"
        type="submit"
        className="login-form__submit"
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="login-form__spinner" size={20} />
            AUTHENTICATING...
          </>
        ) : (
          "LOGIN"
        )}
      </button>

      {/* ── Footer Links ── */}
      <div className="login-form__links">
        <button
          type="button"
          className="login-form__link login-form__link--btn"
          onClick={onSwitchToRegister}
        >
          Create Account
        </button>
        <a href="/help" className="login-form__link">
          Need Help?
        </a>
      </div>
    </form>
  );
}
