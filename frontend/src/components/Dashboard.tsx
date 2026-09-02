import React, { useEffect, useState } from 'react';
import { Activity, ShieldCheck, ShieldAlert, BarChart3 } from 'lucide-react';

interface SummaryData {
  total: number;
  contested: number;
  accepted: number;
  winRate: number;
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<SummaryData | null>(null);

  useEffect(() => {
    // In a real app, this would fetch from /api/v1/analytics/summary
    // Mocking for now as requested to ensure it renders without backend
    setTimeout(() => {
      setData({
        total: 1245,
        contested: 342,
        accepted: 903,
        winRate: 85.4
      });
    }, 1000);
  }, []);

  return (
    <div className="animate-slide-up">
      <header className="page-header">
        <h1 className="page-title text-gradient">Dashboard</h1>
        <p className="page-subtitle">Real-time dispute resolution analytics</p>
      </header>

      {data ? (
        <div className="grid grid-cols-4">
          <div className="glass-card stat-card">
            <div className="stat-header">
              <span>Total Disputes</span>
              <div className="stat-icon">
                <Activity size={20} />
              </div>
            </div>
            <div className="stat-value">{data.total}</div>
          </div>
          
          <div className="glass-card stat-card">
            <div className="stat-header">
              <span>Contested</span>
              <div className="stat-icon" style={{ color: 'var(--warning)' }}>
                <ShieldAlert size={20} />
              </div>
            </div>
            <div className="stat-value">{data.contested}</div>
          </div>

          <div className="glass-card stat-card">
            <div className="stat-header">
              <span>Accepted</span>
              <div className="stat-icon" style={{ color: 'var(--success)' }}>
                <ShieldCheck size={20} />
              </div>
            </div>
            <div className="stat-value">{data.accepted}</div>
          </div>

          <div className="glass-card stat-card">
            <div className="stat-header">
              <span>Win Rate</span>
              <div className="stat-icon" style={{ color: 'var(--accent-magenta)' }}>
                <BarChart3 size={20} />
              </div>
            </div>
            <div className="stat-value">{data.winRate}%</div>
          </div>
        </div>
      ) : (
        <div className="glass-panel p-8 flex justify-center items-center h-64">
          <div className="text-secondary" style={{ animation: 'pulse-neon 2s infinite' }}>Loading analytics...</div>
        </div>
      )}
      
      {/* Chart Placeholder */}
      <div className="glass-panel" style={{ marginTop: '32px', padding: '24px', height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
         <div style={{ textAlign: 'center' }}>
            <BarChart3 size={48} style={{ color: 'var(--glass-border)', margin: '0 auto 16px' }} />
            <h3 style={{ color: 'var(--text-secondary)' }}>Advanced Analytics Visualization</h3>
            <p style={{ color: 'var(--glass-border)', fontSize: '0.9rem' }}>Integration with charting library required</p>
         </div>
      </div>
    </div>
  );
};

export default Dashboard;
