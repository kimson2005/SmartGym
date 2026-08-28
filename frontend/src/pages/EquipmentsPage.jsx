import { useState, useEffect } from "react";
import axiosClient from "../api/axiosClient";
import { Plus, X, Edit, Trash2 } from "lucide-react";
import "./EquipmentsPage.css";

const EquipmentsPage = () => {
  const [equipments, setEquipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentEditId, setCurrentEditId] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    category: "",
    status: "Available",
    total_used_hours: 0,
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchEquipments();
  }, []);

  const fetchEquipments = async () => {
    try {
      setLoading(true);
      const res = await axiosClient.get("/equipments/");
      setEquipments(res.data);
    } catch (error) {
      console.error("Failed to fetch equipments", error);
      alert("Lỗi khi tải danh sách thiết bị!");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const openAddModal = () => {
    setIsEditing(false);
    setCurrentEditId(null);
    setFormData({ name: "", category: "", status: "Available", total_used_hours: 0 });
    setShowModal(true);
  };

  const openEditModal = (equipment) => {
    setIsEditing(true);
    setCurrentEditId(equipment.equipment_id);
    setFormData({
      name: equipment.name,
      category: equipment.category,
      status: equipment.status,
      total_used_hours: equipment.total_used_hours || 0,
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bạn có chắc chắn muốn xóa thiết bị này không?")) {
      try {
        await axiosClient.delete(`/equipments/${id}`);
        alert("Xóa thành công!");
        fetchEquipments();
      } catch (error) {
        alert("Lỗi khi xóa thiết bị!");
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      if (isEditing) {
        await axiosClient.patch(`/equipments/${currentEditId}`, formData);
        alert("Cập nhật thành công!");
      } else {
        await axiosClient.post("/equipments/", formData);
        alert("Thêm thiết bị thành công!");
      }
      setShowModal(false);
      fetchEquipments();
    } catch (error) {
      console.error("Failed to save equipment", error);
      alert("Lỗi khi lưu thiết bị!");
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "Available": return <span className="badge success">Available</span>;
      case "In Use": return <span className="badge warning">In Use</span>;
      case "Maintenance": return <span className="badge danger">Maintenance</span>;
      default: return <span className="badge">{status}</span>;
    }
  };

  const getProgressBarColor = (ratio) => {
    if (ratio < 0.5) return "var(--success)";
    if (ratio < 0.8) return "var(--warning)";
    return "var(--danger)";
  };

  return (
    <div className="equipments-page">
      <div className="page-header">
        <h1 className="page-title">Quản lý Thiết bị</h1>
        <button className="btn btn-primary" onClick={openAddModal}>
          <Plus size={18} /> Thêm thiết bị
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
                <th>Tên</th>
                <th>Loại</th>
                <th>Trạng thái</th>
                <th>Sử dụng / Giới hạn</th>
                <th>Mức bảo trì</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {equipments.map((eq) => {
                const ratio = eq.total_used_hours / eq.maintenance_interval_hours;
                const percentage = Math.min(ratio * 100, 100);
                
                return (
                  <tr key={eq.equipment_id}>
                    <td>#{eq.equipment_id}</td>
                    <td style={{ fontWeight: 500 }}>{eq.name}</td>
                    <td>{eq.category}</td>
                    <td>{getStatusBadge(eq.status)}</td>
                    <td>
                      {eq.total_used_hours.toFixed(1)}h / {eq.maintenance_interval_hours}h
                    </td>
                    <td style={{ width: '200px' }}>
                      <div className="progress-bar-bg">
                        <div 
                          className="progress-bar-fill" 
                          style={{ 
                            width: `${percentage}%`,
                            backgroundColor: getProgressBarColor(ratio)
                          }}
                        ></div>
                      </div>
                    </td>
                    <td>
                      <div className="actions">
                        <button className="action-btn edit" onClick={() => openEditModal(eq)}>
                          <Edit size={16} />
                        </button>
                        <button className="action-btn delete" onClick={() => handleDelete(eq.equipment_id)}>
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>{isEditing ? "Sửa Thiết bị" : "Thêm Thiết bị Mới"}</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                <X size={24} />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Tên thiết bị</label>
                <input type="text" name="name" className="form-control" value={formData.name} onChange={handleInputChange} required />
              </div>
              <div className="form-group">
                <label>Loại thiết bị</label>
                <input type="text" name="category" className="form-control" value={formData.category} onChange={handleInputChange} required />
              </div>
              {isEditing && (
                <>
                  <div className="form-group">
                    <label>Trạng thái</label>
                    <select name="status" className="form-control" value={formData.status} onChange={handleInputChange}>
                      <option value="Available">Sẵn sàng</option>
                      <option value="In Use">Đang dùng</option>
                      <option value="Maintenance">Bảo trì</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Total Used Hours (Giờ đã dùng)</label>
                    <input type="number" step="0.1" min="0" name="total_used_hours" className="form-control" value={formData.total_used_hours} onChange={handleInputChange} />
                  </div>
                </>
              )}
              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '10px', justifyContent: 'center' }} disabled={submitting}>
                {submitting ? 'Đang lưu...' : 'Lưu thiết bị'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default EquipmentsPage;
