
import os
from functools import lru_cache

class Settings:
    PROJECT_ID: str = None
    REGION: str = "us-central1"
    TTS_API_ENDPOINT: str = "https://texttospeech.googleapis.com/v1beta1/text:synthesize"
    CREDENTIALS_PATH: str = None

    def __init__(self):
        self.PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.PROJECT_ID:
            import logging
            logging.getLogger(__name__).warning(
                "GOOGLE_CLOUD_PROJECT not set. GCP API calls will fail."
            )
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
