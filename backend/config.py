import os

class ModelConfig:
    VEO_BUCKET = os.getenv("VEO_BUCKET", "genmedia-canvas")
    # Text Generation
    GEMINI_TEXT_MODELS = [
        "gemini-3-pro-preview",
        "gemini-3-flash-preview",
    ]
    DEFAULT_GEMINI_TEXT_MODEL = "gemini-3-pro-preview"

    # Image Generation/Editing
    GEMINI_IMAGE_MODELS = [
        "gemini-3-pro-image-preview",
        "gemini-2.5-flash-image",
    ]
    DEFAULT_GEMINI_IMAGE_MODEL = "gemini-3-pro-image-preview"

    # Video
    VEO_MODELS = [
        "veo-3.1-generate-preview",
        "veo-3.1-fast-generate-preview"
    ]
    DEFAULT_VEO_MODEL = "veo-3.1-generate-preview"

    # Upscale
    IMAGEN_UPSCALE_MODELS = [
        "imagen-4.0-upscale-preview"
    ]
    DEFAULT_UPSCALE_MODEL = "imagen-4.0-upscale-preview"

    # Music
    MUSIC_MODELS = [
        "lyria-002"
    ]
    DEFAULT_MUSIC_MODEL = "lyria-002"

    # TTS
    TTS_MODELS = [
        "gemini-2.5-flash-tts",
        "gemini-2.5-pro-tts",
        "gemini-2.5-flash-lite-preview-tts"
    ]
    DEFAULT_TTS_MODEL = "gemini-2.5-flash-tts"

    # TTS Voices
    TTS_VOICES = ["Kore", "Leda", "Puck", "Charon", "Fenrir", "Aoede"]
    DEFAULT_TTS_VOICE = "Kore"

model_config = ModelConfig()
