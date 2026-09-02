import React from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, ListChecks, ShieldAlert, Settings } from 'lucide-react';
import Dashboard from './components/Dashboard';
import ReviewQueue from './components/ReviewQueue';
import DisputeDetail from './components/DisputeDetail';

const App: React.FC = () => {
  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <ShieldAlert size={24} />
          </div>
          <span className="text-gradient">DisputeSentinel</span>
        </div>

        <nav className="nav-links">
          <NavLink 
            to="/" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            end
          >
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </NavLink>
          <NavLink 
            to="/queue" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <ListChecks size={20} />
            <span>Review Queue</span>
          </NavLink>
          <NavLink 
            to="/settings" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Settings size={20} />
            <span>Settings</span>
          </NavLink>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/queue" element={<ReviewQueue />} />
          <Route path="/dispute/:id" element={<DisputeDetail />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
