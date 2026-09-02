import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, AlertTriangle } from 'lucide-react';

interface DisputeItem {
  id: string;
  amount: number;
  reason: string;
  status: 'pending' | 'reviewing';
  confidence: number;
  date: string;
}

const ReviewQueue: React.FC = () => {
  const navigate = useNavigate();
  const [queue, setQueue] = useState<DisputeItem[]>([]);

  useEffect(() => {
    // Mocking /api/v1/review-queue
    setTimeout(() => {
      setQueue([
        { id: 'DSP-8492', amount: 1250.00, reason: 'Fraudulent Transaction', status: 'pending', confidence: 92, date: '2026-09-02' },
        { id: 'DSP-8493', amount: 45.99, reason: 'Product Not Received', status: 'reviewing', confidence: 64, date: '2026-09-02' },
        { id: 'DSP-8494', amount: 899.50, reason: 'Unrecognized Charge', status: 'pending', confidence: 88, date: '2026-09-01' },
        { id: 'DSP-8495', amount: 12.00, reason: 'Duplicate Billing', status: 'pending', confidence: 45, date: '2026-09-01' },
      ]);
    }, 800);
  }, []);

  const getConfidenceBadge = (score: number) => {
    if (score >= 80) return <span className="badge badge-success">{score}% High</span>;
    if (score >= 50) return <span className="badge badge-warning">{score}% Med</span>;
    return <span className="badge badge-danger">{score}% Low</span>;
  };

  return (
    <div className="animate-slide-up">
      <header className="page-header">
        <h1 className="page-title text-gradient">Review Queue</h1>
        <p className="page-subtitle">Disputes requiring human attention</p>
      </header>

      <div className="glass-panel" style={{ padding: '24px' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Date</th>
              <th>Amount</th>
              <th>Reason</th>
              <th>AI Confidence</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {queue.map(item => (
              <tr key={item.id} onClick={() => navigate(`/dispute/${item.id}`)}>
                <td style={{ fontWeight: 600 }}>{item.id}</td>
                <td>{item.date}</td>
                <td>${item.amount.toFixed(2)}</td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {item.amount > 1000 && <AlertTriangle size={14} color="var(--warning)" />}
                    {item.reason}
                  </div>
                </td>
                <td>{getConfidenceBadge(item.confidence)}</td>
                <td>
                  <span className={`badge ${item.status === 'pending' ? 'badge-warning' : 'badge-success'}`}>
                    {item.status}
                  </span>
                </td>
                <td>
                  <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                    Review <ArrowRight size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {queue.length === 0 && (
          <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-secondary)' }}>
            Loading queue...
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewQueue;
