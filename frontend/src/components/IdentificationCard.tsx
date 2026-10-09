import React, { useState, useRef } from 'react';
import {
  Camera,
  Upload,
  Sparkles,
  Volume2,
  VolumeX,
  Bookmark,
  EyeOff,
  AlertTriangle,
  Check,
  CheckCircle2
} from 'lucide-react';
import type { IdentificationResult } from '../types';
import { identifyImage } from '../services/api';
import { speakText, stopSpeaking } from '../services/speech';

interface IdentificationCardProps {
  onSaveObservation: (result: IdentificationResult, photoThumb?: string) => void;
  onStartBreak: (instruction: string, duration?: number) => void;
}

export const IdentificationCard: React.FC<IdentificationCardProps> = ({
  onSaveObservation,
  onStartBreak
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [userHint, setUserHint] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IdentificationResult | null>(null);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
      setSavedSuccess(false);
    }
  };

  const handleIdentify = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    try {
      const res = await identifyImage(selectedFile, userHint);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Unable to identify image. Please retry.');
    } finally {
      setLoading(false);
    }
  };

  const handleListen = () => {
    if (isSpeaking) {
      stopSpeaking();
      setIsSpeaking(false);
      return;
    }

    if (!result) return;
    const textToSpeak = `You are looking at ${result.identification}. Notice: ${result.observations[0] || 'the leaf structure'}. Now, put your phone away and observe in real life.`;
    setIsSpeaking(true);
    speakText(textToSpeak, () => setIsSpeaking(false));
  };

  const handleSave = () => {
    if (!result) return;
    onSaveObservation(result, previewUrl || undefined);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Photo Capture Section */}
      {!previewUrl ? (
        <div style={{
          border: '2px dashed var(--border-light)',
          borderRadius: 'var(--radius-lg)',
          padding: '36px 20px',
          textAlign: 'center',
          background: 'var(--forest-50)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '12px'
        }}>
          <div style={{
            background: 'var(--forest-100)',
            color: 'var(--forest-800)',
            padding: '16px',
            borderRadius: '50%'
          }}>
            <Camera size={32} />
          </div>

          <div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '4px' }}>Capture a Wild Specimen</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '360px' }}>
              Photograph a flower, tree bark, fungus, insect, or rock on your trail.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px', marginTop: '6px', flexWrap: 'wrap', justifyContent: 'center' }}>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="btn btn-outdoor"
            >
              <Upload size={18} /> Choose or Take Photo
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          <div style={{
            position: 'relative',
            borderRadius: 'var(--radius-md)',
            overflow: 'hidden',
            maxHeight: '280px',
            background: '#000',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center'
          }}>
            <img
              src={previewUrl}
              alt="Nature specimen"
              style={{ maxHeight: '280px', width: 'auto', objectFit: 'contain' }}
            />
            <button
              onClick={() => {
                setPreviewUrl(null);
                setSelectedFile(null);
                setResult(null);
                stopSpeaking();
              }}
              className="btn btn-secondary"
              style={{
                position: 'absolute',
                top: '12px',
                right: '12px',
                padding: '6px 12px',
                fontSize: '0.8rem',
                background: 'rgba(255, 255, 255, 0.9)'
              }}
            >
              Retake
            </button>
          </div>

          {!result && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <input
                type="text"
                placeholder="Optional context (e.g. growing near creek, shaded forest floor)"
                value={userHint}
                onChange={(e) => setUserHint(e.target.value)}
              />

              <button
                onClick={handleIdentify}
                disabled={loading}
                className="btn btn-outdoor"
                style={{ width: '100%' }}
              >
                {loading ? (
                  <>
                    <Sparkles size={18} className="animate-spin" />
                    Analyzing with Open-Weight Vision AI...
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    Analyze & Step Away
                  </>
                )}
              </button>
            </div>
          )}

        </div>
      )}

      {error && (
        <div style={{
          background: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: 'var(--radius-md)',
          padding: '12px 16px',
          color: '#991b1b',
          fontSize: '0.9rem',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Structured AI Analysis Result */}
      {result && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          borderTop: '1px solid var(--border-light)',
          paddingTop: '20px'
        }}>
          
          {/* Explicit Fallback / Demo Notice Banner */}
          {result.fallback_warning && (
            <div style={{
              background: '#fffbeb',
              border: '1px solid #fde68a',
              borderRadius: 'var(--radius-md)',
              padding: '14px 16px',
              color: '#92400e',
              fontSize: '0.88rem',
              lineHeight: '1.45',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '10px'
            }}>
              <AlertTriangle size={18} style={{ flexShrink: 0, marginTop: '2px', color: '#b45309' }} />
              <div>
                <strong style={{ display: 'block', color: '#78350f', marginBottom: '2px' }}>
                  Illustrative Demo / Fallback Mode
                </strong>
                <span>{result.fallback_warning}</span>
              </div>
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px', flexWrap: 'wrap' }}>
                <span className="badge badge-open">{result.category}</span>
                
                {/* Honest Confidence & Model Attribution Badges */}
                {result.is_confident && !result.is_demo ? (
                  <span className="badge badge-online">
                    {Math.round(result.confidence * 100)}% Confidence
                  </span>
                ) : (
                  <span className="badge badge-demo" style={{ background: '#fef3c7', color: '#92400e' }}>
                    {result.confidence_level === 'uncertain' || !result.is_confident
                      ? `Uncertain Confidence (${Math.round(result.confidence * 100)}%)`
                      : `Illustrative Heuristic (${Math.round(result.confidence * 100)}%)`}
                  </span>
                )}

                {result.is_demo ? (
                  <span className="badge badge-demo" style={{ border: '1px dashed #d97706' }}>
                    Simulation Heuristics
                  </span>
                ) : (
                  <span className="badge badge-online">
                    Live Model ({result.model_used})
                  </span>
                )}
              </div>

              <h2 style={{ fontSize: '1.6rem', color: 'var(--forest-900)', margin: 0 }}>
                {result.identification}
              </h2>
              {result.scientific_name && (
                <p style={{ fontStyle: 'italic', color: 'var(--text-light)', fontSize: '0.95rem' }}>
                  {result.scientific_name}
                </p>
              )}
            </div>

            <button
              onClick={handleListen}
              className={`btn ${isSpeaking ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '8px 14px', fontSize: '0.85rem' }}
            >
              {isSpeaking ? <VolumeX size={16} /> : <Volume2 size={16} />}
              {isSpeaking ? 'Stop Audio' : 'Listen'}
            </button>
          </div>

          {result.scene_description && (
            <div style={{
              fontSize: '0.84rem',
              color: 'var(--text-muted)',
              background: 'var(--forest-50)',
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-light)'
            }}>
              <strong>Visual Scene:</strong> {result.scene_description}
            </div>
          )}

          <p style={{ color: 'var(--text-muted)', fontSize: '0.98rem', lineHeight: '1.5' }}>
            {result.summary}
          </p>

          {/* Micro-Observations to Look For */}
          <div style={{
            background: 'var(--forest-50)',
            border: '1px solid var(--border-light)',
            borderRadius: 'var(--radius-md)',
            padding: '16px'
          }}>
            <h4 style={{ fontSize: '0.95rem', color: 'var(--forest-800)', marginBottom: '10px' }}>
              Look Closely in Real Life:
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {result.observations.map((obs, idx) => (
                <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.9rem', color: 'var(--text-main)' }}>
                  <Check size={16} color="var(--forest-600)" style={{ marginTop: '3px', flexShrink: 0 }} />
                  <span>{obs}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Actionable Outdoor Challenge */}
          <div style={{
            background: 'linear-gradient(135deg, #e4f3e8 0%, #d5edd9 100%)',
            border: '1px solid #b7dfbe',
            borderRadius: 'var(--radius-md)',
            padding: '16px 20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <EyeOff size={18} color="var(--forest-800)" />
              <strong style={{ color: 'var(--forest-900)', fontSize: '0.95rem' }}>Outdoor Challenge</strong>
            </div>
            <p style={{ fontSize: '0.92rem', color: 'var(--forest-900)', lineHeight: '1.45' }}>
              {result.outdoor_challenge}
            </p>
          </div>

          {/* Safety Warning */}
          {result.safety_note && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '0.8rem',
              color: '#854d0e',
              background: '#fefce8',
              border: '1px solid #fef08a',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 12px'
            }}>
              <AlertTriangle size={15} style={{ flexShrink: 0 }} />
              <span>{result.safety_note}</span>
            </div>
          )}

          {/* Step Away & Save Buttons */}
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '6px' }}>
            <button
              onClick={() => onStartBreak(result.outdoor_challenge, 3)}
              className="btn btn-outdoor"
              style={{ flex: 2, minWidth: '200px' }}
            >
              <EyeOff size={18} />
              Step Away / Put Phone Away
            </button>

            <button
              onClick={handleSave}
              disabled={savedSuccess}
              className="btn btn-secondary"
              style={{ flex: 1, minWidth: '150px' }}
            >
              {savedSuccess ? (
                <>
                  <CheckCircle2 size={18} color="#166534" />
                  Saved!
                </>
              ) : (
                <>
                  <Bookmark size={18} />
                  Save Observation
                </>
              )}
            </button>
          </div>

        </div>
      )}

    </div>
  );
};
