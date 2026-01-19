import base64
import re
from typing import Any, Dict, Optional, Union
from google.genai import types
import logging

logger = logging.getLogger(__name__)

def parse_input(val: Any) -> Union[str, types.Part]:
    """
    Parses input value. If it's a data URL (image, video, audio), converts to types.Part.
    Otherwise returns string representation.
    """
    if isinstance(val, str) and val.strip().startswith("data:"):
        match = re.match(r'data:([^;]+);base64,(.+)', val)
        if match:
            mime_type = match.group(1)
            b64_data = match.group(2)
            try:
                return types.Part(
                    inline_data=types.Blob(
                        data=base64.b64decode(b64_data),
                        mime_type=mime_type
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to decode base64 data: {e}")
                return val
    return str(val) if val is not None else ""

def extract_media_bytes(val: Any) -> Optional[bytes]:
    """
    Robustly extracts raw bytes from various input formats:
    - bytes directly
    - base64 data URLs (string)
    - dict with "data" (and "mime_type")
    - dict with "images", "videos", or "audio" lists
    """
    if val is None:
        return None
        
    if isinstance(val, bytes):
        return val
        
    if isinstance(val, str) and val.strip().startswith("data:"):
        match = re.match(r'data:([^;]+);base64,(.+)', val)
        if match:
            try:
                return base64.b64decode(match.group(2))
            except Exception as e:
                logger.warning(f"Failed to decode base64 from string: {e}")
                return None
    
    if isinstance(val, dict):
        if "data" in val:
            data = val["data"]
            return base64.b64decode(data) if isinstance(data, str) else data
        
        for key in ["images", "videos", "audio"]:
            if key in val and isinstance(val[key], list) and val[key]:
                return extract_media_bytes(val[key][0])
                
    return None

def extract_media_info(val: Any) -> Dict[str, Any]:
    """Extracts media bytes and mime_type from various input formats."""
    if val is None:
        return {"data": None, "mime_type": None}
        
    if isinstance(val, dict):
        if "data" in val:
            data = val["data"]
            bytes_data = base64.b64decode(data) if isinstance(data, str) else data
            return {"data": bytes_data, "mime_type": val.get("mime_type")}
        
        if "uri" in val:
            return {"data": val["uri"], "mime_type": val.get("mime_type")}
            
        for key in ["images", "videos", "audio"]:
            if key in val and isinstance(val[key], list) and val[key]:
                return extract_media_info(val[key][0])
                
    bytes_data = extract_media_bytes(val)
    mime_type = None
    if isinstance(val, str) and val.strip().startswith("data:"):
        match = re.match(r'data:([^;]+);base64,(.+)', val)
        if match:
            mime_type = match.group(1)
    
    return {"data": bytes_data, "mime_type": mime_type}
