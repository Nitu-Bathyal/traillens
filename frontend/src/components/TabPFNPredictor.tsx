import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';
import type { ActivityPredictionRequest, ActivityPredictionResponse } from '../types';
import { predictActivity } from '../services/api';

export const TabPFNPredictor: React.FC = () => {
  const [params, setParams] = useState<ActivityPredictionRequest>({
    temperature_c: 21.0,
    humidity_pct: 55.0,
    cloud_cover_pct: 30.0,
    time_of_day: 'morning',
    day_of_week: 'weekend',
    available_minutes: 30,
    terrain: 'park',
    user_energy: 'moderate'
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<ActivityPredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await predictActivity(params);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-open">TabPFN / Tabular AI</span>
          </div>
          <h2 style={{ fontSize: '1.4rem', color: 'var(--forest-900)' }}>
            Outdoor Activity Predictor
          </h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
            Predicts the optimal screen-free nature activity and completion likelihood from ambient environmental features.
          </p>
        </div>
      </div>

      {/* Inputs Form */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        background: 'var(--forest-50)',
        padding: '20px',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-light)'
      }}>
        
        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--forest-900)', marginBottom: '6px' }}>
            Temperature: {params.temperature_c}°C
          </label>
          <input
            type="range"
            min="5"
            max="38"
            step="1"
            value={params.temperature_c}
            onChange={(e) => setParams({ ...params, temperature_c: parseFloat(e.target.value) })}
            style={{ width: '100%' }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--forest-900)', marginBottom: '6px' }}>
            Humidity: {params.humidity_pct}%
          </label>
          <input
            type="range"
            min="20"
            max="100"
            step="5"
            value={params.humidity_pct}
            onChange={(e) => setParams({ ...params, humidity_pct: parseFloat(e.target.value) })}
            style={{ width: '100%' }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--forest-900)', marginBottom: '6px' }}>
            Available Time (min)
          </label>
          <select
            value={params.available_minutes}
            onChange={(e) => setParams({ ...params, available_minutes: parseInt(e.target.value, 10) })}
            style={{ width: '100%' }}
          >
            <option value="15">15 Minutes</option>
            <option value="30">30 Minutes</option>
            <option value="45">45 Minutes</option>
            <option value="60">60 Minutes</option>
            <option value="90">90 Minutes</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--forest-900)', marginBottom: '6px' }}>
            Time of Day
          </label>
          <select
            value={params.time_of_day}
            onChange={(e) => setParams({ ...params, time_of_day: e.target.value })}
            style={{ width: '100%' }}
          >
            <option value="morning">Morning</option>
            <option value="afternoon">Afternoon</option>
            <option value="evening">Evening</option>
            <option value="twilight">Twilight</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--forest-900)', marginBottom: '6px' }}>
            Terrain Setting
          </label>
          <select
            value={params.terrain}
            onChange={(e) => setParams({ ...params, terrain: e.target.value })}
            style={{ width: '100%' }}
          >
            <option value="park">City Park / Lawn</option>
            <option value="forest_trail">Forest / Woodland Trail</option>
            <option value="coastal">Coastal / Riverbank</option>
            <option value="urban_green">Urban Greenway</option>
            <option value="backyard">Backyard Garden</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--forest-900)', marginBottom: '6px' }}>
            Energy Level
          </label>
          <select
            value={params.user_energy}
            onChange={(e) => setParams({ ...params, user_energy: e.target.value })}
            style={{ width: '100%' }}
          >
            <option value="gentle">Gentle / Still</option>
            <option value="moderate">Moderate</option>
            <option value="active">Active Walk</option>
          </select>
        </div>

      </div>

      <button
        onClick={handlePredict}
        disabled={loading}
        className="btn btn-outdoor"
        style={{ width: '100%' }}
      >
        <Sparkles size={18} className={loading ? 'animate-spin' : ''} />
        {loading ? 'Evaluating Tabular Prior...' : 'Predict Optimal Activity'}
      </button>

      {error && (
        <div style={{ color: '#991b1b', fontSize: '0.88rem', background: '#fee2e2', padding: '10px 14px', borderRadius: 'var(--radius-sm)' }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{
          background: '#ffffff',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-md)',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '14px',
          boxShadow: 'var(--shadow-sm)'
        }}>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
            <div>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-light)', textTransform: 'uppercase' }}>Recommended Nature Category</span>
              <h3 style={{ fontSize: '1.4rem', color: 'var(--forest-900)', margin: 0 }}>
                {result.recommended_activity}
              </h3>
            </div>
            
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-light)', textTransform: 'uppercase' }}>Completion Likelihood</span>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#166534' }}>
                {result.completion_likelihood_pct}%
              </div>
            </div>
          </div>

          <p style={{ fontSize: '0.92rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
            {result.rationale}
          </p>

          <div style={{
            background: 'var(--forest-50)',
            padding: '12px 16px',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.82rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px'
          }}>
            <div>
              <strong style={{ color: 'var(--forest-900)' }}>Model Engine: </strong>
              <span>{result.model_name}</span>
            </div>
            {result.evaluation_metrics?.cv_accuracy_mean && (
              <div>
                <strong style={{ color: 'var(--forest-900)' }}>Cross-Validation Benchmark: </strong>
                <span>
                  {Math.round(result.evaluation_metrics.cv_accuracy_mean * 100)}% accuracy (±{Math.round(result.evaluation_metrics.cv_accuracy_std * 100)}%) across 5 stratified folds
                </span>
              </div>
            )}
            <div style={{ color: 'var(--text-light)', fontStyle: 'italic', marginTop: '4px' }}>
              * {result.limitations}
            </div>
          </div>

        </div>
      )}

    </div>
  );
};
