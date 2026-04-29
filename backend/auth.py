import os
import logging
from typing import Optional
from fastapi import Depends, HTTPException, Request, Query
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

logger = logging.getLogger(__name__)

FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "vital-octagon-19612")

class CurrentUser(BaseModel):
    uid: str
    email: str = ""
    name: Optional[str] = None
    picture: Optional[str] = None

def verify_firebase_token(token: str) -> dict:
    try:
        claims = id_token.verify_firebase_token(
            token,
            google_requests.Request(),
            audience=FIREBASE_PROJECT_ID
        )
        return claims
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")

async def get_current_user(
    request: Request,
    user_id: Optional[str] = Query(None)
) -> CurrentUser:
    auth_header = request.headers.get("Authorization", "")

    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        claims = verify_firebase_token(token)
        return CurrentUser(
            uid=claims.get("sub", claims.get("user_id", "")),
            email=claims.get("email", ""),
            name=claims.get("name"),
            picture=claims.get("picture")
        )

    # Dev mode fallback
    dev_user_id = request.headers.get("X-User-Id") or user_id
    if dev_user_id:
        return CurrentUser(uid=dev_user_id, email="dev@local", name="Dev User")

    raise HTTPException(status_code=401, detail="Authentication required")


async def get_current_user_optional(
    request: Request,
    user_id: Optional[str] = Query(None)
) -> CurrentUser:
    """Return the authenticated user if possible, otherwise fall back to a default user."""
    try:
        return await get_current_user(request, user_id)
    except HTTPException:
        return CurrentUser(uid="default", email="", name="Anonymous")
