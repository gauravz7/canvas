
import os
from functools import lru_cache

class Settings:
    PROJECT_ID: str = "vital-octagon-19612"
    REGION: str = "us-central1"
    TTS_API_ENDPOINT: str = "https://texttospeech.googleapis.com/v1beta1/text:synthesize"
    CREDENTIALS_PATH: str = None

    # Optional: Allow override via env
    def __init__(self):
        self.PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "vital-octagon-19612")
        self.CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        # Fallback to local keys.json if it exists and no env var set
        if not self.CREDENTIALS_PATH:
            potential_keys = os.path.join(os.path.dirname(os.path.dirname(__file__)), "keys.json")
            if os.path.exists(potential_keys):
                self.CREDENTIALS_PATH = potential_keys
                # Set env var for other libraries that look for it
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.CREDENTIALS_PATH

@lru_cache()
def get_settings():
    return Settings()
