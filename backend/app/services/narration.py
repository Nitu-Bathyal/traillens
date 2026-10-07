from typing import Optional, Dict, Any
import httpx
from app.config import settings


class NarrationService:
    """
    ElevenLabs Voice Narration Service with Web Speech API browser fallback.
    Speaks a short audio prompt instructing the user to observe nature
    and put their phone away.
    """

    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.voice_id = settings.ELEVENLABS_VOICE_ID

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def prepare_script(self, identification: str, observation_hint: str, challenge_duration: int = 3) -> str:
        """
        Produce a concise, calming voice script that prioritizes putting the device away.
        """
        return (
            f"You may be looking at {identification}. "
            f"Notice {observation_hint}. "
            f"Now, put your phone away and spend {challenge_duration} minutes observing without screens."
        )

    async def generate_speech(self, text: str) -> Dict[str, Any]:
        """
        Generate audio bytes via ElevenLabs API if key is present,
        otherwise return instructions for browser Web Speech synthesis.
        """
        if not self.is_configured():
            return {
                "provider": "web_speech_fallback",
                "audio_base64": None,
                "text": text,
                "message": "ElevenLabs API key not configured. Using client-side Web Speech API for voice."
            }

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.65,
                "similarity_boost": 0.75,
                "style": 0.2,
                "use_speaker_boost": True
            }
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    import base64
                    audio_b64 = base64.b64encode(res.content).decode("utf-8")
                    return {
                        "provider": "elevenlabs",
                        "audio_base64": audio_b64,
                        "audio_mime": "audio/mpeg",
                        "text": text,
                        "message": "Voice generated with ElevenLabs."
                    }
                else:
                    return {
                        "provider": "web_speech_fallback",
                        "audio_base64": None,
                        "text": text,
                        "message": f"ElevenLabs request returned status {res.status_code}. Falling back to browser speech."
                    }
        except Exception as e:
            return {
                "provider": "web_speech_fallback",
                "audio_base64": None,
                "text": text,
                "message": f"ElevenLabs call failed ({str(e)}). Falling back to browser speech."
            }


narration_service = NarrationService()
