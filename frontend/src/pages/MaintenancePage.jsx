import { useState } from "react";
import axiosClient from "../api/axiosClient";
import { Wrench, ShieldAlert } from "lucide-react";
import "./MaintenancePage.css";

const MaintenancePage = () => {
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState(null);

  const runMaintenanceScan = async () => {
    try {
      setScanning(true);
      const res = await axiosClient.post("/equipments/analyze-maintenance/all");
      setResult(res.data);
    } catch (error) {
      console.error("Failed to run scan", error);
      alert("Lỗi khi chạy AI phân tích bảo trì!");
    } finally {
      setScanning(false);
    }
  };

  const getProgressBarColor = (ratio) => {
    if (ratio < 0.5) return "var(--success)";
    if (ratio < 0.8) return "var(--warning)";
    return "var(--danger)";
  };

  return (
    <div className="maintenance-page">
      <div className="page-header">
        <h1 className="page-title">Bảo trì Dự đoán AI</h1>
      </div>

      <div className="scan-section">
        <div className="scan-card">
          <ShieldAlert size={48} color="#FF3333" style={{ marginBottom: "20px" }} />
          <h2>Quét Bảo trì Tự động</h2>
          <p>Phân tích dữ liệu sử dụng thực tế của toàn bộ thiết bị để dự báo và tự động trigger bảo trì trước khi hỏng hóc xảy ra.</p>
          
          <button 
            className={`btn btn-primary scan-btn ${scanning ? 'scanning' : ''}`} 
            onClick={runMaintenanceScan}
            disabled={scanning}
          >
            <Wrench size={20} className={scanning ? 'spin' : ''} />
            {scanning ? "🤖 AI Đang phân tích..." : "🤖 Quét Bảo trì Toàn bộ"}
          </button>
        </div>
      </div>

      {result && (
        <div className="result-section fade-in">
          <div className="summary-cards">
            <div className="summary-card">
              <h4>Thiết bị đã quét</h4>
              <p className="big-num">{result.total_equipments_scanned || result.details?.length || 0}</p>
            </div>
            <div className="summary-card warning-card">
              <h4>Cảnh báo bảo trì</h4>
              <p className="big-num">{result.triggered_maintenance_count || result.details?.filter(d => d.status === 'Maintenance').length || 0}</p>
            </div>
          </div>

          <h3 className="details-title">Chi tiết phân tích</h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Mã TB</th>
                  <th>Tên</th>
                  <th>Sử dụng / Ngưỡng</th>
                  <th>Mức bảo trì</th>
                  <th>Trạng thái</th>
                  <th>Hành động AI</th>
                </tr>
              </thead>
              <tbody>
                {result.details && result.details.map((eq) => {
                  const ratio = eq.total_used_hours / eq.maintenance_interval_hours;
                  const percentage = Math.min(ratio * 100, 100);
                  
                  return (
                    <tr key={eq.equipment_id}>
                      <td>#{eq.equipment_id}</td>
                      <td style={{ fontWeight: 500 }}>{eq.equipment_name}</td>
                      <td>{eq.total_used_hours.toFixed(1)}h / {eq.maintenance_interval_hours}h</td>
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
                        <span className={`badge ${eq.status === 'Maintenance' ? 'danger' : (eq.status === 'In Use' ? 'warning' : 'success')}`}>
                          {eq.status}
                        </span>
                      </td>
                      <td>
                        <ul className="action-list">
                          {eq.actions.length > 0 ? (
                            eq.actions.map((act, idx) => <li key={idx}>- {act}</li>)
                          ) : (
                            <li style={{ color: 'var(--text-secondary)' }}>Không cần hành động</li>
                          )}
                        </ul>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default MaintenancePage;
