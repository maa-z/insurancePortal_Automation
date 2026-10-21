import React from 'react';

interface StatCardProps {
  label: string;
  value: number | string;
  sublabel?: string;
  variant?: 'neutral' | 'success' | 'warning' | 'danger' | 'info';
  icon?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  sublabel,
  variant = 'neutral',
  icon,
}) => {
  return (
    <div className={`stat-card stat-${variant}`}>
      <div className="stat-card-header">
        <span className="stat-label">{label}</span>
        {icon && <span className="stat-icon">{icon}</span>}
      </div>
      <div className="stat-value">{value}</div>
      {sublabel && <div className="stat-sublabel">{sublabel}</div>}
    </div>
  );
};
