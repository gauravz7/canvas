import os
import shutil
import uuid
import base64
from datetime import datetime
from typing import Optional, List, Union
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Asset
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)

# Ensure tables exist
Base.metadata.create_all(bind=engine)

class StorageService:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(self.base_dir, "data", "assets")
        os.makedirs(self.assets_dir, exist_ok=True)

    def save_asset(self, 
                   user_id: str, 
                   content: Union[bytes, str], 
                   asset_type: str, 
                   mime_type: str, 
                   prompt: str, 
                   model_id: str,
                   meta_data: dict = None) -> Asset:
        """
        Save asset to disk and database.
        content: can be bytes or a base64 string or a GCS URI (though GCS URI we might just store as reference)
        """
        db = SessionLocal()
        try:
            # 1. Prepare File Path
            # Structure: assets/{user_id}/{asset_type}/timestamp_uuid.ext
            user_dir = os.path.join(self.assets_dir, user_id, asset_type)
            os.makedirs(user_dir, exist_ok=True)

            ext = self._get_ext_from_mime(mime_type)
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(user_dir, filename)
            relative_path = os.path.join(user_id, asset_type, filename)

            # 2. Write File
            if isinstance(content, str) and content.startswith("gs://"):
                # For GCS, we might not download it locally immediately, 
                # OR we could just store the GCS URI.
                # The user asked to "keep all assets available in the folder". 
                # For now, if it's GCS, we will assume we store the URI in storage_path or metadata.
                # BUT, to make it "available in the folder", we probably want to download it?
                # Let's simple store the logic: if it's bytes/b64, save file. If GCS, store URI.
                 relative_path = content # Check if this breaks things later. 
                 # Actually, let's strictly support saving BYTES here for generated content.
                 # If we receive a GCS URI as "content", it usually means we generated it to GCS.
                 # We should probably treat it as a "reference" asset.
                 pass
            
            if isinstance(content, bytes):
                with open(file_path, "wb") as f:
                    f.write(content)
            elif isinstance(content, str) and not content.startswith("gs://"):
                # Assume base64
                try:
                    # Clean header if present (data:image/png;base64,...)
                    if "," in content:
                        content = content.split(",")[1]
                    file_bytes = base64.b64decode(content)
                    with open(file_path, "wb") as f:
                        f.write(file_bytes)
                except Exception as e:
                    print(f"Error decoding base64: {e}")
                    # If fail, maybe it's just a string prompt? No, content should be media.
                    return None

            # 3. DB Entry
            asset = Asset(
                user_id=user_id,
                asset_type=asset_type,
                storage_path=relative_path,
                filename=filename if not relative_path.startswith("gs://") else os.path.basename(relative_path),
                mime_type=mime_type,
                prompt=prompt,
                model_id=model_id,
                meta_data=meta_data or {}
            )
            db.add(asset)
            db.commit()
            db.refresh(asset)
            return asset
        finally:
            db.close()

    def get_history(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Asset]:
        db = SessionLocal()
        try:
            return db.query(Asset).filter(Asset.user_id == user_id).order_by(Asset.created_at.desc()).offset(offset).limit(limit).all()
        finally:
            db.close()

    def download_gcs_blob(self, gcs_uri: str, user_id: str) -> Optional[str]:
        """
        Downloads a GCS blob to local storage and returns the relative path.
        Used to proxy GCS videos for reliable frontend playback.
        """
        try:
            if not gcs_uri.startswith("gs://"):
                return None
                
            bucket_name = gcs_uri.split("/")[2]
            blob_name = "/".join(gcs_uri.split("/")[3:])
            
            # Use default client (picks up GOOGLE_APPLICATION_CREDENTIALS)
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            user_video_dir = os.path.join(self.assets_dir, user_id, "video")
            os.makedirs(user_video_dir, exist_ok=True)
            
            # Simple hash/clean name from blob_name to avoid path injection
            safe_name = blob_name.replace("/", "_")
            if not safe_name.endswith(".mp4"):
                safe_name += ".mp4"
                
            local_path = os.path.join(user_video_dir, safe_name)
            relative_path = os.path.join(user_id, "video", safe_name)
            
            if not os.path.exists(local_path):
                logger.info(f"Downloading GCS blob {gcs_uri} to {local_path}")
                blob.download_to_filename(local_path)
            
            return relative_path
        except Exception as e:
            logger.error(f"Error downloading GCS blob {gcs_uri}: {e}")
            return None

    def _get_ext_from_mime(self, mime_type: str) -> str:
        if "jpeg" in mime_type or "jpg" in mime_type: return ".jpg"
        if "png" in mime_type: return ".png"
        if "mp4" in mime_type: return ".mp4"
        if "cwav" in mime_type: return ".cwav" # Custom audio format?
        if "wav" in mime_type: return ".wav"
        if "mp3" in mime_type: return ".mp3"
        return ""

storage_service = StorageService()
