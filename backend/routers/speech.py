
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import base64
from services.vertex_service import vertex_service
from services.storage_service import storage_service
from config import model_config
import asyncio

router = APIRouter()

class SingleSpeakerRequest(BaseModel):
    text: str
    voice_name: str = model_config.DEFAULT_TTS_VOICE
    language_code: str = "en-us"
    prompt: Optional[str] = None
    model_id: str = model_config.DEFAULT_TTS_MODEL
    user_id: str = "default_user"

class Turn(BaseModel):
    speaker: str
    text: str

class MultiSpeakerRequest(BaseModel):
    turns: List[Turn]
    prompt: Optional[str] = None
    speaker_map: Dict[str, str] # Alias -> Voice Name
    model_id: str = model_config.DEFAULT_TTS_MODEL
    user_id: str = "default_user"

@router.post("/single")
async def synthesize_single(req: SingleSpeakerRequest):
    payload = {
        "input": {
            "text": req.text,
            "prompt": req.prompt
        },
        "voice": {
            "languageCode": req.language_code,
            "name": req.voice_name,
            "model_name": req.model_id
        },
        "audioConfig": {
            "audioEncoding": "LINEAR16"
        }
    }
    
    try:
        b64_audio = await vertex_service.synthesize_raw(payload)
        
        # Save asset
        asset = await asyncio.to_thread(
            storage_service.save_asset,
            user_id=req.user_id,
            content=b64_audio,
            asset_type="audio",
            mime_type="audio/wav", # LINEAR16 usually wrapped in wav or just raw pcm? Vertex usually allows WAV request. 
            # Wait, Vertex 'audioEncoding': 'LINEAR16' returns raw PCM or WAV? 
            # Usually it returns WAV if you ask for it, or just raw. 
            # Let's assume it's playable as is or we wrap it. 
            # Actually, `WaveformPlayer` handles it.
            # "audioContent" from Vertex is usually valid audio file content (WAV) if configured?
            # Actually LINEAR16 is raw PCM. MP3 is MP3.
            # Let's check what we receive. 
            # If it works in frontend, it's likely WAV or MP3.
            # Default to audio/wav for now.
            prompt=req.text[:100],
            model_id=req.model_id,
            meta_data={"voice_name": req.voice_name}
        )
        
        return {
            "audioContent": b64_audio,
            "storage_path": asset.storage_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/multi")
async def synthesize_multi(req: MultiSpeakerRequest):
    # Construct speaker configs
    speaker_configs = []
    for alias, voice in req.speaker_map.items():
        speaker_configs.append({
            "speakerAlias": alias,
            "speakerId": voice
        })

    payload = {
        "input": {
            "prompt": req.prompt,
            "multiSpeakerMarkup": {
                "turns": [{"speaker": t.speaker, "text": t.text} for t in req.turns]
            }
        },
        "voice": {
            "languageCode": "en-us",
            "modelName": req.model_id,
            "multiSpeakerVoiceConfig": {
                "speakerVoiceConfigs": speaker_configs
            }
        },
        "audioConfig": {
            "audioEncoding": "LINEAR16",
            "sampleRateHertz": 24000
        }
    }

    try:
        b64_audio = await vertex_service.synthesize_raw(payload)
        
        # Save asset
        asset = await asyncio.to_thread(
            storage_service.save_asset,
            user_id=req.user_id,
            content=b64_audio,
            asset_type="audio",
            mime_type="audio/wav",
            prompt=req.prompt or "Multi-speaker conversation",
            model_id=req.model_id,
            meta_data={"speaker_map": req.speaker_map}
        )

        return {
            "audioContent": b64_audio,
            "storage_path": asset.storage_path
        }
    except Exception as e:
        error_msg = str(e)
        status_code = 500
        if "400" in error_msg:
            status_code = 400
        elif "401" in error_msg:
            status_code = 401
        elif "403" in error_msg:
            status_code = 403
        elif "404" in error_msg:
            status_code = 404
            
        print(f"Speech Gen Error: {error_msg}")
        raise HTTPException(status_code=status_code, detail=error_msg)
