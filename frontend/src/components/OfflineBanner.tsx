import React from 'react';
import { CloudOff, RefreshCw } from 'lucide-react';

interface OfflineBannerProps {
  isOnline: boolean;
  pendingSyncCount: number;
  onSync: () => void;
  isSyncing: boolean;
}

export const OfflineBanner: React.FC<OfflineBannerProps> = ({
  isOnline,
  pendingSyncCount,
  onSync,
  isSyncing
}) => {
  if (isOnline && pendingSyncCount === 0) return null;

  return (
    <div style={{
      background: !isOnline ? '#fef2f2' : '#f0fdf4',
      border: `1px solid ${!isOnline ? '#fecaca' : '#bbf7d0'}`,
      borderRadius: 'var(--radius-md)',
      padding: '12px 16px',
      margin: '12px 0',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '12px',
      flexWrap: 'wrap'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <CloudOff size={18} color={!isOnline ? '#b91c1c' : '#15803d'} />
        <span style={{
          fontSize: '0.88rem',
          color: !isOnline ? '#991b1b' : '#166534',
          fontWeight: 500
        }}>
          {!isOnline
            ? 'Offline trail mode: observations are saved locally to your device.'
            : `${pendingSyncCount} observation(s) waiting to sync to the field database.`}
        </span>
      </div>

      {isOnline && pendingSyncCount > 0 && (
        <button
          onClick={onSync}
          disabled={isSyncing}
          className="btn btn-secondary"
          style={{ padding: '6px 14px', fontSize: '0.82rem' }}
        >
          <RefreshCw size={14} className={isSyncing ? 'animate-spin' : ''} />
          {isSyncing ? 'Syncing...' : 'Sync Now'}
        </button>
      )}
    </div>
  );
};
