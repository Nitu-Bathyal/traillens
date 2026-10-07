import json
import random
from pathlib import Path
from typing import List, Optional
from app.models.challenge import Challenge

CHALLENGES_FILE = Path(__file__).parent.parent / "data" / "challenges_db.json"


class ChallengeService:
    def __init__(self):
        self._challenges: List[Challenge] = []
        self._load_challenges()

    def _load_challenges(self):
        if CHALLENGES_FILE.exists():
            with open(CHALLENGES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._challenges = [Challenge(**item) for item in data]
        else:
            self._challenges = []

    def get_all(self) -> List[Challenge]:
        return self._challenges

    def get_random(self, category: Optional[str] = None) -> Challenge:
        if not self._challenges:
            return Challenge(
                id="default-observation",
                title="Mindful Nature Observation",
                category="mindfulness",
                duration_minutes=3,
                instruction="Find any living plant or tree. Observe it silently for 3 minutes without digital distraction.",
                screen_rule="Turn your phone face down or slip it into your pocket.",
                difficulty="easy",
                equipment_needed="None — eyes and stillness"
            )

        if category:
            filtered = [c for c in self._challenges if c.category.lower() == category.lower()]
            if filtered:
                return random.choice(filtered)

        return random.choice(self._challenges)

    def get_by_id(self, challenge_id: str) -> Optional[Challenge]:
        for c in self._challenges:
            if c.id == challenge_id:
                return c
        return None


challenge_service = ChallengeService()
