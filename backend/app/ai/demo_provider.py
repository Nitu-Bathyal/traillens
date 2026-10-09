from typing import Optional
from PIL import Image
from app.ai.base import AIProvider
from app.models.observation import IdentificationResult
from app.ai.image_analyzer import analyze_image_heuristics, DEMO_WARNING_MESSAGE


class DemoAIProvider(AIProvider):
    """
    Deterministic offline heuristic provider.
    Runs 100% locally with zero external network connectivity.
    Performs genuine image feature analysis (color channels, horizon gradients,
    foliage density) and strictly refuses to fabricate species or inflated confidence scores.
    """

    @property
    def name(self) -> str:
        return "demo"

    @property
    def model_name(self) -> str:
        return "TrailLens Nature Heuristics Engine (Offline Demo Fallback)"

    @property
    def license(self) -> str:
        return "Apache 2.0 / Open Source"

    @property
    def is_offline(self) -> bool:
        return True

    async def identify(
        self,
        image: Image.Image,
        user_hint: Optional[str] = None
    ) -> IdentificationResult:
        result = analyze_image_heuristics(image, user_hint)
        result.model_used = self.model_name
        result.is_demo = True
        if not result.fallback_warning:
            result.fallback_warning = DEMO_WARNING_MESSAGE
        return result
