from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    asset_type = Column(String, index=True)  # image, video, audio
    storage_path = Column(String, nullable=False) # Relative path to backend/data/assets
    filename = Column(String, nullable=False)
    mime_type = Column(String) 
    prompt = Column(Text)
    model_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta_data = Column(JSON, default={}) # Extra params (seed, aspect ratio, etc)

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, default="Untitled Workflow")
    data = Column(JSON, nullable=False) # Stores the full node/edge graph
    user_id = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

