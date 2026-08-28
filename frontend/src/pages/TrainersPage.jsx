import { useState, useEffect } from "react";
import axiosClient from "../api/axiosClient";
import { Plus, X, Edit, Trash2, Star, Filter, Check, XCircle, Clock, UserCheck } from "lucide-react";
import "./TrainersPage.css";

const TrainersPage = () => {
  /* ── State ── */
  const [trainers, setTrainers] = useState([]);
  const [trainerBookings, setTrainerBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("profiles"); // profiles | bookings
  const [bookingFilter, setBookingFilter] = useState("All");

  /* ── Modal State ── */
  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentEditId, setCurrentEditId] = useState(null);
  const [formData, setFormData] = useState({
    user_id: "",
    specialty: "",
    experience_years: 0,
    hourly_rate: 0,
    bio: "",
  });
  const [submitting, setSubmitting] = useState(false);

  /* ── Fetch Data ── */
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [trainersRes, bookingsRes] = await Promise.all([
        axiosClient.get("/trainers/"),
        axiosClient.get("/trainers/bookings/"),
      ]);
      setTrainers(trainersRes.data);
      setTrainerBookings(bookingsRes.data);
    } catch (error) {
      console.error("Failed to fetch trainer data", error);
      alert("Lỗi khi tải dữ liệu Huấn luyện viên!");
    } finally {
      setLoading(false);
    }
  };

  /* ── Input Handlers ── */
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  /* ── Modal Handlers ── */
  const openAddModal = () => {
    setIsEditing(false);
    setCurrentEditId(null);
    setFormData({ user_id: "", specialty: "", experience_years: 0, hourly_rate: 0, bio: "" });
    setShowModal(true);
  };

  const openEditModal = (trainer) => {
    setIsEditing(true);
    setCurrentEditId(trainer.trainer_id);
    setFormData({
      user_id: trainer.user_id,
      specialty: trainer.specialty,
      experience_years: trainer.experience_years,
      hourly_rate: trainer.hourly_rate,
      bio: trainer.bio || "",
    });
    setShowModal(true);
  };

  /* ── CRUD Actions ── */
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      if (isEditing) {
        await axiosClient.put(`/trainers/${currentEditId}`, {
          specialty: formData.specialty,
          experience_years: Number(formData.experience_years),
          hourly_rate: Number(formData.hourly_rate),
          bio: formData.bio || null,
        });
        alert("Cập nhật hồ sơ HLV thành công!");
      } else {
        await axiosClient.post("/trainers/", {
          ...formData,
          user_id: Number(formData.user_id),
          experience_years: Number(formData.experience_years),
          hourly_rate: Number(formData.hourly_rate),
          bio: formData.bio || null,
        });
        alert("Tạo hồ sơ HLV thành công!");
      }
      setShowModal(false);
      fetchData();
    } catch (error) {
      console.error("Failed to save trainer", error);
      alert(error.response?.data?.detail || "Lỗi khi lưu hồ sơ HLV!");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bạn có chắc chắn muốn xóa hồ sơ HLV này không?")) {
      try {
        await axiosClient.delete(`/trainers/${id}`);
        alert("Xóa hồ sơ HLV thành công!");
        fetchData();
      } catch (error) {
        alert(error.response?.data?.detail || "Lỗi khi xóa hồ sơ HLV!");
      }
    }
  };

  /* ── Booking Actions ── */
  const handleConfirmBooking = async (bookingId, trainerId) => {
    try {
      // Find the trainer to get user_id
      const trainer = trainers.find((t) => t.trainer_id === trainerId);
      if (!trainer) {
        alert("Không tìm thấy thông tin trainer!");
        return;
      }
      await axiosClient.patch(`/trainers/bookings/${bookingId}/confirm?trainer_user_id=${trainer.user_id}`);
      alert("Xác nhận booking thành công!");
      fetchData();
    } catch (error) {
      alert(error.response?.data?.detail || "Lỗi khi xác nhận booking!");
    }
  };

  const handleRejectBooking = async (bookingId, trainerId) => {
    if (window.confirm("Bạn có chắc muốn từ chối booking này?")) {
      try {
        const trainer = trainers.find((t) => t.trainer_id === trainerId);
        if (!trainer) return;
        await axiosClient.patch(`/trainers/bookings/${bookingId}/reject?trainer_user_id=${trainer.user_id}`);
        alert("Đã từ chối booking!");
        fetchData();
      } catch (error) {
        alert(error.response?.data?.detail || "Lỗi khi từ chối booking!");
      }
    }
  };

  const handleCompleteBooking = async (bookingId) => {
    try {
      await axiosClient.patch(`/trainers/bookings/${bookingId}/complete`);
      alert("Đã đánh dấu hoàn thành!");
      fetchData();
    } catch (error) {
      alert(error.response?.data?.detail || "Lỗi khi hoàn thành booking!");
    }
  };

  const handleCancelBooking = async (bookingId) => {
    if (window.confirm("Bạn có chắc muốn hủy booking này?")) {
      try {
        await axiosClient.patch(`/trainers/bookings/${bookingId}/cancel`);
        alert("Đã hủy booking!");
        fetchData();
      } catch (error) {
        alert(error.response?.data?.detail || "Lỗi khi hủy booking!");
      }
    }
  };

  /* ── Badge Helpers ── */
  const getStatusBadge = (status) => {
    switch (status) {
      case "Pending": return <span className="badge warning">Pending</span>;
      case "Confirmed": return <span className="badge success">Confirmed</span>;
      case "Completed": return <span className="badge info">Completed</span>;
      case "Rejected": return <span className="badge danger">Rejected</span>;
      case "Cancelled": return <span className="badge danger">Cancelled</span>;
      default: return <span className="badge">{status}</span>;
    }
  };

  /* ── Filtered Bookings ── */
  const filteredBookings = bookingFilter === "All"
    ? trainerBookings
    : trainerBookings.filter((b) => b.status === bookingFilter);

  /* ── Render ── */
  if (loading) return <div className="loading">Đang tải dữ liệu...</div>;

  return (
    <div className="trainers-page">
      <div className="page-header">
        <h1 className="page-title">Quản lý Huấn luyện viên</h1>
        {activeTab === "profiles" && (
          <button className="btn btn-primary" onClick={openAddModal}>
            <Plus size={18} /> Thêm HLV
          </button>
        )}
      </div>

      {/* ── Tab Navigation ── */}
      <div className="tab-nav">
        <button
          className={`tab-btn ${activeTab === "profiles" ? "active" : ""}`}
          onClick={() => setActiveTab("profiles")}
        >
          <UserCheck size={18} /> Hồ sơ HLV
        </button>
        <button
          className={`tab-btn ${activeTab === "bookings" ? "active" : ""}`}
          onClick={() => setActiveTab("bookings")}
        >
          <Clock size={18} /> Lịch đặt HLV
          {trainerBookings.filter((b) => b.status === "Pending").length > 0 && (
            <span className="tab-badge">
              {trainerBookings.filter((b) => b.status === "Pending").length}
            </span>
          )}
        </button>
      </div>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* TAB 1: TRAINER PROFILES                                         */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      {activeTab === "profiles" && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Mã</th>
                <th>Người dùng</th>
                <th>Chuyên môn</th>
                <th>Kinh nghiệm</th>
                <th>Giá/giờ</th>
                <th>Giới thiệu</th>
                <th>Ngày tạo</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {trainers.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: "center" }}>
                    Chưa có huấn luyện viên nào. Nhấn "Thêm HLV" để bắt đầu.
                  </td>
                </tr>
              ) : (
                trainers.map((trainer) => (
                  <tr key={trainer.trainer_id}>
                    <td>#{trainer.trainer_id}</td>
                    <td>User #{trainer.user_id}</td>
                    <td>
                      <span className="specialty-tag">{trainer.specialty}</span>
                    </td>
                    <td>{trainer.experience_years} năm</td>
                    <td className="rate-cell">
                      {Number(trainer.hourly_rate).toLocaleString("vi-VN")}đ/h
                    </td>
                    <td className="bio-cell">
                      {trainer.bio
                        ? trainer.bio.length > 50
                          ? trainer.bio.substring(0, 50) + "..."
                          : trainer.bio
                        : "—"}
                    </td>
                    <td>{new Date(trainer.created_at).toLocaleDateString("vi-VN")}</td>
                    <td>
                      <div className="actions">
                        <button className="action-btn edit" onClick={() => openEditModal(trainer)} title="Sửa">
                          <Edit size={16} />
                        </button>
                        <button className="action-btn delete" onClick={() => handleDelete(trainer.trainer_id)} title="Xóa">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* TAB 2: TRAINER BOOKINGS                                         */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      {activeTab === "bookings" && (
        <>
          <div className="booking-filter-bar">
            <Filter size={18} color="var(--text-secondary)" />
            <select
              className="filter-select"
              value={bookingFilter}
              onChange={(e) => setBookingFilter(e.target.value)}
            >
              <option value="All">Tất cả</option>
              <option value="Pending">Chờ duyệt</option>
              <option value="Confirmed">Đã xác nhận</option>
              <option value="Completed">Hoàn thành</option>
              <option value="Rejected">Từ chối</option>
              <option value="Cancelled">Đã hủy</option>
            </select>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Mã đặt</th>
                  <th>Hội viên</th>
                  <th>HLV</th>
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
                    <td colSpan="8" style={{ textAlign: "center" }}>
                      Không có lịch đặt nào.
                    </td>
                  </tr>
                ) : (
                  filteredBookings.map((booking) => (
                    <tr key={booking.booking_id}>
                      <td>#{booking.booking_id}</td>
                      <td>User #{booking.member_id}</td>
                      <td>Trainer #{booking.trainer_id}</td>
                      <td>{new Date(booking.start_time).toLocaleString("vi-VN")}</td>
                      <td>{new Date(booking.end_time).toLocaleString("vi-VN")}</td>
                      <td>{getStatusBadge(booking.status)}</td>
                      <td>{new Date(booking.created_at).toLocaleDateString("vi-VN")}</td>
                      <td>
                        <div className="actions booking-actions">
                          {booking.status === "Pending" && (
                            <>
                              <button
                                className="action-btn confirm"
                                onClick={() => handleConfirmBooking(booking.booking_id, booking.trainer_id)}
                                title="Xác nhận"
                              >
                                <Check size={16} />
                              </button>
                              <button
                                className="action-btn reject"
                                onClick={() => handleRejectBooking(booking.booking_id, booking.trainer_id)}
                                title="Từ chối"
                              >
                                <XCircle size={16} />
                              </button>
                            </>
                          )}
                          {booking.status === "Confirmed" && (
                            <>
                              <button
                                className="action-btn complete"
                                onClick={() => handleCompleteBooking(booking.booking_id)}
                                title="Hoàn thành"
                              >
                                <Star size={16} />
                              </button>
                              <button
                                className="action-btn cancel"
                                onClick={() => handleCancelBooking(booking.booking_id)}
                                title="Hủy"
                              >
                                <XCircle size={16} />
                              </button>
                            </>
                          )}
                          {(booking.status === "Completed" || booking.status === "Rejected" || booking.status === "Cancelled") && (
                            <span style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>—</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* ADD / EDIT TRAINER MODAL                                        */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>{isEditing ? "Sửa Hồ sơ HLV" : "Thêm HLV Mới"}</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                <X size={24} />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              {!isEditing && (
                <div className="form-group">
                  <label>Mã người dùng (user phải có vai trò "trainer")</label>
                  <input
                    type="number"
                    name="user_id"
                    className="form-control"
                    value={formData.user_id}
                    onChange={handleInputChange}
                    required
                    min="1"
                  />
                </div>
              )}
              <div className="form-group">
                <label>Chuyên môn</label>
                <input
                  type="text"
                  name="specialty"
                  className="form-control"
                  value={formData.specialty}
                  onChange={handleInputChange}
                  required
                  placeholder="VD: Yoga, Gym, Cardio, Boxing..."
                />
              </div>
              <div className="form-group">
                <label>Kinh nghiệm (năm)</label>
                <input
                  type="number"
                  name="experience_years"
                  className="form-control"
                  value={formData.experience_years}
                  onChange={handleInputChange}
                  min="0"
                />
              </div>
              <div className="form-group">
                <label>Giá theo giờ (VND/giờ)</label>
                <input
                  type="number"
                  name="hourly_rate"
                  className="form-control"
                  value={formData.hourly_rate}
                  onChange={handleInputChange}
                  min="0"
                  step="1000"
                />
              </div>
              <div className="form-group">
                <label>Giới thiệu</label>
                <textarea
                  name="bio"
                  className="form-control"
                  value={formData.bio}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="Giới thiệu ngắn về huấn luyện viên..."
                />
              </div>
              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: "100%", marginTop: "10px", justifyContent: "center" }}
                disabled={submitting}
              >
                {submitting ? "Đang lưu..." : isEditing ? "Cập nhật HLV" : "Tạo HLV"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrainersPage;
