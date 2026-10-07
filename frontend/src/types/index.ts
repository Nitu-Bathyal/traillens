export interface IdentificationResult {
  identification: string;
  scientific_name?: string | null;
  category: string;
  confidence: number;
  confidence_level: string;
  summary: string;
  observations: string[];
  outdoor_challenge: string;
  safety_note: string;
  screen_break_message: string;
  model_used: string;
  is_demo: boolean;
}

export interface Observation {
  id: string;
  session_id: string;
  identification: IdentificationResult;
  latitude?: number | null;
  longitude?: number | null;
  user_notes?: string | null;
  image_thumbnail?: string | null;
  created_at: string;
  sync_status: 'synced' | 'pending';
  client_id?: string | null;
}

export interface OutdoorChallenge {
  id: string;
  title: string;
  category: string;
  duration_minutes: number;
  instruction: string;
  screen_rule: string;
  difficulty: string;
  equipment_needed: string;
  follow_up_prompt?: string | null;
}

export interface ActivityPredictionRequest {
  temperature_c: number;
  humidity_pct: number;
  cloud_cover_pct: number;
  time_of_day: string;
  day_of_week: string;
  available_minutes: number;
  terrain: string;
  user_energy: string;
}

export interface ActivityPredictionResponse {
  recommended_activity: string;
  category: string;
  confidence_score: number;
  completion_likelihood_pct: number;
  suggested_duration_min: number;
  rationale: string;
  features_used: Record<string, any>;
  model_name: string;
  evaluation_metrics: Record<string, any>;
  limitations: string;
}

export interface ProviderInfo {
  active_provider: string;
  model_name: string;
  license: string;
  is_offline: boolean;
  gemma_preference: {
    recommended_reasoning_model: string;
    recommended_vision_model: string;
    license: string;
    open_weights_rationale: string;
  };
}
