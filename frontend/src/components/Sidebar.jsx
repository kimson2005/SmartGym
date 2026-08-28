import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, Users, Dumbbell, Calendar, Wrench, GraduationCap, UserCircle, LogOut } from "lucide-react";
import { clearAuthData } from "../services/authService";
import "./Sidebar.css";

const Sidebar = () => {
  const navigate = useNavigate();

  const navItems = [
    { path: "/", icon: <LayoutDashboard size={20} />, label: "Tổng quan" },
    { path: "/users", icon: <Users size={20} />, label: "Người dùng" },
    { path: "/equipments", icon: <Dumbbell size={20} />, label: "Thiết bị" },
    { path: "/bookings", icon: <Calendar size={20} />, label: "Đặt lịch" },
    { path: "/trainers", icon: <GraduationCap size={20} />, label: "Huấn luyện viên" },
    { path: "/maintenance", icon: <Wrench size={20} />, label: "Bảo trì AI" },
  ];

  /**
   * Handle logout:
   * 1. Clear all auth data from localStorage (token, user_id, role)
   * 2. Redirect to /login
   */
  const handleLogout = () => {
    clearAuthData();
    navigate("/login");
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <Dumbbell className="logo-icon" size={28} />
        <span className="logo-text">SMART GYM</span>
      </div>

      <nav className="sidebar-nav">
        <ul>
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink 
                to={item.path} 
                className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}
              >
                {item.icon}
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-footer">
        <div className="admin-profile">
          <UserCircle size={36} color="var(--text-secondary)" />
          <div className="admin-info">
            <p className="admin-name">Quản trị viên</p>
            <p className="admin-role">Quản lý hệ thống</p>
          </div>
        </div>
        <button className="logout-btn" onClick={handleLogout} title="Đăng xuất">
          <LogOut size={18} />
          <span>Đăng xuất</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
