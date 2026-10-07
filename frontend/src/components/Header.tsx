import React from 'react';
import { Compass, Wifi, WifiOff, Sparkles } from 'lucide-react';

interface HeaderProps {
  isOnline: boolean;
  modelInfo?: string;
  isDemo?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ isOnline, modelInfo, isDemo }) => {
  return (
    <header style={{
      padding: '24px 0 16px',
      borderBottom: '1px solid var(--border-light)',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'var(--forest-800)',
            color: '#fff',
            width: '44px',
            height: '44px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(22, 54, 30, 0.25)'
          }}>
            <Compass size={26} strokeWidth={2.2} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.75rem', margin: 0, lineHeight: 1.1, color: 'var(--forest-900)' }}>
              TRAILLENS
            </h1>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', fontWeight: 500 }}>
              See something. Understand it. Step away.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          {isDemo && (
            <span className="badge badge-demo" title="Deterministic open taxonomy simulation">
              <Sparkles size={12} /> DEMO MODE
            </span>
          )}

          <span
            className={`badge ${isOnline ? 'badge-online' : 'badge-offline'}`}
            title={isOnline ? 'Connected to network' : 'Offline trail mode active'}
          >
            {isOnline ? <Wifi size={13} /> : <WifiOff size={13} />}
            {isOnline ? 'Online' : 'Offline Trail'}
          </span>
        </div>
      </div>

      {modelInfo && (
        <div style={{
          fontSize: '0.78rem',
          color: 'var(--text-light)',
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <span>Active Intelligence:</span>
          <strong style={{ color: 'var(--text-muted)' }}>{modelInfo}</strong>
        </div>
      )}
    </header>
  );
};
