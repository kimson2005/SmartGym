/**
 * ============================================================================
 * REGISTER FORM COMPONENT — Smart Gym Account Creation
 * ============================================================================
 *
 * State-managed React component for the registration form.
 * Styled identically to LoginForm using the same BEM class prefix pattern.
 *
 * ─── FORM FIELDS → DATABASE MAPPING ───
 *   Form "Full Name"        →  API payload "full_name"       →  DB column "users.full_name"
 *   Form "Email Address"    →  API payload "email"           →  DB column "users.email" (UNIQUE)
 *   Form "Password"         →  API payload "password"        →  Backend hashes → "users.password_hash"
 *   Form "Confirm Password" →  Frontend validation only      →  NOT sent to API
 *
 * ─── API ENDPOINT ───
 *   POST /api/v1/users/
 *   Payload:  { "full_name": "...", "email": "...", "password": "..." }
 *   Success:  { "user_id": 3, "full_name": "...", "email": "...", ... }
 *   Error:    HTTP 400/409 with error message
 *
 * ============================================================================
 */

import { useState } from "react";
import { registerUser } from "../../services/authService";
import "./RegisterForm.css";

// Lucide icons — same icon library used in LoginForm for consistency
import { User, Mail, Lock, Eye, EyeOff, Loader2, ArrowLeft } from "lucide-react";

/**
 * @param {Object} props
 * @param {Function} props.onSwitchToLogin - Callback to trigger the slide animation
 *                                           back to the Login form view
 */
export default function RegisterForm({ onSwitchToLogin }) {
  // ── Form State ──
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(false);

  // ── UI State ──
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  /**
   * Client-side validation before sending to the API.
   * Returns an error message string, or empty string if valid.
   */
  const validateForm = () => {
    if (!fullName.trim() || !email.trim() || !password.trim() || !confirmPassword.trim()) {
      return "Please fill in all fields.";
    }
    // Basic email format check
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return "Please enter a valid email address.";
    }
    if (password.length < 6) {
      return "Password must be at least 6 characters.";
    }
    if (password !== confirmPassword) {
      return "Passwords do not match.";
    }
    if (!agreeTerms) {
      return "You must agree to the Terms & Conditions.";
    }
    return "";
  };

  /**
   * Handle registration form submission.
   * Sends POST /api/v1/users/ with { full_name, email, password }
   * On success, auto-slides back to Login form after 1.5 seconds.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    // ── Validate ──
    const validationError = validateForm();
    if (validationError) {
      setErrorMessage(validationError);
      return;
    }

    setIsLoading(true);

    try {
      // ── Call auth service (mock or real) ──
      // Payload: { full_name, email, password }
      // "confirm_password" is NOT sent — it's frontend-only validation
      await registerUser(fullName, email, password);

      setSuccessMessage("Account created successfully! Redirecting to login...");

      // ── Auto-slide back to Login after 1.5 seconds ──
      setTimeout(() => {
        onSwitchToLogin();
      }, 1500);

    } catch (error) {
      setErrorMessage(error.message || "Registration failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form className="register-form" onSubmit={handleSubmit} noValidate>
      {/* ── Back to Login Button ── */}
      <button
        type="button"
        className="register-form__back"
        onClick={onSwitchToLogin}
      >
        <ArrowLeft size={18} />
        <span>Back to Login</span>
      </button>

      {/* ── Form Header ── */}
      <div className="register-form__header">
        <h1 className="register-form__title">CREATE ACCOUNT</h1>
        <p className="register-form__subtitle">
          Join Smart Gym and start your fitness journey today.
        </p>
      </div>

      {/* ── Error Message ── */}
      {errorMessage && (
        <div className="register-form__alert register-form__alert--error" role="alert">
          <span className="register-form__alert-icon">⚠</span>
          {errorMessage}
        </div>
      )}

      {/* ── Success Message ── */}
      {successMessage && (
        <div className="register-form__alert register-form__alert--success" role="alert">
          <span className="register-form__alert-icon">✓</span>
          {successMessage}
        </div>
      )}

      {/* ── Full Name Field ──
           Maps to: API payload "full_name" → DB column "users.full_name"
      */}
      <div className="register-form__field">
        <div className="register-form__input-wrapper">
          <User className="register-form__input-icon" size={20} />
          <input
            id="register-fullname"
            type="text"
            className="register-form__input"
            placeholder="Full Name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            autoComplete="name"
            disabled={isLoading}
            aria-label="Full name"
          />
        </div>
      </div>

      {/* ── Email Field ──
           Maps to: API payload "email" → DB column "users.email" (VARCHAR 255, UNIQUE)
      */}
      <div className="register-form__field">
        <div className="register-form__input-wrapper">
          <Mail className="register-form__input-icon" size={20} />
          <input
            id="register-email"
            type="email"
            className="register-form__input"
            placeholder="Email Address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            disabled={isLoading}
            aria-label="Email address"
          />
        </div>
      </div>

      {/* ── Password Field ──
           Maps to: API payload "password" → Backend hashes → DB "users.password_hash"
      */}
      <div className="register-form__field">
        <div className="register-form__input-wrapper">
          <Lock className="register-form__input-icon" size={20} />
          <input
            id="register-password"
            type={showPassword ? "text" : "password"}
            className="register-form__input"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            disabled={isLoading}
            aria-label="Password"
          />
          <button
            type="button"
            className="register-form__toggle-password"
            onClick={() => setShowPassword(!showPassword)}
            tabIndex={-1}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
      </div>

      {/* ── Confirm Password Field ──
           Frontend validation only — NOT sent to the API.
           Ensures the user typed their intended password correctly.
      */}
      <div className="register-form__field">
        <div className="register-form__input-wrapper">
          <Lock className="register-form__input-icon" size={20} />
          <input
            id="register-confirm-password"
            type={showConfirmPassword ? "text" : "password"}
            className="register-form__input"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            autoComplete="new-password"
            disabled={isLoading}
            aria-label="Confirm password"
          />
          <button
            type="button"
            className="register-form__toggle-password"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            tabIndex={-1}
            aria-label={showConfirmPassword ? "Hide password" : "Show password"}
          >
            {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
      </div>

      {/* ── Terms & Conditions Checkbox ── */}
      <div className="register-form__checkbox-group">
        <label className="register-form__checkbox-label" htmlFor="register-terms">
          <input
            id="register-terms"
            type="checkbox"
            className="register-form__checkbox"
            checked={agreeTerms}
            onChange={(e) => setAgreeTerms(e.target.checked)}
            disabled={isLoading}
          />
          <span>I agree to the <a href="#" className="register-form__terms-link">Terms & Conditions</a></span>
        </label>
      </div>

      {/* ── Submit Button ── */}
      <button
        id="register-submit-btn"
        type="submit"
        className="register-form__submit"
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="register-form__spinner" size={20} />
            CREATING ACCOUNT...
          </>
        ) : (
          "CREATE ACCOUNT"
        )}
      </button>

      {/* ── Footer Link ── */}
      <div className="register-form__links">
        <span className="register-form__link-text">Already have an account?</span>
        <button
          type="button"
          className="register-form__link"
          onClick={onSwitchToLogin}
        >
          Sign In
        </button>
      </div>
    </form>
  );
}
