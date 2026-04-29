import os

class ModelConfig:
    VEO_BUCKET = os.getenv("VEO_BUCKET", "genmedia-canvas")
    # Text Generation
    GEMINI_TEXT_MODELS = [
        "gemini-3.1-flash-lite-preview",
        "gemini-3.1-pro-preview",
        "gemini-3-flash-preview",
    ]
    DEFAULT_GEMINI_TEXT_MODEL = "gemini-3.1-flash-lite-preview"

    # Image Generation/Editing
    GEMINI_IMAGE_MODELS = [
        "gemini-3.1-flash-image-preview",
        "gemini-3-pro-image-preview",
        "gemini-2.5-flash-image",
    ]
    DEFAULT_GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image-preview"

    # Video
    VEO_MODELS = [
        "veo-3.1-lite-generate-001",
        "veo-3.1-fast-generate-001",
        "veo-3.1-generate-001",
    ]
    DEFAULT_VEO_MODEL = "veo-3.1-lite-generate-001"

    # Upscale
    IMAGEN_UPSCALE_MODELS = [
        "imagen-4.0-upscale-preview"
    ]
    DEFAULT_UPSCALE_MODEL = "imagen-4.0-upscale-preview"

    # Music
    MUSIC_MODELS = [
        "lyria-3-clip-preview",
        "lyria-3-pro-preview",
        "lyria-002",
    ]
    DEFAULT_MUSIC_MODEL = "lyria-3-clip-preview"

    # TTS
    TTS_MODELS = [
        "gemini-3.1-flash-tts-preview",
        "gemini-2.5-flash-preview-tts",
        "gemini-2.5-pro-preview-tts",
    ]
    DEFAULT_TTS_MODEL = "gemini-3.1-flash-tts-preview"

    # TTS Voices
    TTS_VOICES = ["Kore", "Leda", "Puck", "Charon", "Fenrir", "Aoede", "Enceladus"]

    # TTS Languages
    TTS_LANGUAGES = [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "it", "name": "Italian"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "nl", "name": "Dutch"},
        {"code": "pl", "name": "Polish"},
        {"code": "ro", "name": "Romanian"},
        {"code": "ru", "name": "Russian"},
        {"code": "uk", "name": "Ukrainian"},
        {"code": "tr", "name": "Turkish"},
        {"code": "ar", "name": "Arabic"},
        {"code": "hi", "name": "Hindi"},
        {"code": "bn", "name": "Bangla"},
        {"code": "ta", "name": "Tamil"},
        {"code": "te", "name": "Telugu"},
        {"code": "th", "name": "Thai"},
        {"code": "id", "name": "Indonesian"},
        {"code": "vi", "name": "Vietnamese"},
        {"code": "ja", "name": "Japanese"},
        {"code": "ko", "name": "Korean"},
        {"code": "zh", "name": "Chinese"},
    ]
    DEFAULT_TTS_LANGUAGE = "en"
    DEFAULT_TTS_VOICE = "Kore"

model_config = ModelConfig()
