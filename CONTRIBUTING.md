# Contributing to TrailLens

Welcome to TrailLens! We are delighted you want to contribute to this Hacktoberfest 2026 open-source project.

## The Touch Grass Philosophy

Every contribution must honor the central project principle:

> **"See something. Understand it. Step away."**

We build technology that helps human beings look at the natural world with curiosity and then immediately **put their phones away**.

We do **not** accept:
- Infinite chat loops, chatbots, or conversational rabbit holes
- Gamification mechanics designed to maximize screen time (streaks, badges that require checking the phone, notification spam)
- Social feeds, leaderboards, or vanity metrics
- Secret proprietary API replacements disguised as open models

We enthusiastically welcome:
- High-quality sensory outdoor challenges (`backend/app/data/challenges_db.json`)
- Integrations with new open-weight models (PaliGemma, Gemma 2, Qwen2-VL, Moondream)
- Offline-first resilience enhancements and local edge inference improvements
- Accessibility, contrast, and outdoor sunlight readability improvements
- Unit and integration tests

---

## Development Setup

### Backend (Python 3.11+)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run tests:
   ```bash
   pytest backend/tests -v
   ```
4. Start backend dev server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend (Node 18+)

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Start Vite dev server:
   ```bash
   npm run dev
   ```
3. Build for production:
   ```bash
   npm run build
   ```

---

## Submitting Pull Requests

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/sensory-botany-challenge
   ```
2. Run test suites:
   ```bash
   pytest backend/tests
   npm run build --prefix frontend
   ```
3. Commit with concise, descriptive commit messages.
4. Open a Pull Request referencing the relevant Hacktoberfest issue!
