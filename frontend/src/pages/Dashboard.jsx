import { useState, useEffect } from "react";
import { Users, Dumbbell, Calendar, AlertTriangle, GraduationCap } from "lucide-react";
import StatCard from "../components/StatCard";
import axiosClient from "../api/axiosClient";
import "./Dashboard.css";

const Dashboard = () => {
  const [stats, setStats] = useState({
    users: 0,
    equipments: 0,
    bookings: 0,
    maintenance: 0,
    trainers: 0,
  });
  const [recentBookings, setRecentBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [usersRes, equipRes, bookRes, trainersRes] = await Promise.all([
        axiosClient.get("/users/"),
        axiosClient.get("/equipments/"),
        axiosClient.get("/bookings/?limit=10"),
        axiosClient.get("/trainers/"),
      ]);

      const equipments = equipRes.data;
      const maintenanceCount = equipments.filter((e) => e.status === "Maintenance").length;

      setStats({
        users: usersRes.data.length,
        equipments: equipments.length,
        bookings: bookRes.data.length,
        maintenance: maintenanceCount,
        trainers: trainersRes.data.length,
      });

      setRecentBookings(bookRes.data);
    } catch (error) {
      console.error("Failed to fetch dashboard data", error);
      alert("Lỗi khi tải dữ liệu Dashboard!");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "Confirmed":
        return <span className="badge success">Confirmed</span>;
      case "Completed":
        return <span className="badge info">Completed</span>;
      case "Cancelled":
        return <span className="badge danger">Cancelled</span>;
      default:
        return <span className="badge">{status}</span>;
    }
  };

  if (loading) return <div className="loading">Đang tải dữ liệu...</div>;

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1 className="page-title">Tổng quan Hệ thống</h1>
      </div>

      <div className="stats-grid">
        <StatCard icon={<Users />} title="Tổng người dùng" value={stats.users} />
        <StatCard icon={<Dumbbell />} title="Thiết bị" value={stats.equipments} color="var(--success)" />
        <StatCard icon={<Calendar />} title="Lịch đặt" value={stats.bookings} color="var(--info)" />
        <StatCard icon={<GraduationCap />} title="Huấn luyện viên" value={stats.trainers} color="var(--warning)" />
        <StatCard icon={<AlertTriangle />} title="Cần bảo trì" value={stats.maintenance} color="var(--danger)" />
      </div>

      <div className="recent-bookings-section">
        <h2>Lịch đặt Gần đây</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Mã đặt</th>
                <th>Người dùng</th>
                <th>Thiết bị</th>
                <th>Bắt đầu</th>
                <th>Kết thúc</th>
                <th>Trạng thái</th>
              </tr>
            </thead>
            <tbody>
              {recentBookings.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: "center" }}>Không có lịch đặt nào gần đây.</td>
                </tr>
              ) : (
                recentBookings.map((booking) => (
                  <tr key={booking.booking_id}>
                    <td>#{booking.booking_id}</td>
                    <td>{booking.user_id}</td>
                    <td>{booking.equipment_id}</td>
                    <td>{new Date(booking.start_time).toLocaleString("vi-VN")}</td>
                    <td>{new Date(booking.end_time).toLocaleString("vi-VN")}</td>
                    <td>{getStatusBadge(booking.status)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
