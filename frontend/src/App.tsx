import React, { useEffect, useState } from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, ListChecks, ShieldAlert, Settings, AlertTriangle, CheckCircle2 } from 'lucide-react';
import Dashboard from './components/Dashboard';
import ReviewQueue from './components/ReviewQueue';
import DisputeDetail from './components/DisputeDetail';

interface SystemHealth {
  database: string;
  razorpay: {
    credentials_configured: boolean;
    api_connectivity: string;
    live_actions_enabled: boolean;
    evidence_upload_enabled: boolean;
  };
  llm: {
    provider: string;
    configured: boolean;
  };
  carrier: {
    provider: string;
    configured: boolean;
  };
}

const App: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        // Assume API is mounted on /api/v1 if proxied, or fully qualified. We'll try relative first.
        const res = await fetch('http://localhost:8000/api/v1/health/integrations');
        if (res.ok) {
          const data = await res.json();
          setHealth(data);
        }
      } catch (e) {
        console.error("Failed to fetch integrations health", e);
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

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
      <main className="main-content flex flex-col">
        {/* Environment Banner */}
        {health && (
          <div className={`p-3 text-sm font-semibold flex items-center justify-between shadow-sm z-10 ${
            health.razorpay.live_actions_enabled 
              ? 'bg-red-600 text-white' 
              : 'bg-amber-100 text-amber-900 border-b border-amber-200'
          }`}>
            <div className="flex items-center gap-2">
              <AlertTriangle size={16} />
              {health.razorpay.live_actions_enabled 
                ? "DANGER: REAL LIVE FINANCIAL ACTIONS ENABLED. ACTIONS ARE IRREVERSIBLE."
                : "STAGING / SAFE MODE: Financial actions (Contest/Accept) will be skipped."
              }
            </div>
            <div className="flex items-center gap-4 text-xs font-normal opacity-90">
              <span className="flex items-center gap-1">
                API: {health.razorpay.api_connectivity === 'connected' ? <CheckCircle2 size={12} /> : 'Disconnected'}
              </span>
              <span className="flex items-center gap-1">
                Upload: {health.razorpay.evidence_upload_enabled ? 'ON' : 'OFF'}
              </span>
              <span className="flex items-center gap-1">
                LLM ({health.llm.provider}): {health.llm.configured ? 'ON' : 'OFF'}
              </span>
            </div>
          </div>
        )}

        <div className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/queue" element={<ReviewQueue />} />
            <Route path="/dispute/:id" element={<DisputeDetail />} />
          </Routes>
        </div>
      </main>
    </div>
  );
};

export default App;
