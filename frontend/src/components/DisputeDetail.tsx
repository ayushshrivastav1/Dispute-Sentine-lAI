import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle, XCircle, FileText, User, CreditCard } from 'lucide-react';

const DisputeDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock fetch
    setTimeout(() => setLoading(false), 800);
  }, [id]);

  if (loading) {
    return (
      <div className="animate-slide-up flex justify-center items-center h-full">
        <h2 className="text-gradient" style={{ animation: 'pulse-neon 1.5s infinite' }}>Analyzing Evidence Dossier...</h2>
      </div>
    );
  }

  return (
    <div className="animate-slide-up">
      <button 
        className="btn btn-secondary" 
        style={{ marginBottom: '24px' }}
        onClick={() => navigate('/queue')}
      >
        <ArrowLeft size={16} /> Back to Queue
      </button>

      <header className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title text-gradient">Dispute {id}</h1>
          <p className="page-subtitle">Filed on Sept 02, 2026 • Fraudulent Transaction</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-danger">
            <XCircle size={18} /> Reject
          </button>
          <button className="btn btn-success">
            <CheckCircle size={18} /> Approve
          </button>
        </div>
      </header>

      <div className="grid grid-cols-3">
        <div className="glass-panel dossier-section" style={{ gridColumn: 'span 2', marginTop: 0 }}>
          <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={20} color="var(--accent-neon)" /> Evidence Dossier
          </h3>
          
          <div className="evidence-list">
            <div className="evidence-item">
              <CheckCircle size={18} color="var(--success)" />
              <div>
                <strong style={{ display: 'block' }}>AVS Match</strong>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Billing address matches card on file</span>
              </div>
            </div>
            <div className="evidence-item">
              <XCircle size={18} color="var(--danger)" />
              <div>
                <strong style={{ display: 'block' }}>IP Geolocation Mismatch</strong>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Transaction IP (Russia) differs from billing (USA)</span>
              </div>
            </div>
            <div className="evidence-item">
              <CheckCircle size={18} color="var(--warning)" />
              <div>
                <strong style={{ display: 'block' }}>Device Fingerprint</strong>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>New device used for this transaction</span>
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <User size={20} color="var(--accent-magenta)" /> Customer Info
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.9rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Name</span>
                <strong>John Doe</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Account Age</span>
                <strong>3 Years</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Prior Disputes</span>
                <strong>0</strong>
              </div>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '24px' }}>
             <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CreditCard size={20} color="var(--accent-neon)" /> Transaction Info
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.9rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Amount</span>
                <strong style={{ fontSize: '1.2rem', color: 'var(--danger)' }}>$1,250.00</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Card</span>
                <strong>Visa •••• 4242</strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="win-probability">
        <div className="win-prob-header">
          <span>AI Win Probability Analysis</span>
          <span className="text-gradient">92%</span>
        </div>
        <div className="progress-container">
          <div className="progress-bar" style={{ width: '92%' }}></div>
        </div>
        <p style={{ marginTop: '12px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          High confidence of winning dispute based on AVS match and prior account history, despite IP mismatch. Recommended Action: <strong>Contest</strong>.
        </p>
      </div>
    </div>
  );
};

export default DisputeDetail;
