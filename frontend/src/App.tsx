import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Header } from './components/Header';
import { AgentControlCenter } from './agent/AgentControlCenter';
import { InsurancePortal } from './portal/InsurancePortal';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="app-root">
        <Header />
        <Routes>
          <Route path="/" element={<Navigate to="/agent" replace />} />
          <Route path="/agent" element={<AgentControlCenter />} />
          <Route path="/portal" element={<InsurancePortal />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;
