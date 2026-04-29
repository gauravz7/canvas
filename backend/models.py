from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
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
    visibility = Column(String, default="private", index=True)
    team_id = Column(String, nullable=True, index=True)
    creator_name = Column(String, nullable=True)
    creator_email = Column(String, nullable=True)

class Team(Base):
    __tablename__ = "teams"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    join_code = Column(String, unique=True, index=True)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TeamMember(Base):
    __tablename__ = "team_members"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    user_email = Column(String)
    user_name = Column(String)
    role = Column(String, default="member")
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

