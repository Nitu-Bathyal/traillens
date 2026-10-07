import React, { useState, useEffect, useRef } from 'react';
import { EyeOff, CheckCircle, Volume2, VolumeX } from 'lucide-react';

interface ScreenBreakModalProps {
  isOpen: boolean;
  durationMinutes: number;
  challengeTitle?: string;
  challengeInstruction: string;
  onComplete: () => void;
  onCancel: () => void;
}

const MINDFUL_CUES = [
  "Look closely at the underside of the leaves or bark.",
  "Close your eyes for 30 seconds and listen for birds or wind.",
  "Notice the texture of the soil or rock beneath your feet.",
  "Look for any small creatures or pollinators nearby.",
  "Take three deep outdoor breaths."
];

export const ScreenBreakModal: React.FC<ScreenBreakModalProps> = ({
  isOpen,
  durationMinutes,
  challengeTitle,
  challengeInstruction,
  onComplete,
  onCancel
}) => {
  const [secondsRemaining, setSecondsRemaining] = useState(durationMinutes * 60);
  const [ambientAudio, setAmbientAudio] = useState(false);
  const [cueIndex, setCueIndex] = useState(0);
  const audioContextRef = useRef<AudioContext | null>(null);
  const oscillatorRef = useRef<OscillatorNode | null>(null);

  useEffect(() => {
    if (isOpen) {
      setSecondsRemaining(durationMinutes * 60);
      const timer = setInterval(() => {
        setSecondsRemaining(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      const cueTimer = setInterval(() => {
        setCueIndex(prev => (prev + 1) % MINDFUL_CUES.length);
      }, 35000);

      return () => {
        clearInterval(timer);
        clearInterval(cueTimer);
      };
    }
  }, [isOpen, durationMinutes]);

  // Clean up Web Audio
  useEffect(() => {
    return () => {
      stopAmbientTone();
    };
  }, []);

  const toggleAmbientTone = () => {
    if (ambientAudio) {
      stopAmbientTone();
      setAmbientAudio(false);
    } else {
      startAmbientTone();
      setAmbientAudio(true);
    }
  };

  const startAmbientTone = () => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      const ctx = new AudioCtx();
      audioContextRef.current = ctx;

      // Create gentle 432Hz ambient chime tone
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(432, ctx.currentTime);

      gain.gain.setValueAtTime(0.01, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.04, ctx.currentTime + 2);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      oscillatorRef.current = osc;
    } catch {
      // AudioContext policy fallback
    }
  };

  const stopAmbientTone = () => {
    try {
      if (oscillatorRef.current) {
        oscillatorRef.current.stop();
        oscillatorRef.current.disconnect();
        oscillatorRef.current = null;
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
    } catch {
      // Ignore
    }
  };

  if (!isOpen) return null;

  const mins = Math.floor(secondsRemaining / 60);
  const secs = secondsRemaining % 60;
  const progress = 1 - (secondsRemaining / (durationMinutes * 60));

  return (
    <div className="screen-break-modal">
      <div style={{ maxWidth: '480px', width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
        
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          padding: '12px 20px',
          borderRadius: 'var(--radius-full)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '0.9rem',
          letterSpacing: '0.04em',
          textTransform: 'uppercase'
        }}>
          <EyeOff size={18} />
          <span>Step Away Mode</span>
        </div>

        <h2 style={{ color: '#ffffff', fontSize: '1.8rem', textAlign: 'center', margin: 0 }}>
          {challengeTitle || 'Observe Without Screens'}
        </h2>

        {/* Circular Countdown Ring */}
        <div style={{
          position: 'relative',
          width: '180px',
          height: '180px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
            <circle
              cx="90"
              cy="90"
              r="76"
              stroke="rgba(255, 255, 255, 0.15)"
              strokeWidth="8"
              fill="transparent"
            />
            <circle
              cx="90"
              cy="90"
              r="76"
              stroke="#5cb071"
              strokeWidth="8"
              fill="transparent"
              strokeDasharray={477}
              strokeDashoffset={477 * (1 - progress)}
              strokeLinecap="round"
              style={{ transition: 'stroke-dashoffset 1s linear' }}
            />
          </svg>
          <div style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '2.4rem', fontWeight: 700, fontFamily: 'monospace' }}>
              {mins}:{secs < 10 ? `0${secs}` : secs}
            </span>
            <div style={{ fontSize: '0.78rem', color: '#a3c2a9', textTransform: 'uppercase' }}>
              {secondsRemaining === 0 ? 'Complete' : 'Remaining'}
            </div>
          </div>
        </div>

        <div style={{
          background: 'rgba(255, 255, 255, 0.08)',
          borderRadius: 'var(--radius-md)',
          padding: '16px 20px',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          fontSize: '1rem',
          lineHeight: '1.5'
        }}>
          <p style={{ fontWeight: 600, color: '#e4f3e8', marginBottom: '6px' }}>
            {challengeInstruction}
          </p>
          <p style={{ fontSize: '0.85rem', color: '#a3c2a9' }}>
            {MINDFUL_CUES[cueIndex]}
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={toggleAmbientTone}
            className="btn btn-outline"
            style={{
              borderColor: 'rgba(255, 255, 255, 0.25)',
              color: '#ffffff',
              fontSize: '0.85rem',
              padding: '8px 16px'
            }}
          >
            {ambientAudio ? <VolumeX size={16} /> : <Volume2 size={16} />}
            {ambientAudio ? 'Mute Tone' : 'Ambient 432Hz'}
          </button>
        </div>

        <div style={{ display: 'flex', gap: '12px', width: '100%', marginTop: '10px' }}>
          <button
            onClick={() => {
              stopAmbientTone();
              onComplete();
            }}
            className="btn btn-outdoor"
            style={{ flex: 1, padding: '14px' }}
          >
            <CheckCircle size={18} />
            I Observed This
          </button>
          
          <button
            onClick={() => {
              stopAmbientTone();
              onCancel();
            }}
            className="btn btn-outline"
            style={{ borderColor: 'rgba(255, 255, 255, 0.25)', color: '#ffffff' }}
          >
            Back
          </button>
        </div>

      </div>
    </div>
  );
};
