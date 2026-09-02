import React from 'react';
import { CheckCircle } from 'lucide-react';

export interface AuditEvent {
  id: string;
  timestamp: string;
  action: string;
  hash: string;
  verified: boolean;
}

interface AuditLedgerProps {
  events: AuditEvent[];
}

export const AuditLedger: React.FC<AuditLedgerProps> = ({ events }) => {
  return (
    <div className="glass-panel" style={{ marginTop: '32px' }}>
      <h3 style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)' }}>
        <CheckCircle size={20} color="var(--accent-cyan)" /> Cryptographic Audit Ledger
      </h3>
      
      <div style={{ position: 'relative', borderLeft: '2px solid rgba(255, 255, 255, 0.1)', marginLeft: '12px', paddingLeft: '24px' }}>
        {events.map((event) => (
          <div key={event.id} style={{ marginBottom: '32px', position: 'relative' }}>
            {/* Timeline dot */}
            <span style={{
              position: 'absolute',
              left: '-31px',
              top: '4px',
              display: 'flex',
              height: '12px',
              width: '12px',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: '50%',
              backgroundColor: 'var(--accent-cyan)',
              boxShadow: '0 0 0 4px var(--bg-surface)'
            }}></span>
            
            <div style={{ display: 'flex', flexDirection: 'column', marginBottom: '8px' }}>
              <h4 style={{ fontWeight: '500', color: 'var(--text-primary)', textTransform: 'uppercase', fontSize: '0.85rem', letterSpacing: '0.05em' }}>
                {event.action}
              </h4>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
                {new Date(event.timestamp).toLocaleString()}
              </span>
            </div>
            
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between', 
              background: 'rgba(0, 0, 0, 0.2)', 
              padding: '12px', 
              borderRadius: '8px', 
              border: '1px solid rgba(255, 255, 255, 0.05)',
              fontFamily: 'monospace',
              fontSize: '0.75rem',
              color: 'var(--text-secondary)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                <span style={{ color: 'var(--text-tertiary)', userSelect: 'none' }}>SHA256:</span>
                <span style={{ color: 'var(--text-primary)', opacity: 0.8 }}>{event.hash}</span>
              </div>
              
              {event.verified && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  marginLeft: '16px',
                  padding: '4px 8px',
                  background: 'rgba(16, 185, 129, 0.1)',
                  color: '#10b981',
                  borderRadius: '9999px',
                  border: '1px solid rgba(16, 185, 129, 0.2)'
                }} title="Hash Verified">
                  <CheckCircle size={14} style={{ marginRight: '4px' }} />
                  <span style={{ fontSize: '0.65rem', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Verified</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
