/**
 * ============================================================================
 * APP ROUTER — Smart Gym Application
 * ============================================================================
 *
 * Security architecture:
 *   1. On EVERY app load, all previous auth data is cleared (token, user_id, role).
 *      This prevents session hijacking or stale token reuse.
 *   2. All protected routes require a valid auth session (isAuthenticated).
 *      If not authenticated → redirect to /login automatically.
 *   3. The /login route is the ONLY publicly accessible page.
 *
 * Routing:
 *   /login               →  LoginPage (public, no sidebar)
 *   /                    →  Dashboard (protected, with sidebar)
 *   /users               →  UsersPage (protected)
 *   /equipments          →  EquipmentsPage (protected)
 *   /bookings            →  BookingsPage (protected)
 *   /maintenance         →  MaintenancePage (protected)
 *   /admin/dashboard     →  Redirects to / (protected)
 *   /user/dashboard      →  Member dashboard (protected)
 *   *                    →  Catch-all → /login
 *
 * ============================================================================
 */

import { Routes, Route, useLocation, Navigate } from "react-router-dom";
import { useEffect, useRef } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import UsersPage from "./pages/UsersPage";
import EquipmentsPage from "./pages/EquipmentsPage";
import BookingsPage from "./pages/BookingsPage";
import MaintenancePage from "./pages/MaintenancePage";
import TrainersPage from "./pages/TrainersPage";
import LoginPage from "./pages/auth/LoginPage";
import { isAuthenticated, clearAuthData } from "./services/authService";
import "./App.css";

/**
 * ProtectedRoute — Wrapper that redirects to /login if user is not authenticated.
 * This ensures no one can access admin pages without going through login first.
 */
function ProtectedRoute({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function App() {
  const location = useLocation();
  const hasCleared = useRef(false);

  /**
   * ── Security: Clear previous sessions on app startup ──
   * This runs ONCE when the app first loads (fresh page load / refresh).
   * It ensures no stale tokens from previous sessions persist,
   * forcing the user to authenticate every time they open the app.
   *
   * The useRef flag prevents this from running on every route change
   * (which would log the user out immediately after login).
   */
  useEffect(() => {
    if (!hasCleared.current) {
      clearAuthData();
      hasCleared.current = true;
    }
  }, []);

  // ── Routes that should NOT show the sidebar (standalone pages) ──
  const noSidebarRoutes = ["/login", "/register", "/help", "/request-admin"];
  const showSidebar = !noSidebarRoutes.includes(location.pathname);

  return (
    <div className={showSidebar ? "app-container" : ""}>
      {showSidebar && <Sidebar />}
      <main className={showSidebar ? "main-content" : ""}>
        <Routes>
          {/* ── Public Route ── */}
          <Route path="/login" element={<LoginPage />} />

          {/* ── Protected Routes (require authentication) ── */}
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/users" element={<ProtectedRoute><UsersPage /></ProtectedRoute>} />
          <Route path="/equipments" element={<ProtectedRoute><EquipmentsPage /></ProtectedRoute>} />
          <Route path="/bookings" element={<ProtectedRoute><BookingsPage /></ProtectedRoute>} />
          <Route path="/maintenance" element={<ProtectedRoute><MaintenancePage /></ProtectedRoute>} />
          <Route path="/trainers" element={<ProtectedRoute><TrainersPage /></ProtectedRoute>} />

          {/* ── Post-Login Redirect Routes ── */}
          <Route path="/admin/dashboard" element={<ProtectedRoute><Navigate to="/" replace /></ProtectedRoute>} />
          <Route path="/user/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />

          {/* ── Catch-all: any unknown route → login ── */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
