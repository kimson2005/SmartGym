import { useState, useEffect } from "react";
import axiosClient from "../api/axiosClient";
import { XCircle, Filter } from "lucide-react";
import "./BookingsPage.css";

const BookingsPage = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("All");

  useEffect(() => {
    fetchBookings();
  }, []);

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const res = await axiosClient.get("/bookings/");
      setBookings(res.data);
    } catch (error) {
      console.error("Failed to fetch bookings", error);
      alert("Lỗi khi tải danh sách đặt lịch!");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (id) => {
    if (window.confirm("Bạn có chắc chắn muốn hủy đặt lịch này không?")) {
      try {
        await axiosClient.patch(`/bookings/${id}/cancel`);
        alert("Hủy đặt lịch thành công!");
        fetchBookings();
      } catch (error) {
        console.error("Failed to cancel booking", error);
        alert("Lỗi khi hủy đặt lịch!");
      }
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "Confirmed": return <span className="badge success">Confirmed</span>;
      case "Completed": return <span className="badge info">Completed</span>;
      case "Cancelled": return <span className="badge danger">Cancelled</span>;
      default: return <span className="badge">{status}</span>;
    }
  };

  const filteredBookings = filter === "All" ? bookings : bookings.filter(b => b.status === filter);

  return (
    <div className="bookings-page">
      <div className="page-header">
        <h1 className="page-title">Quản lý Đặt lịch</h1>
        <div className="filter-container">
          <Filter size={18} color="var(--text-secondary)" />
          <select 
            className="filter-select" 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="All">Tất cả</option>
            <option value="Confirmed">Đã xác nhận</option>
            <option value="Completed">Hoàn thành</option>
            <option value="Cancelled">Đã hủy</option>
          </select>
        </div>
      </div>

      <div className="table-container">
        {loading ? (
          <div className="loading">Đang tải...</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Mã đặt</th>
                <th>Người dùng</th>
                <th>Thiết bị</th>
                <th>Bắt đầu</th>
                <th>Kết thúc</th>
                <th>Trạng thái</th>
                <th>Ngày tạo</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {filteredBookings.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: "center" }}>Không có lịch đặt nào.</td>
                </tr>
              ) : (
                filteredBookings.map((booking) => (
                  <tr key={booking.booking_id}>
                    <td>#{booking.booking_id}</td>
                    <td>User #{booking.user_id}</td>
                    <td>Eq #{booking.equipment_id}</td>
                    <td>{new Date(booking.start_time).toLocaleString("vi-VN")}</td>
                    <td>{new Date(booking.end_time).toLocaleString("vi-VN")}</td>
                    <td>{getStatusBadge(booking.status)}</td>
                    <td>{new Date(booking.created_at).toLocaleDateString("vi-VN")}</td>
                    <td>
                      {booking.status === "Confirmed" && (
                        <button 
                          className="btn btn-sm btn-danger cancel-btn"
                          onClick={() => handleCancel(booking.booking_id)}
                        >
                          <XCircle size={14} /> Hủy
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default BookingsPage;
