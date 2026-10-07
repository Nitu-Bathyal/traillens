from app.config import settings
from app.ai.base import AIProvider
from app.ai.demo_provider import DemoAIProvider
from app.ai.open_model_provider import OpenModelProvider


def get_ai_provider() -> AIProvider:
    """
    Factory function returning the configured AI provider.
    Defaults to 'demo' for reliable, zero-config out-of-the-box operation,
    or 'open_model' / 'gemma' when open-weight models are enabled.
    """
    provider_type = settings.AI_PROVIDER.lower().strip()

    if provider_type in ["open_model", "gemma", "ollama", "huggingface"]:
        return OpenModelProvider(
            model_name=settings.OPEN_MODEL_NAME,
            vision_model_name=settings.VISION_MODEL_NAME,
            license_info=settings.OPEN_MODEL_LICENSE
        )
    return DemoAIProvider()
