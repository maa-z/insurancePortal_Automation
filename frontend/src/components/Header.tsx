import React from 'react';
import { NavLink } from 'react-router-dom';

export const Header: React.FC = () => {
  return (
    <nav className="global-nav">
      <div className="global-nav-container">
        <div className="global-nav-brand">
          <span className="brand-dot" />
          <span className="brand-name">PriorAuth AI Platform</span>
        </div>
        <div className="global-nav-links">
          <NavLink
            to="/agent"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            data-testid="nav-link-agent"
          >
            Agent Control Center
          </NavLink>
          <NavLink
            to="/portal"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            data-testid="nav-link-portal"
          >
            Portal Simulator
          </NavLink>
        </div>
      </div>
    </nav>
  );
};
