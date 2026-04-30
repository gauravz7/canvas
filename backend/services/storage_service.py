import os
import re
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

    def _sanitize_path_component(self, value: str) -> str:
        sanitized = re.sub(r'[^a-zA-Z0-9_\-.]', '_', value)
        if not sanitized or sanitized in ('.', '..'):
            sanitized = 'invalid'
        return sanitized

    def save_asset(self,
                   user_id: str,
                   content: Union[bytes, str],
                   asset_type: str,
                   mime_type: str,
                   prompt: str,
                   model_id: str,
                   meta_data: dict = None) -> Asset:
        db = SessionLocal()
        try:
            user_id = self._sanitize_path_component(user_id)
            asset_type = self._sanitize_path_component(asset_type)
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

            # Also persist to GCS for cross-instance durability on Cloud Run
            self._persist_asset_to_gcs(asset, file_path)

            return asset
        finally:
            db.close()

    def _persist_asset_to_gcs(self, asset, local_file_path: str):
        """Upload asset file + metadata JSON to GCS so it survives Cloud Run instance restarts."""
        try:
            from config import model_config
            import json
            bucket_name = os.getenv("ASSETS_BUCKET", model_config.VEO_BUCKET)
            client = storage.Client()
            bucket = client.bucket(bucket_name)

            # Upload the asset file
            if local_file_path and os.path.exists(local_file_path):
                blob_path = f"user_assets/{asset.storage_path}"
                blob = bucket.blob(blob_path)
                blob.upload_from_filename(local_file_path, content_type=asset.mime_type)

            # Upload metadata sidecar JSON
            meta = {
                "user_id": asset.user_id,
                "asset_type": asset.asset_type,
                "storage_path": asset.storage_path,
                "filename": asset.filename,
                "mime_type": asset.mime_type,
                "prompt": asset.prompt,
                "model_id": asset.model_id,
                "created_at": asset.created_at.isoformat() if asset.created_at else None,
                "meta_data": asset.meta_data or {},
            }
            meta_blob = bucket.blob(f"user_asset_metadata/{asset.user_id}/{asset.id}.json")
            meta_blob.upload_from_string(json.dumps(meta), content_type="application/json")
        except Exception as e:
            logger.warning(f"GCS persistence failed (non-fatal): {e}")

    def list_assets_from_gcs(self, user_id: str) -> List[dict]:
        """List asset metadata from GCS for a given user. Used to recover after instance restart."""
        try:
            from config import model_config
            import json
            user_id = self._sanitize_path_component(user_id)
            bucket_name = os.getenv("ASSETS_BUCKET", model_config.VEO_BUCKET)
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            prefix = f"user_asset_metadata/{user_id}/"
            blobs = list(bucket.list_blobs(prefix=prefix))
            assets = []
            for blob in blobs:
                try:
                    data = json.loads(blob.download_as_text())
                    assets.append(data)
                except Exception:
                    pass
            assets.sort(key=lambda a: a.get("created_at", ""), reverse=True)
            return assets
        except Exception as e:
            logger.warning(f"GCS list_assets failed: {e}")
            return []

    def get_history(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Asset]:
        user_id = self._sanitize_path_component(user_id)
        db = SessionLocal()
        try:
            return db.query(Asset).filter(Asset.user_id == user_id).order_by(Asset.created_at.desc()).offset(offset).limit(limit).all()
        finally:
            db.close()

    def download_gcs_blob(self, gcs_uri: str, user_id: str) -> Optional[str]:
        try:
            if not gcs_uri.startswith("gs://"):
                return None

            user_id = self._sanitize_path_component(user_id)
            bucket_name = gcs_uri.split("/")[2]
            blob_name = "/".join(gcs_uri.split("/")[3:])

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

    def register_asset(
        self,
        user_id: str,
        storage_path: str,
        asset_type: str,
        mime_type: str,
        prompt: str = "",
        model_id: str = "",
        meta_data: dict = None
    ) -> Asset:
        """Register an existing file as an Asset in the DB without re-saving content."""
        db = SessionLocal()
        try:
            user_id = self._sanitize_path_component(user_id)
            # Skip if already registered for this user + path
            existing = db.query(Asset).filter(
                Asset.user_id == user_id,
                Asset.storage_path == storage_path
            ).first()
            if existing:
                return existing

            filename = os.path.basename(storage_path)
            asset = Asset(
                user_id=user_id,
                asset_type=asset_type,
                storage_path=storage_path,
                filename=filename,
                mime_type=mime_type,
                prompt=prompt,
                model_id=model_id,
                meta_data=meta_data or {}
            )
            db.add(asset)
            db.commit()
            db.refresh(asset)
            logger.info(f"Registered asset {asset.id}: {storage_path} ({asset_type}) for user={user_id}")

            # Persist to GCS for cross-instance durability
            full_local_path = os.path.join(self.assets_dir, storage_path)
            self._persist_asset_to_gcs(asset, full_local_path)

            return asset
        except Exception as e:
            logger.error(f"register_asset failed: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    def upload_to_gcs(self, data: bytes, bucket_name: str, mime_type: str = "video/mp4") -> str:
        import uuid as _uuid
        blob_path = f"uploads/{_uuid.uuid4()}.mp4"
        try:
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            blob.upload_from_string(data, content_type=mime_type)
            gcs_uri = f"gs://{bucket_name}/{blob_path}"
            logger.info(f"Uploaded {len(data)} bytes to {gcs_uri}")
            return gcs_uri
        except Exception as e:
            logger.error(f"GCS upload failed: {e}")
            raise

    def _get_ext_from_mime(self, mime_type: str) -> str:
        if not mime_type:
            return ""
        m = mime_type.lower()
        if "jpeg" in m or "jpg" in m: return ".jpg"
        if "png" in m: return ".png"
        if "webp" in m: return ".webp"
        if "mp4" in m: return ".mp4"
        if "webm" in m: return ".webm"
        if "wav" in m: return ".wav"
        if "mpeg" in m or "mp3" in m: return ".mp3"
        if "ogg" in m: return ".ogg"
        return ""

storage_service = StorageService()
