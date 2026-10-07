import React from 'react';
import { Bookmark, Trash2, Calendar, CheckCircle, Clock } from 'lucide-react';
import type { Observation } from '../types';

interface FieldJournalProps {
  observations: Observation[];
  onDelete: (id: string) => void;
}

export const FieldJournal: React.FC<FieldJournalProps> = ({ observations, onDelete }) => {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', color: 'var(--forest-900)' }}>Field Journal</h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
            Your outdoor encounters and observations recorded off-screen.
          </p>
        </div>
        <span className="badge badge-open">
          {observations.length} Specimen{observations.length === 1 ? '' : 's'}
        </span>
      </div>

      {observations.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '40px 20px',
          background: 'var(--forest-50)',
          borderRadius: 'var(--radius-md)',
          border: '1px dashed var(--border-light)'
        }}>
          <Bookmark size={36} color="var(--forest-400)" style={{ marginBottom: '12px' }} />
          <h3 style={{ fontSize: '1.1rem', marginBottom: '6px' }}>Your Journal is Empty</h3>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', maxWidth: '320px', margin: '0 auto' }}>
            Head outside, photograph a natural specimen, complete a micro-challenge, and record your observation here.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {observations.map((obs) => {
            const dateStr = new Date(obs.created_at).toLocaleDateString(undefined, {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            });

            return (
              <div
                key={obs.id || obs.client_id}
                style={{
                  background: '#ffffff',
                  border: '1px solid var(--border-light)',
                  borderRadius: 'var(--radius-md)',
                  padding: '16px',
                  display: 'flex',
                  gap: '16px',
                  alignItems: 'flex-start',
                  boxShadow: 'var(--shadow-sm)'
                }}
              >
                {obs.image_thumbnail && (
                  <img
                    src={obs.image_thumbnail}
                    alt={obs.identification.identification}
                    style={{
                      width: '80px',
                      height: '80px',
                      borderRadius: 'var(--radius-sm)',
                      objectFit: 'cover',
                      flexShrink: 0,
                      border: '1px solid var(--border-light)'
                    }}
                  />
                )}

                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <strong style={{ fontSize: '1.05rem', color: 'var(--forest-900)' }}>
                        {obs.identification.identification}
                      </strong>
                      <span className="badge badge-open" style={{ fontSize: '0.7rem' }}>
                        {obs.identification.category}
                      </span>
                    </div>

                    <button
                      onClick={() => onDelete(obs.id)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-light)',
                        cursor: 'pointer',
                        padding: '4px'
                      }}
                      title="Delete record"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>

                  {obs.identification.scientific_name && (
                    <span style={{ fontSize: '0.85rem', fontStyle: 'italic', color: 'var(--text-light)' }}>
                      {obs.identification.scientific_name}
                    </span>
                  )}

                  <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', margin: '4px 0' }}>
                    {obs.identification.summary}
                  </p>

                  {obs.user_notes && (
                    <div style={{
                      fontSize: '0.82rem',
                      background: 'var(--forest-50)',
                      padding: '6px 10px',
                      borderRadius: 'var(--radius-sm)',
                      color: 'var(--forest-800)'
                    }}>
                      <strong>Field Note:</strong> {obs.user_notes}
                    </div>
                  )}

                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    fontSize: '0.78rem',
                    color: 'var(--text-light)',
                    marginTop: '4px'
                  }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Calendar size={13} /> {dateStr}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      {obs.sync_status === 'synced' ? (
                        <>
                          <CheckCircle size={13} color="#166534" /> Synced
                        </>
                      ) : (
                        <>
                          <Clock size={13} color="#92400e" /> Saved Offline
                        </>
                      )}
                    </span>
                  </div>
                </div>

              </div>
            );
          })}
        </div>
      )}

    </div>
  );
};
