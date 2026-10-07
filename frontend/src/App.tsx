import React, { useState, useEffect } from 'react';
import { Camera, Compass, Bookmark, Sliders } from 'lucide-react';
import { Header } from './components/Header';
import { OfflineBanner } from './components/OfflineBanner';
import { IdentificationCard } from './components/IdentificationCard';
import { OutdoorChallenge } from './components/OutdoorChallenge';
import { FieldJournal } from './components/FieldJournal';
import { TabPFNPredictor } from './components/TabPFNPredictor';
import { ScreenBreakModal } from './components/ScreenBreakModal';

import {
  getLocalObservations,
  saveLocalObservation,
  deleteLocalObservation,
  getSyncQueue,
  enqueueSync,
  clearSyncQueue,
  getSessionId
} from './services/storage';
import {
  fetchObservations,
  saveObservationRemote,
  deleteObservationRemote,
  syncBatchRemote,
  fetchProviderInfo
} from './services/api';
import type { Observation, IdentificationResult, ProviderInfo } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'identify' | 'challenge' | 'journal' | 'predict'>('identify');
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [syncQueue, setSyncQueue] = useState<Observation[]>([]);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [providerInfo, setProviderInfo] = useState<ProviderInfo | null>(null);

  // Screen break / Step away modal state
  const [isBreakOpen, setIsBreakOpen] = useState<boolean>(false);
  const [breakInstruction, setBreakInstruction] = useState<string>('Observe the specimen in its natural habitat.');
  const [breakDuration, setBreakDuration] = useState<number>(3);
  const [breakTitle, setBreakTitle] = useState<string>('Step Away Mode');

  // Network status listeners
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      triggerSync();
    };
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initial local load
    const locals = getLocalObservations();
    setObservations(locals);
    setSyncQueue(getSyncQueue());

    // Fetch provider info & remote observations if online
    loadData();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const loadData = async () => {
    try {
      const pInfo = await fetchProviderInfo();
      setProviderInfo(pInfo);
    } catch {
      // Offline or local
    }

    if (navigator.onLine) {
      try {
        const remotes = await fetchObservations();
        if (remotes && remotes.length > 0) {
          setObservations(remotes);
          remotes.forEach(r => saveLocalObservation(r));
        }
      } catch {
        // Fall back to local
      }
    }
  };

  const triggerSync = async () => {
    const queue = getSyncQueue();
    if (queue.length === 0) return;

    setIsSyncing(true);
    try {
      const payload = queue.map(q => ({
        session_id: q.session_id,
        identification: q.identification,
        latitude: q.latitude,
        longitude: q.longitude,
        user_notes: q.user_notes,
        image_thumbnail: q.image_thumbnail,
        offline_created_at: q.created_at,
        client_id: q.client_id
      }));

      await syncBatchRemote(payload);
      clearSyncQueue();
      setSyncQueue([]);
      // Reload observations
      await loadData();
    } catch {
      // Keep queue for next attempt
    } finally {
      setIsSyncing(false);
    }
  };

  const handleSaveObservation = async (result: IdentificationResult, photoThumb?: string) => {
    const clientId = 'obs-' + Math.random().toString(36).substring(2, 11);
    const newObs: Observation = {
      id: clientId,
      session_id: getSessionId(),
      identification: result,
      image_thumbnail: photoThumb,
      created_at: new Date().toISOString(),
      sync_status: isOnline ? 'synced' : 'pending',
      client_id: clientId
    };

    // Save locally immediately
    saveLocalObservation(newObs);
    setObservations(prev => [newObs, ...prev.filter(o => o.client_id !== clientId)]);

    if (isOnline) {
      try {
        const remote = await saveObservationRemote({
          session_id: newObs.session_id,
          identification: newObs.identification,
          image_thumbnail: newObs.image_thumbnail,
          client_id: newObs.client_id
        });
        // Update local with remote id
        saveLocalObservation(remote);
        setObservations(prev => [remote, ...prev.filter(o => o.client_id !== clientId)]);
      } catch {
        enqueueSync(newObs);
        setSyncQueue(getSyncQueue());
      }
    } else {
      enqueueSync(newObs);
      setSyncQueue(getSyncQueue());
    }
  };

  const handleDeleteObservation = async (id: string) => {
    deleteLocalObservation(id);
    setObservations(prev => prev.filter(o => o.id !== id && o.client_id !== id));
    if (isOnline) {
      try {
        await deleteObservationRemote(id);
      } catch {
        // Ignored
      }
    }
  };

  const handleStartBreak = (instruction: string, duration: number = 3, title?: string) => {
    setBreakInstruction(instruction);
    setBreakDuration(duration);
    if (title) setBreakTitle(title);
    setIsBreakOpen(true);
  };

  return (
    <>
      <Header
        isOnline={isOnline}
        modelInfo={providerInfo?.model_name}
        isDemo={providerInfo?.active_provider === 'demo'}
      />

      <OfflineBanner
        isOnline={isOnline}
        pendingSyncCount={syncQueue.length}
        onSync={triggerSync}
        isSyncing={isSyncing}
      />

      {/* Primary Action Tabs */}
      <nav className="nav-tabs">
        <button
          className={`tab-btn ${activeTab === 'identify' ? 'active' : ''}`}
          onClick={() => setActiveTab('identify')}
        >
          <Camera size={18} /> Identify
        </button>

        <button
          className={`tab-btn ${activeTab === 'challenge' ? 'active' : ''}`}
          onClick={() => setActiveTab('challenge')}
        >
          <Compass size={18} /> Outdoor Challenge
        </button>

        <button
          className={`tab-btn ${activeTab === 'journal' ? 'active' : ''}`}
          onClick={() => setActiveTab('journal')}
        >
          <Bookmark size={18} /> My Observations ({observations.length})
        </button>

        <button
          className={`tab-btn ${activeTab === 'predict' ? 'active' : ''}`}
          onClick={() => setActiveTab('predict')}
        >
          <Sliders size={18} /> Activity Predictor
        </button>
      </nav>

      {/* Main Tab Panels */}
      <main style={{ flex: 1 }}>
        {activeTab === 'identify' && (
          <IdentificationCard
            onSaveObservation={handleSaveObservation}
            onStartBreak={handleStartBreak}
          />
        )}

        {activeTab === 'challenge' && (
          <OutdoorChallenge
            onStartBreak={handleStartBreak}
          />
        )}

        {activeTab === 'journal' && (
          <FieldJournal
            observations={observations}
            onDelete={handleDeleteObservation}
          />
        )}

        {activeTab === 'predict' && (
          <TabPFNPredictor />
        )}
      </main>

      {/* Step Away Fullscreen Experience */}
      <ScreenBreakModal
        isOpen={isBreakOpen}
        durationMinutes={breakDuration}
        challengeTitle={breakTitle}
        challengeInstruction={breakInstruction}
        onComplete={() => setIsBreakOpen(false)}
        onCancel={() => setIsBreakOpen(false)}
      />

      <footer style={{
        marginTop: '32px',
        paddingTop: '20px',
        borderTop: '1px solid var(--border-light)',
        textAlign: 'center',
        fontSize: '0.82rem',
        color: 'var(--text-light)',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px'
      }}>
        <div>
          TrailLens &bull; Hacktoberfest 2026 Open-Source AI Challenge: "Touch Grass"
        </div>
        <div>
          Open-Weight Intelligence (Gemma 2 / PaliGemma) &bull; Zero Screen-Addiction &bull; Offline First
        </div>
      </footer>
    </>
  );
};

export default App;
