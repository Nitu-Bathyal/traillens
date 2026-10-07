from fastapi import APIRouter
from app.config import settings
from app.ai.factory import get_ai_provider

router = APIRouter(prefix="/api/providers", tags=["AI Providers & Open Innovation"])


@router.get("")
async def get_provider_info():
    """
    Returns full open-weight model provenance, active configuration,
    and instructions on replacing or running models locally.
    """
    provider = get_ai_provider()
    return {
        "active_provider": provider.name,
        "model_name": provider.model_name,
        "license": provider.license,
        "is_offline": provider.is_offline,
        "gemma_preference": {
            "recommended_reasoning_model": "google/gemma-2-2b-it",
            "recommended_vision_model": "google/paligemma-3b-pt-224",
            "license": "Gemma Open Weights Terms of Use",
            "open_weights_rationale": "Open weights ensure reproducible, private on-device or edge deployment without proprietary API vendor lock-in."
        },
        "substitution_guide": {
            "how_to_substitute": "Set AI_PROVIDER='open_model' and OPEN_MODEL_NAME or VISION_MODEL_NAME in .env or environment variables.",
            "supported_runtimes": [
                "Local Ollama (e.g. ollama run gemma2 / minicpm-v)",
                "Hugging Face Open Inference Endpoints",
                "Self-hosted vLLM or llama.cpp OpenAI-compatible server",
                "Deterministic Offline Demo Engine (zero config)"
            ]
        },
        "privacy_commitment": {
            "camera_images": "Processed in memory only; never retained on server without explicit observation saving.",
            "gps_coordinates": "Optional; coarse/redacted by default; never transmitted to telemetry.",
            "telemetry": "Errors sanitized via Sentry; raw images scrubbed."
        }
    }
