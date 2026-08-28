/**
 * ============================================================================
 * LOGIN PAGE — Smart Gym Split-Screen Auth (Login + Register)
 * ============================================================================
 *
 * Full-page authentication layout with:
 *   - LEFT PANEL:  Hero athlete image with overlay branding
 *   - RIGHT PANEL: Animated form switcher (Login ↔ Register)
 *
 * ─── ANIMATION ARCHITECTURE ───
 *   Both LoginForm and RegisterForm live in the SAME right panel.
 *   A `isLoginView` boolean state controls which form is visible.
 *
 *   Transition flow:
 *     Click "Create Account" → Login slides left + fades out,
 *                               Register slides in from right + fades in
 *     Click "Back to Login"  → Register slides right + fades out,
 *                               Login slides in from left + fades in
 *
 *   CSS classes used:
 *     .form-slide--active    → Currently visible form (opacity 1, translateX 0)
 *     .form-slide--exit-left → Slides out to the left (Login leaving)
 *     .form-slide--enter-right → Slides in from the right (Register entering)
 *     .form-slide--exit-right → Slides out to the right (Register leaving)
 *     .form-slide--enter-left → Slides in from the left (Login entering)
 *
 * Responsive behavior:
 *   - Desktop (>968px): Side-by-side split-screen
 *   - Tablet (768-968px): Narrower image panel
 *   - Mobile (<768px): Stacked layout, image becomes compact header
 *
 * ============================================================================
 */

import LoginForm from "../../components/auth/LoginForm";
import RegisterForm from "../../components/auth/RegisterForm";
import "./LoginPage.css";

// Lucide icons for branding
import { Dumbbell, Menu, X } from "lucide-react";
import { useState, useCallback } from "react";

export default function LoginPage() {
  const [menuOpen, setMenuOpen] = useState(false);

  /**
   * ── View Toggle State ──
   * true  = Show LoginForm (default)
   * false = Show RegisterForm
   *
   * The `isAnimating` flag prevents rapid double-clicks from
   * breaking the animation mid-transition (400ms lock).
   */
  const [isLoginView, setIsLoginView] = useState(true);
  const [isAnimating, setIsAnimating] = useState(false);

  /**
   * Switch to Register form view.
   * Called by LoginForm's "Create Account" button via onSwitchToRegister prop.
   */
  const switchToRegister = useCallback(() => {
    if (isAnimating) return;
    setIsAnimating(true);
    setIsLoginView(false);
    setTimeout(() => setIsAnimating(false), 500);
  }, [isAnimating]);

  /**
   * Switch back to Login form view.
   * Called by RegisterForm's "Back to Login" button or after successful registration.
   */
  const switchToLogin = useCallback(() => {
    if (isAnimating) return;
    setIsAnimating(true);
    setIsLoginView(true);
    setTimeout(() => setIsAnimating(false), 500);
  }, [isAnimating]);

  return (
    <div className="login-page">
      {/* ── Top Navigation Bar ── */}
      <nav className="login-nav">
        <div className="login-nav__brand">
          <Dumbbell className="login-nav__icon" size={28} />
          <span className="login-nav__logo">SMART GYM</span>
        </div>
        <button
          className="login-nav__hamburger"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle navigation menu"
        >
          {menuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        {/* ── Mobile Menu Dropdown ── */}
        {menuOpen && (
          <div className="login-nav__dropdown">
            <a href="/" className="login-nav__dropdown-link">Home</a>
            <a href="/about" className="login-nav__dropdown-link">About</a>
            <a href="/pricing" className="login-nav__dropdown-link">Pricing</a>
            <a href="/help" className="login-nav__dropdown-link">Contact</a>
          </div>
        )}
      </nav>

      {/* ── Left Panel: Hero Image ── */}
      <div className="login-page__hero">
        {/* The athlete image is set as a CSS background-image for better control */}
        <div className="login-page__hero-overlay">
          <div className="login-page__hero-content">
            <div className="login-page__hero-badge">PREMIUM FITNESS</div>
            <h2 className="login-page__hero-tagline">
              PUSH YOUR
              <span className="login-page__hero-highlight"> LIMITS</span>
            </h2>
            <p className="login-page__hero-desc">
              Join thousands of members achieving their fitness goals with Smart Gym's
              AI-powered training programs.
            </p>
            <div className="login-page__hero-stats">
              <div className="login-page__stat">
                <span className="login-page__stat-number">1K+</span>
                <span className="login-page__stat-label">Members</span>
              </div>
              <div className="login-page__stat-divider"></div>
              <div className="login-page__stat">
                <span className="login-page__stat-number">100+</span>
                <span className="login-page__stat-label">Equipment</span>
              </div>
              <div className="login-page__stat-divider"></div>
              <div className="login-page__stat">
                <span className="login-page__stat-number">10+</span>
                <span className="login-page__stat-label">Trainers</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Right Panel: Animated Form Switcher ── */}
      <div className="login-page__form-panel">
        <div className="login-page__form-container">
          {/*
           * ── Animation Wrapper ──
           * Both forms are always in the DOM but positioned absolutely.
           * The active form gets .form-slide--active (visible),
           * the inactive form gets an exit class (hidden + off-screen).
           *
           * This approach avoids mount/unmount flicker and allows
           * CSS transitions to handle the animation smoothly.
           */}
          <div className="form-slide-wrapper">
            {/* ── Login Form ── */}
            <div
              className={`form-slide ${
                isLoginView ? "form-slide--active" : "form-slide--exit-left"
              }`}
            >
              <LoginForm onSwitchToRegister={switchToRegister} />
            </div>

            {/* ── Register Form ── */}
            <div
              className={`form-slide ${
                !isLoginView ? "form-slide--active" : "form-slide--exit-right"
              }`}
            >
              <RegisterForm onSwitchToLogin={switchToLogin} />
            </div>
          </div>
        </div>

        {/* ── Bottom Decorative Element ── */}
        <div className="login-page__footer">
          <p>© 2026 Smart Gym. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}
