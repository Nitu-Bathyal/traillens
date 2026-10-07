from abc import ABC, abstractmethod
from typing import Optional
from PIL import Image
from app.models.observation import IdentificationResult


class AIProvider(ABC):
    """
    Abstract Base Class for TrailLens AI Providers.
    Designed so open-weight models (Gemma, PaliGemma, Qwen2-VL, etc.)
    can be plugged in without changing the core application logic.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'open_model', 'gemma_local', 'demo')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Specific model architecture and weights."""
        pass

    @property
    @abstractmethod
    def license(self) -> str:
        """Open license governing the model weights."""
        pass

    @property
    @abstractmethod
    def is_offline(self) -> bool:
        """Whether this provider operates locally without external network calls."""
        pass

    @abstractmethod
    async def identify(
        self,
        image: Image.Image,
        user_hint: Optional[str] = None
    ) -> IdentificationResult:
        """
        Analyze nature photo and return concise identification,
        micro-observations, and a zero-screen outdoor challenge.
        """
        pass
