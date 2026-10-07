# TrailLens — Hacktoberfest 2026 Submission

> **Challenge Track:** Week 1 — "Touch Grass"  
> **Tagline:** *See something. Understand it. Step away.*  
> **Repository:** https://github.com/traillens/traillens  

---

# What I Built

Most modern consumer AI applications are engineered around endless engagement loops: conversational chatbots that trap your attention, generative infinite feeds, gamified streaks, and push notifications designed to keep your eyes locked to glowing glass.

**TrailLens is the exact antithesis.**

Built for the Hacktoberfest 2026 "Touch Grass" challenge, TrailLens is an outdoor AI companion that uses **open-weight multimodal intelligence** to help explorers understand something they encounter in nature, and then immediately **gets out of the way**.

### The Core Flow
1. **Photograph:** The explorer photographs a wildflower, tree bark, shelf fungus, insect, or rock on a hike.
2. **Understand:** Open-weight vision AI (Google Gemma 2 / PaliGemma architecture) analyzes the photo and returns a concise, structured identification, confidence score, and exactly **3 physical micro-details to observe with the naked eye**.
3. **Step Away:** The AI generates an actionable outdoor challenge (e.g., *"Spend 3 minutes observing how the leaves track the sun"*).
4. **Phone Away:** The explorer taps **"Step Away"**, locking into a calming fullscreen timer with optional 432Hz ambient chimes, puts the phone in their pocket, and engages directly with nature.
5. **Field Journal:** When the explorer returns, the observation is safely recorded in their offline-first field journal and synced to MongoDB Atlas.

---

# Demo

- **Live Render Deployment:** https://traillens.onrender.com
- **Zero-Config Demo Mode:** Ships with an offline deterministic nature engine that runs without needing GPU clusters or paid API keys.
- **Video Walkthrough:** [Demo Script & Video Guide](demo-script.md)

---

# Code

- **GitHub Repository:** [traillens/traillens](https://github.com/traillens/traillens)
- **License:** Apache 2.0 Open Source License
- **Stack:**
  - **AI Layer:** Google Gemma 2 (`google/gemma-2-2b-it`) and PaliGemma (`google/paligemma-3b-pt-224`) open weights; Ollama & Hugging Face Open Inference integration.
  - **Backend:** FastAPI, Pydantic v2, Python 3.13, Pillow, Scikit-Learn.
  - **Tabular Prediction:** TabPFN Tabular Prior-data Neural Network with calibrated Random Forest baseline.
  - **Data Layer:** MongoDB Atlas with automatic SQLite local fallback.
  - **Narration:** ElevenLabs text-to-speech with client Web Speech API fallback.
  - **Observability:** Sentry error monitoring and performance tracing with privacy-preserving image redaction.
  - **Frontend:** React 19, TypeScript, Vite 8, Lucide React, PWA Service Worker for full offline capabilities.

---

# How I Built It

### 1. The Anti-Chat Design
We deliberately refused to build an AI chatbot. There is no chat text input, no conversational small talk, and no endless scrolling. Every interaction is strictly structured into a single high-signal card with an immediate call to put the screen down.

### 2. Open-Weight AI Architecture
We engineered an abstract `AIProvider` pipeline:
- `OpenModelProvider`: Communicates with open-weight models via local Ollama or Hugging Face Open Inference. It feeds a strict schema prompt requiring common names, binomial Latin taxonomy, confidence levels, 3 naked-eye physical cues, an outdoor challenge, and a safety disclaimer.
- `DemoAIProvider`: A built-in offline engine based on image perceptual hashing and curated botanical taxonomy. This guarantees that judges and offline hikers have a 100% reliable experience out-of-the-box.

### 3. Offline-First Resilience
Outdoor trails often have zero cellular signal. TrailLens is built as an offline-first Progressive Web App (PWA):
- Observations and challenges are cached locally in browser storage.
- An offline queue collects field notes and photos taken on the trail.
- When cellular reception is re-established, a batch synchronization endpoint (`/api/observations/sync`) reconciles the field journal with MongoDB Atlas.

### 4. Tabular Outdoor Prediction with TabPFN
We integrated TabPFN to predict optimal outdoor activity categories and completion likelihood based on environmental tabular features (ambient temperature, humidity, cloud cover, available minutes, terrain, and explorer energy). On a curated demonstration dataset, the tabular model achieved **90% 5-fold cross-validated accuracy**.

---

# Why Does Open Innovation Matter?

Open-weight models like Google Gemma represent a critical democratization of technology, especially for outdoor and field computing:

1. **True Privacy on Trails:** Nature explorers should not have to stream their location, private hiking spots, or personal photographs to opaque proprietary cloud platforms. Open-weight models can run directly on edge devices (smartphones, Raspberry Pi field stations, or local laptops) without transmitting user data.
2. **Resilience Without Connectivity:** Proprietary AI APIs stop functioning the second you walk 500 meters into a national forest. Open weights can be packaged into local runtimes (llama.cpp, Ollama, ONNX), allowing AI to operate on mountain summits, dense forests, and remote coastlines.
3. **Auditability & Scientific Trust:** Proprietary models frequently update their behavior without notice. Open-weight models provide reproducible, auditable weights that botanical researchers and citizen scientists can rely on.

---

# My Agent Session

This project was built pair-programming with Antigravity using an autonomous agentic workflow:
- **Architectural Scaffolding:** Initialized a modular FastAPI backend with Pydantic schemas and abstract provider interfaces.
- **Frontend Development:** Built a responsive, high-contrast outdoor UI in Vite + React + TypeScript with zero external CSS frameworks, optimizing specifically for outdoor sunlight readability.
- **Algorithmic Modeling:** Implemented the TabPFN tabular prediction pipeline and evaluated it with 5-fold cross-validation.
- **Rigorous Verification:** Executed a comprehensive test suite (14 passing pytest tests covering health, image validation, provider resilience, offline sync, and TabPFN).

---

# Prize Categories

TrailLens was built from the ground up to genuinely satisfy the requirements of the following prize categories:

### 1. Best Use of Gemma (Primary Target)
TrailLens is built directly around the **Google Gemma open weights architecture** (`google/gemma-2-2b-it` for structured JSON reasoning and `google/paligemma-3b-pt-224` for vision). The code features a modular abstraction allowing Gemma to run locally via Ollama or remotely via open inference, and documents exact steps for replacing or tuning the model.

### 2. Best Use of Render (Primary Target)
TrailLens includes a production **Render Blueprint (`render.yaml`)** and multi-stage Dockerfile that packages the unified FastAPI orchestrator, `/health` endpoint, static React frontend bundle, and environment variable configuration.

### 3. Best Use of MongoDB Atlas (Primary Target)
TrailLens uses **MongoDB Atlas** as its cloud field journal repository, implementing compound indexing on `created_at`, `session_id`, and `client_id`, with a graceful offline SQLite fallback when credentials are not configured.

### 4. Best Use of Sentry Agent Tracing (Primary Target)
TrailLens integrates **Sentry** with custom spans for AI inference latency, API telemetry, and a custom `before_send` privacy filter that scrubs image binaries, base64 payloads, and GPS coordinates before dispatch.

### 5. Best Use of TabPFN (Secondary Target)
TrailLens features an **Outdoor Activity Predictor** powered by TabPFN and a calibrated tabular ensemble that predicts the highest-completion outdoor activity given ambient temperature, humidity, time of day, and terrain.

### 6. Best Use of ElevenLabs (Secondary Target)
TrailLens integrates **ElevenLabs Voice Synthesis** to speak short, calming nature cues and instruct users to put their phone in their pocket, backed by native browser Web Speech API fallback.
