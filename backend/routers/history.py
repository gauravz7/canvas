from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from models import Asset
from auth import get_current_user, get_current_user_optional, CurrentUser

router = APIRouter()

class AssetResponse(BaseModel):
    id: int
    user_id: str
    asset_type: str
    storage_path: str
    filename: str
    mime_type: Optional[str]
    prompt: Optional[str]
    model_id: Optional[str]
    created_at: datetime
    meta_data: Optional[dict]
    signed_url: Optional[str] = None

    class Config:
        from_attributes = True


def _enrich_assets(assets):
    """Add signed URLs for GCS-stored assets."""
    from services.vertex_service import vertex_service

    results = []
    for asset in assets:
        asset_dict = {c.name: getattr(asset, c.name) for c in asset.__table__.columns}
        if asset.storage_path.startswith("gs://"):
            asset_dict["signed_url"] = vertex_service.get_signed_url(asset.storage_path)
        results.append(asset_dict)
    return results


@router.get("", response_model=List[AssetResponse])
@router.get("/", response_model=List[AssetResponse])
async def get_history(
    asset_type: Optional[str] = Query(None, description="Filter by asset type: image, video, audio"),
    limit: int = Query(50, ge=1, le=200, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: CurrentUser = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    user_ids = [current_user.uid]
    if current_user.uid != "default":
        user_ids.append("default")
    query = db.query(Asset).filter(Asset.user_id.in_(user_ids))
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    db_assets = query.order_by(Asset.created_at.desc()).offset(offset).limit(min(limit, 200)).all()
    enriched = _enrich_assets(db_assets)

    # Merge with GCS-backed assets (for Cloud Run durability across instance restarts)
    try:
        from services.storage_service import storage_service
        existing_paths = {a.get("storage_path") for a in enriched}
        for uid in user_ids:
            for gcs_asset in storage_service.list_assets_from_gcs(uid):
                if gcs_asset.get("storage_path") in existing_paths:
                    continue
                if asset_type and gcs_asset.get("asset_type") != asset_type:
                    continue
                # Map to AssetResponse-shaped dict
                enriched.append({
                    "id": gcs_asset.get("id", 0),
                    "user_id": gcs_asset.get("user_id", uid),
                    "asset_type": gcs_asset.get("asset_type", ""),
                    "storage_path": gcs_asset.get("storage_path", ""),
                    "filename": gcs_asset.get("filename", ""),
                    "mime_type": gcs_asset.get("mime_type"),
                    "prompt": gcs_asset.get("prompt"),
                    "model_id": gcs_asset.get("model_id"),
                    "created_at": gcs_asset.get("created_at"),
                    "meta_data": gcs_asset.get("meta_data") or {},
                    "signed_url": None,
                })
                existing_paths.add(gcs_asset.get("storage_path"))
    except Exception:
        pass

    enriched.sort(key=lambda a: str(a.get("created_at") or ""), reverse=True)
    return enriched[:limit]
