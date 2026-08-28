import { useState, useEffect } from "react";
import axiosClient from "../api/axiosClient";
import { Plus, X } from "lucide-react";
import "./UsersPage.css";

const UsersPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
    role: "member",
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await axiosClient.get("/users/");
      setUsers(res.data);
    } catch (error) {
      console.error("Failed to fetch users", error);
      alert("Lỗi khi tải danh sách người dùng!");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await axiosClient.post("/users/", { ...formData, is_active: true, physical_info: null });
      alert("Tạo người dùng thành công!");
      setShowModal(false);
      setFormData({ full_name: "", email: "", password: "", role: "member" });
      fetchUsers();
    } catch (error) {
      console.error("Failed to create user", error);
      alert(error.response?.data?.detail || "Lỗi khi tạo người dùng!");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="users-page">
      <div className="page-header">
        <h1 className="page-title">Quản lý Người dùng</h1>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          <Plus size={18} /> Thêm người dùng
        </button>
      </div>

      <div className="table-container">
        {loading ? (
          <div className="loading">Đang tải...</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Mã</th>
                <th>Họ và tên</th>
                <th>Email</th>
                <th>Vai trò</th>
                <th>Trạng thái</th>
                <th>Ngày tạo</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.user_id}>
                  <td>#{user.user_id}</td>
                  <td style={{ fontWeight: 500 }}>{user.full_name}</td>
                  <td>{user.email}</td>
                  <td>
                    <span className={`badge ${user.role === 'admin' ? 'admin' : user.role === 'trainer' ? 'warning' : 'info'}`}>
                      {user.role}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${user.is_active ? 'success' : 'danger'}`}>
                      {user.is_active ? 'Hoạt động' : 'Ngưng'}
                    </span>
                  </td>
                  <td>{new Date(user.created_at).toLocaleDateString("vi-VN")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Thêm Người dùng Mới</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                <X size={24} />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Họ và tên</label>
                <input type="text" name="full_name" className="form-control" value={formData.full_name} onChange={handleInputChange} required />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" name="email" className="form-control" value={formData.email} onChange={handleInputChange} required />
              </div>
              <div className="form-group">
                <label>Mật khẩu</label>
                <input type="password" name="password" className="form-control" value={formData.password} onChange={handleInputChange} required minLength={6} />
              </div>
              <div className="form-group">
                <label>Vai trò</label>
                <select name="role" className="form-control" value={formData.role} onChange={handleInputChange}>
                  <option value="member">Thành viên</option>
                  <option value="trainer">Huấn luyện viên</option>
                  <option value="admin">Quản trị viên</option>
                </select>
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '10px', justifyContent: 'center' }} disabled={submitting}>
                {submitting ? 'Đang tạo...' : 'Tạo người dùng'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersPage;
