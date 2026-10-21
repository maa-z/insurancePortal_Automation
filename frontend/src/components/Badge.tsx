import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'green' | 'yellow' | 'orange' | 'red' | 'blue' | 'gray' | 'purple';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'gray', className = '' }) => {
  return <span className={`status-badge badge-${variant} ${className}`}>{children}</span>;
};
