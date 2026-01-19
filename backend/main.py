import logging
from services.log_service import UnifiedLoggingHandler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import speech, generative, history, logs
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Setup root logging to redirect to LogService
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(UnifiedLoggingHandler())

app = FastAPI(title="Gemini-TTS Playground")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(speech.router, prefix="/api/synthesize", tags=["speech"])
app.include_router(generative.router, prefix="/api/generate", tags=["generative"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])

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
        "DEFAULT_TTS_VOICE": model_config.DEFAULT_TTS_VOICE
    }

# Serve static files from the frontend/dist directory
# We assume the directory is at ../frontend/dist relative to this file
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

# Mount storage for local access
data_dir = os.path.join(os.path.dirname(__file__), "data")
app.mount("/data", StaticFiles(directory=data_dir), name="data")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # If the path starts with api, it should have been handled by the router
    if full_path.startswith("api"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
    
    # Check if file exists in dist
    file_path = os.path.join(frontend_dist, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Fallback to index.html for SPA
    return FileResponse(os.path.join(frontend_dist, "index.html"))
