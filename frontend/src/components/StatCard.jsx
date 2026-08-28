import "./StatCard.css";

const StatCard = ({ icon, title, value, color = "var(--accent-gradient)" }) => {
  return (
    <div className="stat-card">
      <div 
        className="stat-icon-wrapper" 
        style={{ background: color.includes('gradient') ? color : `rgba(${color}, 0.15)`, color: color.includes('gradient') ? 'white' : color }}
      >
        {icon}
      </div>
      <div className="stat-content">
        <h3>{value}</h3>
        <p>{title}</p>
      </div>
    </div>
  );
};

export default StatCard;
