import json
import re
import io
import base64
from typing import Optional
from PIL import Image
import httpx

from app.ai.base import AIProvider
from app.models.observation import IdentificationResult
from app.config import settings
from app.ai.image_analyzer import analyze_image_heuristics


TRAILLENS_SYSTEM_PROMPT = """You are TrailLens, an outdoor open-weight nature vision companion.
Your central mission: Help people see something in the natural world, understand it quickly, and immediately step away from the screen to observe it in real life.
Analyze the user's nature photo carefully.

IMPORTANT ACCURACY & HONESTY RULES:
1. NEVER fabricate or hallucinate a species name if the organism is not clearly visible in the image.
2. If the photo shows a wide landscape, sunset, sky, panorama, or distant trees without a clear close-up macro organism:
   - Set "identification": "No confident identification — Landscape / Scenic View"
   - Set "scientific_name": null
   - Set "confidence": 0.15
   - Set "confidence_level": "uncertain"
   - In "summary", explain that the image captures a broad scenic landscape or sunset rather than an individual identifiable organism, and advise the explorer to move within 1 meter of a single leaf, flower, or tree trunk.
3. For potentially toxic, irritating, or dangerous wild plants/fungi, always provide a clear safety warning.
4. Keep the summary to 2-3 concise sentences. No conversational filler.

Output MUST be strict valid JSON with no conversational preamble or markdown code fence.
JSON Schema:
{
  "identification": "Common Name of specimen OR 'No confident identification — ...'",
  "scientific_name": "Latin binomial if known, or null",
  "category": "flora | fauna | fungi | geology | weather",
  "confidence": 0.0 to 1.0 (float - do NOT claim 1.0; reflect honest uncertainty),
  "confidence_level": "high | moderate | uncertain",
  "summary": "2-3 concise sentences explaining what is seen.",
  "observations": [
    "Detail 1 the user should physically look for right now (e.g., leaf vein pattern, horizon gradient)",
    "Detail 2",
    "Detail 3"
  ],
  "outdoor_challenge": "A specific 2-5 minute activity to do outdoors right now WITHOUT looking at a phone.",
  "safety_note": "A clear, realistic safety warning.",
  "screen_break_message": "Put your phone away. Spend the next 3 minutes observing without screens."
}
"""


class OpenModelProvider(AIProvider):
    """
    Open-weight model provider for TrailLens.
    Supports:
    - Google Gemma 2 / PaliGemma open weights (via Hugging Face Open Inference API or local Ollama endpoint)
    - Ollama multimodal runtimes (paligemma, minicpm-v, llava, qwen2-vl)
    """

    def __init__(
        self,
        model_name: str = "google/gemma-2-2b-it",
        vision_model_name: str = "google/paligemma-3b-pt-224",
        license_info: str = "Gemma Terms of Use / Open Weights"
    ):
        self._model_name = model_name
        self._vision_model_name = vision_model_name
        self._license = license_info

    @property
    def name(self) -> str:
        return "open_model"

    @property
    def model_name(self) -> str:
        return f"{self._model_name} (Vision: {self._vision_model_name})"

    @property
    def license(self) -> str:
        return self._license

    @property
    def is_offline(self) -> bool:
        return "localhost" in settings.OLLAMA_BASE_URL or "127.0.0.1" in settings.OLLAMA_BASE_URL

    def _image_to_base64(self, image: Image.Image) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def _clean_json_response(self, text: str) -> dict:
        """Strip markdown fences and parse JSON safely."""
        cleaned = text.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
        if fence_match:
            cleaned = fence_match.group(1).strip()
        else:
            brace_match = re.search(r"(\{[\s\S]*\})", cleaned)
            if brace_match:
                cleaned = brace_match.group(1).strip()
        return json.loads(cleaned)

    async def identify(
        self,
        image: Image.Image,
        user_hint: Optional[str] = None
    ) -> IdentificationResult:
        ollama_url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        b64_img = self._image_to_base64(image)

        prompt = TRAILLENS_SYSTEM_PROMPT
        if user_hint:
            prompt += f"\nUser Context / Field Hint: {user_hint}"

        # 1. Try local Ollama open vision model if available
        try:
            # Map configured vision model to Ollama model tag
            ollama_model = "minicpm-v"
            if "paligemma" in self._vision_model_name.lower():
                ollama_model = "paligemma"
            elif "llava" in self._vision_model_name.lower():
                ollama_model = "llava"
            elif "qwen" in self._vision_model_name.lower():
                ollama_model = "qwen2-vl"

            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(
                    ollama_url,
                    json={
                        "model": ollama_model,
                        "prompt": prompt,
                        "images": [b64_img],
                        "stream": False,
                        "format": "json"
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    raw_text = data.get("response", "")
                    parsed = self._clean_json_response(raw_text)
                    conf = float(parsed.get("confidence", 0.7))
                    is_conf = conf >= 0.5 and "no confident" not in parsed.get("identification", "").lower()
                    return IdentificationResult(
                        identification=parsed.get("identification", "Wild Organism"),
                        scientific_name=parsed.get("scientific_name"),
                        category=parsed.get("category", "flora"),
                        confidence=conf,
                        confidence_level=parsed.get("confidence_level", "moderate"),
                        is_confident=is_conf,
                        summary=parsed.get("summary", "Identified using open-weight vision model."),
                        observations=parsed.get("observations", ["Observe leaf texture", "Count petals"]),
                        outdoor_challenge=parsed.get("outdoor_challenge", "Spend 3 minutes looking closely."),
                        safety_note=parsed.get("safety_note", "Do not consume wild organisms."),
                        screen_break_message=parsed.get("screen_break_message", "Put your phone away now."),
                        model_used=f"Ollama Local ({ollama_model})",
                        is_demo=False,
                        fallback_warning=None,
                        scene_description="Processed via live local Ollama open vision model"
                    )
        except Exception:
            # Local Ollama not currently active or unreachable
            pass

        # 2. Try Hugging Face Open Inference API if API token is configured
        if settings.HUGGINGFACE_API_KEY:
            try:
                hf_url = f"{settings.HUGGINGFACE_INFERENCE_URL}/{self._vision_model_name}"
                headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_bytes = buffered.getvalue()

                async with httpx.AsyncClient(timeout=30.0) as client:
                    hf_res = await client.post(
                        hf_url,
                        headers=headers,
                        content=img_bytes
                    )
                    if hf_res.status_code == 200:
                        parsed = self._clean_json_response(hf_res.text)
                        conf = float(parsed.get("confidence", 0.75))
                        is_conf = conf >= 0.5 and "no confident" not in parsed.get("identification", "").lower()
                        return IdentificationResult(
                            identification=parsed.get("identification", "Specimen"),
                            scientific_name=parsed.get("scientific_name"),
                            category=parsed.get("category", "flora"),
                            confidence=conf,
                            confidence_level=parsed.get("confidence_level", "moderate"),
                            is_confident=is_conf,
                            summary=parsed.get("summary", "Analyzed with Hugging Face open weights."),
                            observations=parsed.get("observations", []),
                            outdoor_challenge=parsed.get("outdoor_challenge", "Observe in nature."),
                            safety_note=parsed.get("safety_note", "Never ingest wild specimens."),
                            screen_break_message=parsed.get("screen_break_message", "Put phone away."),
                            model_used=f"HuggingFace Open Weights ({self._vision_model_name})",
                            is_demo=False,
                            fallback_warning=None,
                            scene_description="Processed via live Hugging Face open vision weights"
                        )
            except Exception:
                pass

        # 3. Transparent fallback to genuine image heuristics
        # NEVER falsely label this as a Gemma or PaliGemma prediction
        result = analyze_image_heuristics(image, user_hint)
        result.model_used = "TrailLens Heuristics Engine (Offline Fallback)"
        result.is_demo = True
        result.fallback_warning = (
            f"LIVE INFERENCE UNAVAILABLE: The configured open-weight model ({self.model_name}) "
            f"could not be reached at {settings.OLLAMA_BASE_URL} and no valid HUGGINGFACE_API_KEY is configured. "
            f"This result was produced by the offline heuristic engine, NOT by {self._model_name} or {self._vision_model_name}."
        )
        return result
