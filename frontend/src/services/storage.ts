import type { Observation } from '../types';

const KEY_OBSERVATIONS = 'traillens_observations_v1';
const KEY_SYNC_QUEUE = 'traillens_sync_queue_v1';
const KEY_SESSION_ID = 'traillens_session_id_v1';

export function getSessionId(): string {
  let id = localStorage.getItem(KEY_SESSION_ID);
  if (!id) {
    id = 'explorer-' + Math.random().toString(36).substring(2, 9);
    localStorage.setItem(KEY_SESSION_ID, id);
  }
  return id;
}

export function getLocalObservations(): Observation[] {
  try {
    const raw = localStorage.getItem(KEY_OBSERVATIONS);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveLocalObservation(obs: Observation): void {
  const current = getLocalObservations();
  const index = current.findIndex(o => o.id === obs.id || (obs.client_id && o.client_id === obs.client_id));
  if (index >= 0) {
    current[index] = obs;
  } else {
    current.unshift(obs);
  }
  localStorage.setItem(KEY_OBSERVATIONS, JSON.stringify(current));
}

export function deleteLocalObservation(id: string): void {
  const current = getLocalObservations();
  const filtered = current.filter(o => o.id !== id && o.client_id !== id);
  localStorage.setItem(KEY_OBSERVATIONS, JSON.stringify(filtered));
}

export function getSyncQueue(): Observation[] {
  try {
    const raw = localStorage.getItem(KEY_SYNC_QUEUE);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function enqueueSync(obs: Observation): void {
  const queue = getSyncQueue();
  queue.push(obs);
  localStorage.setItem(KEY_SYNC_QUEUE, JSON.stringify(queue));
}

export function clearSyncQueue(): void {
  localStorage.removeItem(KEY_SYNC_QUEUE);
}
