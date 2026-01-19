from .base import BaseNodeExecutor
import asyncio
import base64
from typing import Any, Dict

class AudioExecutor(BaseNodeExecutor):
    """Executor for Speech and Music Generation nodes."""

    async def execute(self, node: Any, inputs: Dict[str, Any], user_id: str, context: Dict[str, Any] = None) -> Any:
        prompt = self._get_prompt(node, inputs)
        if not prompt:
            return {"error": "No prompt provided"}

        try:
            if node.type == "speech_gen":
                return await self._execute_speech(node, prompt, user_id)
            elif node.type == "lyria_gen":
                return await self._execute_music(node, prompt, user_id)
        except Exception as e:
             self.logger.error(f"Audio execution failed: {e}")
             raise e

    def _get_prompt(self, node: Any, inputs: Dict[str, Any]) -> str:
        text_inputs = inputs.get("text", []) or inputs.get("input", [])
        return text_inputs[0] if text_inputs else node.data.value or ""

    async def _execute_speech(self, node: Any, prompt: str, user_id: str):
        config = node.data.config or {}
        # Use defaults from config or fallback strings if needed, matching Studio logic
        # Fix: use 'or' to handle empty strings coming from frontend
        model_id = config.get("model_id") or "gemini-2.5-flash-tts"
        voice_name = config.get("voice_name") or "Kore"

        # Construct payload matching routers/speech.py logic for Gemini TTS
        payload = {
            "input": {"text": prompt},
             "voice": {
                 "languageCode": "en-US", 
                 "name": voice_name,
                 "model_name": model_id
             },
             "audioConfig": {"audioEncoding": "LINEAR16"}
        }
        # Remove model_name if None (sanity check)
        if not payload["voice"]["model_name"]:
            del payload["voice"]["model_name"]

        print(f"[DEBUG] TTS Config: voice={voice_name}, model={model_id}")
        print(f"[DEBUG] TTS Payload: {payload}")
        self.logger.info(f"TTS Config: voice={voice_name}, model={model_id}")
        self.logger.info(f"TTS Payload: {payload}")

        b64_audio = await self.services['vertex'].synthesize_raw(payload)
        
        audio_content = base64.b64decode(b64_audio)
        asset = await asyncio.to_thread(
            self.services['storage'].save_asset,
            user_id=user_id,
            content=audio_content,
            asset_type="audio",
            mime_type="audio/wav", 
            prompt=prompt[:100],
            model_id=model_id,
            meta_data={"voice_name": voice_name}
        )

        return {
            "audio": {
                "data": b64_audio,
                "mime_type": "audio/mp3",
                "storage_path": asset.storage_path
            }
        }

    async def _execute_music(self, node: Any, prompt: str, user_id: str):
        result = await self.services['vertex'].generate_music(prompt=prompt)
        b64_audio = result.get("audioContent")
        audio_content = base64.b64decode(b64_audio)
        
        asset = await asyncio.to_thread(
            self.services['storage'].save_asset,
             user_id=user_id,
             content=audio_content,
             asset_type="audio",
             mime_type="audio/mp3",
             prompt=prompt[:100],
             model_id="lyria-002"
        )
        
        return {
            "audio": {
                "data": b64_audio,
                 "mime_type": "audio/mp3",
                 "storage_path": asset.storage_path
            }
        }
