import type {
  IdentificationResult,
  Observation,
  OutdoorChallenge,
  ActivityPredictionRequest,
  ActivityPredictionResponse,
  ProviderInfo
} from '../types';
import { getSessionId } from './storage';

const API_BASE = import.meta.env.VITE_API_BASE_URL || (window.location.port === '5173' ? 'http://localhost:8000' : '');

export async function identifyImage(file: File, userHint?: string): Promise<IdentificationResult> {
  const formData = new FormData();
  formData.append('file', file);
  if (userHint) {
    formData.append('user_hint', userHint);
  }

  const res = await fetch(`${API_BASE}/api/identify`, {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Identification failed' }));
    throw new Error(errorData.detail || 'Identification failed');
  }

  return res.json();
}

export async function getRandomChallenge(category?: string): Promise<OutdoorChallenge> {
  const url = category ? `${API_BASE}/api/challenges/random?category=${encodeURIComponent(category)}` : `${API_BASE}/api/challenges/random`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('Failed to retrieve outdoor challenge');
  }
  return res.json();
}

export async function predictActivity(req: ActivityPredictionRequest): Promise<ActivityPredictionResponse> {
  const res = await fetch(`${API_BASE}/api/predict-activity`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req)
  });
  if (!res.ok) {
    throw new Error('Failed to predict outdoor activity');
  }
  return res.json();
}

export async function requestNarration(params: {
  identification: string;
  observationHint: string;
  challengeDuration?: number;
  customText?: string;
}): Promise<{ provider: string; audio_base64?: string; text: string; message: string }> {
  const res = await fetch(`${API_BASE}/api/narrate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      identification: params.identification,
      observation_hint: params.observationHint,
      challenge_duration: params.challengeDuration || 3,
      custom_text: params.customText
    })
  });
  if (!res.ok) {
    throw new Error('Narration service unavailable');
  }
  return res.json();
}

export async function fetchObservations(): Promise<Observation[]> {
  const sessionId = getSessionId();
  const res = await fetch(`${API_BASE}/api/observations?session_id=${encodeURIComponent(sessionId)}`);
  if (!res.ok) {
    throw new Error('Failed to load observations');
  }
  return res.json();
}

export async function saveObservationRemote(obs: any): Promise<Observation> {
  const res = await fetch(`${API_BASE}/api/observations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(obs)
  });
  if (!res.ok) {
    throw new Error('Failed to save observation to cloud');
  }
  return res.json();
}

export async function deleteObservationRemote(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/observations/${id}`, {
    method: 'DELETE'
  });
  if (!res.ok) {
    throw new Error('Failed to delete observation');
  }
}

export async function syncBatchRemote(items: any[]): Promise<any> {
  const res = await fetch(`${API_BASE}/api/observations/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ observations: items })
  });
  if (!res.ok) {
    throw new Error('Batch sync failed');
  }
  return res.json();
}

export async function fetchProviderInfo(): Promise<ProviderInfo> {
  const res = await fetch(`${API_BASE}/api/providers`);
  if (!res.ok) {
    throw new Error('Failed to fetch provider info');
  }
  return res.json();
}
