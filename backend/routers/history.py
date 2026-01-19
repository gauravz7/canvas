from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from services.storage_service import storage_service
from pydantic import BaseModel
from datetime import datetime

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

@router.get("/{user_id}", response_model=List[AssetResponse])
async def get_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0
):
    assets = storage_service.get_history(user_id, limit, offset)
    
    # Enrich with signed URLs for GCS assets
    from services.vertex_service import vertex_service
    
    # We need to convert SQLAlchemy models to Pydantic or dict to add signed_url
    results = []
    for asset in assets:
        asset_dict = {c.name: getattr(asset, c.name) for c in asset.__table__.columns}
        if asset.storage_path.startswith("gs://"):
            asset_dict["signed_url"] = vertex_service.get_signed_url(asset.storage_path)
        results.append(asset_dict)
        
    return results
