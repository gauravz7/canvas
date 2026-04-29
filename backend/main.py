import logging
from services.log_service import UnifiedLoggingHandler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import speech, generative, history, logs, teams
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import re
import mimetypes

logger = logging.getLogger(__name__)

# Setup root logging to redirect to LogService
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(UnifiedLoggingHandler())

app = FastAPI(title="Gemini-TTS Playground")

cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:5175")
cors_origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(speech.router, prefix="/api/synthesize", tags=["speech"])
app.include_router(generative.router, prefix="/api/generate", tags=["generative"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])

from canvas_module import router as canvas_router
app.include_router(canvas_router.router, prefix="/api/workflow", tags=["workflow"])

@app.get("/health")
def health():
    return {"status": "ok"}

from config import model_config
@app.get("/api/config")
def get_config():
    return {
        "GEMINI_TEXT_MODELS": model_config.GEMINI_TEXT_MODELS,
        "DEFAULT_GEMINI_TEXT_MODEL": model_config.DEFAULT_GEMINI_TEXT_MODEL,
        "GEMINI_IMAGE_MODELS": model_config.GEMINI_IMAGE_MODELS,
        "DEFAULT_GEMINI_IMAGE_MODEL": model_config.DEFAULT_GEMINI_IMAGE_MODEL,
        "VEO_MODELS": model_config.VEO_MODELS,
        "DEFAULT_VEO_MODEL": model_config.DEFAULT_VEO_MODEL,
        "IMAGEN_UPSCALE_MODELS": model_config.IMAGEN_UPSCALE_MODELS,
        "DEFAULT_UPSCALE_MODEL": model_config.DEFAULT_UPSCALE_MODEL,
        "MUSIC_MODELS": model_config.MUSIC_MODELS,
        "DEFAULT_MUSIC_MODEL": model_config.DEFAULT_MUSIC_MODEL,
        "TTS_MODELS": model_config.TTS_MODELS,
        "DEFAULT_TTS_MODEL": model_config.DEFAULT_TTS_MODEL,
        "TTS_VOICES": model_config.TTS_VOICES,
        "DEFAULT_TTS_VOICE": model_config.DEFAULT_TTS_VOICE,
        "TTS_LANGUAGES": model_config.TTS_LANGUAGES,
        "DEFAULT_TTS_LANGUAGE": model_config.DEFAULT_TTS_LANGUAGE
    }

# Serve static files from the frontend/dist directory
# We assume the directory is at ../frontend/dist relative to this file
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

@app.get("/api/media/{user_id}/{asset_type}/{filename}")
async def serve_media(user_id: str, asset_type: str, filename: str):
    safe_user = re.sub(r'[^a-zA-Z0-9_\-.]', '_', user_id)
    safe_type = re.sub(r'[^a-zA-Z0-9_\-.]', '_', asset_type)
    safe_file = re.sub(r'[^a-zA-Z0-9_\-.]', '_', filename)

    assets_dir = os.path.join(os.path.dirname(__file__), "data", "assets")
    file_path = os.path.realpath(os.path.join(assets_dir, safe_user, safe_type, safe_file))
    assets_dir_real = os.path.realpath(assets_dir)

    if not file_path.startswith(assets_dir_real + os.sep):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    if not os.path.isfile(file_path):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    mime_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(file_path, media_type=mime_type)

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith("api"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    file_path = os.path.realpath(os.path.join(frontend_dist, full_path))
    frontend_dist_real = os.path.realpath(frontend_dist)

    if not file_path.startswith(frontend_dist_real + os.sep) and file_path != frontend_dist_real:
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    if os.path.isfile(file_path):
        return FileResponse(file_path)

    return FileResponse(os.path.join(frontend_dist, "index.html"))
