
import httpx
import google.auth
import google.auth.transport.requests
from core.config import get_settings
from config import model_config
from typing import Dict, Any

settings = get_settings()

class VertexService:
    def __init__(self):
        self._creds = None
        self._project = None
        self._auth_req = None

    @property
    def creds(self):
        if not self._creds:
            from google.oauth2 import service_account
            
            if settings.CREDENTIALS_PATH:
                scopes = ["https://www.googleapis.com/auth/cloud-platform"]
                self._creds = service_account.Credentials.from_service_account_file(
                    settings.CREDENTIALS_PATH, scopes=scopes
                )
                self._project = settings.PROJECT_ID
                # Ensure the environment variable is set for other SDKs
                import os
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.CREDENTIALS_PATH
            else:
                self._creds, self._project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            
            self._auth_req = google.auth.transport.requests.Request()
        return self._creds

    @property
    def auth_req(self):
        if not self._auth_req:
             # Trigger creds load if needed
             _ = self.creds
        return self._auth_req

    def _get_token(self) -> str:
        if not self.creds.valid:
            self.creds.refresh(self.auth_req)
        return self.creds.token

    async def synthesize_raw(self, payload: Dict[str, Any]) -> bytes:
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "x-goog-user-project": settings.PROJECT_ID,
            "Content-Type": "application/json; charset=utf-8"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.TTS_API_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Vertex API Error {response.status_code}: {response.text}")
            
            data = response.json()
            if "audioContent" not in data:
                raise Exception(f"No audio content in response: {data}")
                
            return data["audioContent"] # Returns base64 string

    async def upscale_image(self, image_bytes: bytes, upscale_factor: str = "x2") -> str:
        """Upscales an image using Imagen 4.0 Upscale REST API."""
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "x-goog-user-project": settings.PROJECT_ID,
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # Base64 encode the image
        import base64
        b64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        endpoint = f"https://{settings.REGION}-aiplatform.googleapis.com/v1/projects/{settings.PROJECT_ID}/locations/{settings.REGION}/publishers/google/models/imagen-4.0-upscale-preview:predict"
        
        payload = {
            "instances": [
                {
                    "prompt": "Upscale the image",
                    "image": {
                        "bytesBase64Encoded": b64_image
                    }
                }
            ],
            "parameters": {
                "mode": "upscale",
                "upscaleConfig": {
                    "upscaleFactor": upscale_factor
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=60.0 # Upscaling can take time
            )
            
            if response.status_code != 200:
                raise Exception(f"Imagen API Error {response.status_code}: {response.text}")
            
            data = response.json()
            if "predictions" not in data or not data["predictions"]:
                raise Exception(f"No predictions in response: {data}")
            
            # The API response structure can vary. We'll try to extract the upscaled image robustly.
            prediction = data["predictions"][0]
            
            # 1. Try direct bytesBase64Encoded
            if isinstance(prediction, dict) and "bytesBase64Encoded" in prediction:
                return prediction["bytesBase64Encoded"]
            
            # 2. Try nested in an "image" key
            if isinstance(prediction, dict) and "image" in prediction and isinstance(prediction["image"], dict):
                if "bytesBase64Encoded" in prediction["image"]:
                    return prediction["image"]["bytesBase64Encoded"]
            
            # 3. If prediction is already a string, assume it's the base64 data
            if isinstance(prediction, str):
                return prediction
                
            # If all fails, log the response and raise a descriptive error
            import json
            print(f"[ERROR] Failed to extract upscaled image. Prediction structure: {json.dumps(prediction, indent=2)}")
            raise Exception("Failed to extract upscaled image from Vertex AI response. Check logs for details.")

    async def generate_music(self, prompt: str, negative_prompt: str = "", seed: int = 12345) -> Dict[str, Any]:
        """Generates music using Lyria-002 model on Vertex AI."""
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "x-goog-user-project": settings.PROJECT_ID,
            "Content-Type": "application/json; charset=utf-8"
        }
        
        endpoint = f"https://{settings.REGION}-aiplatform.googleapis.com/v1/projects/{settings.PROJECT_ID}/locations/{settings.REGION}/publishers/google/models/lyria-002:predict"
        
        payload = {
            "instances": [
                {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt if negative_prompt else None
                }
            ],
            "parameters": {
                "sampleCount": 1,
                "candidateCount": 1,
                "audioConfig": {
                    "audioEncoding": "MP3"
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=120.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Lyria API Error {response.status_code}: {response.text}")
            
            data = response.json()
            if "predictions" not in data or not data["predictions"]:
                raise Exception(f"No predictions in response: {data}")
            
            # Lyria returns audioContent or bytesBase64Encoded in predictions
            prediction = data["predictions"][0]
            # Normalize to include 'audioContent' for the router if it's missing but bytesBase64Encoded is present
            if "bytesBase64Encoded" in prediction and "audioContent" not in prediction:
                prediction["audioContent"] = prediction["bytesBase64Encoded"]
            return prediction

    def get_signed_url(self, gcs_uri: str, expiration_mins: int = 60) -> str:
        """Generates a signed URL for a GCS URI."""
        try:
            from google.cloud import storage
            from datetime import timedelta
            
            if not gcs_uri.startswith("gs://"):
                return None
                
            bucket_name = gcs_uri.split("/")[2]
            blob_name = "/".join(gcs_uri.split("/")[3:])
            
            client = storage.Client(credentials=self.creds, project=settings.PROJECT_ID)
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expiration_mins),
                method="GET"
            )
            return url
        except Exception as e:
            print(f"Error generating signed URL for {gcs_uri}: {e}")
            return None

vertex_service = VertexService()
