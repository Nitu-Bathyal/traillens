import React, { useState, useEffect } from 'react';
import { RefreshCw, EyeOff, Clock } from 'lucide-react';
import type { OutdoorChallenge as ChallengeType } from '../types';
import { getRandomChallenge } from '../services/api';

interface OutdoorChallengeProps {
  onStartBreak: (instruction: string, duration?: number, title?: string) => void;
}

const CATEGORIES = [
  { id: '', label: 'All' },
  { id: 'textures', label: 'Textures' },
  { id: 'botany', label: 'Botany' },
  { id: 'acoustics', label: 'Birdsong & Sound' },
  { id: 'weather', label: 'Sky & Wind' },
  { id: 'insects', label: 'Insects' },
  { id: 'mindfulness', label: 'Mindfulness' }
];

export const OutdoorChallenge: React.FC<OutdoorChallengeProps> = ({ onStartBreak }) => {
  const [selectedCat, setSelectedCat] = useState<string>('');
  const [challenge, setChallenge] = useState<ChallengeType | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchChallenge = async (cat?: string) => {
    setLoading(true);
    try {
      const data = await getRandomChallenge(cat);
      setChallenge(data);
    } catch {
      // Local fallback
      setChallenge({
        id: 'fallback-observation',
        title: 'Tactile Tree Mapping',
        category: 'textures',
        duration_minutes: 3,
        instruction: 'Find three different trees nearby. Close your eyes and touch their bark with both hands. Compare the furrow depth and temperature.',
        screen_rule: 'Slide your phone deep into your pocket or pack.',
        difficulty: 'easy',
        equipment_needed: 'None — your hands and sense of touch'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChallenge(selectedCat);
  }, [selectedCat]);

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', color: 'var(--forest-900)' }}>Outdoor Challenge Engine</h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
            Sensory micro-missions designed to be performed with zero screen time.
          </p>
        </div>

        <button
          onClick={() => fetchChallenge(selectedCat)}
          disabled={loading}
          className="btn btn-secondary"
          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
        >
          <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
          Draw Another Challenge
        </button>
      </div>

      {/* Category Pills */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '4px' }}>
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCat(cat.id)}
            style={{
              padding: '6px 14px',
              fontSize: '0.82rem',
              fontWeight: 600,
              borderRadius: 'var(--radius-full)',
              border: selectedCat === cat.id ? '1px solid var(--forest-600)' : '1px solid var(--border-light)',
              background: selectedCat === cat.id ? 'var(--forest-800)' : '#ffffff',
              color: selectedCat === cat.id ? '#ffffff' : 'var(--text-muted)',
              cursor: 'pointer',
              whiteSpace: 'nowrap'
            }}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {challenge && (
        <div style={{
          background: 'var(--forest-50)',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-lg)',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="badge badge-open">{challenge.category}</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              <Clock size={14} />
              <span>{challenge.duration_minutes} min screen break</span>
            </div>
          </div>

          <h3 style={{ fontSize: '1.35rem', color: 'var(--forest-900)' }}>
            {challenge.title}
          </h3>

          <p style={{ fontSize: '1.02rem', lineHeight: '1.5', color: 'var(--text-main)' }}>
            {challenge.instruction}
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '12px',
            background: '#ffffff',
            padding: '12px 16px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-light)',
            fontSize: '0.85rem'
          }}>
            <div>
              <span style={{ color: 'var(--text-light)', display: 'block' }}>Screen Rule:</span>
              <strong style={{ color: 'var(--forest-800)' }}>{challenge.screen_rule}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-light)', display: 'block' }}>Gear Needed:</span>
              <strong style={{ color: 'var(--forest-800)' }}>{challenge.equipment_needed}</strong>
            </div>
          </div>

          {challenge.follow_up_prompt && (
            <p style={{ fontSize: '0.88rem', fontStyle: 'italic', color: 'var(--text-muted)' }}>
              Reflection to ponder outdoors: "{challenge.follow_up_prompt}"
            </p>
          )}

          <button
            onClick={() => onStartBreak(challenge.instruction, challenge.duration_minutes, challenge.title)}
            className="btn btn-outdoor"
            style={{ width: '100%', marginTop: '4px' }}
          >
            <EyeOff size={18} />
            Start Challenge (Lock Screen & Step Away)
          </button>

        </div>
      )}

    </div>
  );
};
