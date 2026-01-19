from .base import BaseNodeExecutor
from backend.core.media_utils import extract_media_bytes
import asyncio
from typing import Any, Dict

class ImagenExecutor(BaseNodeExecutor):
    """Executor for Imagen Upscale nodes."""

    async def execute(self, node: Any, inputs: Dict[str, Any], user_id: str, context: Dict[str, Any] = None) -> Any:
        image_inputs = inputs.get("image", []) or inputs.get("input", [])
        image_to_upscale = None
        
        for val in image_inputs:
            extracted = extract_media_bytes(val)
            if extracted:
                image_to_upscale = extracted
                break
        
        if not image_to_upscale:
            return {"error": "No image found to upscale"}

        config = node.data.config or {}
        upscale_factor = config.get("upscale_factor", "x2")

        try:
             upscaled_b64 = await self.services['vertex'].upscale_image(
                 image_bytes=image_to_upscale,
                 upscale_factor=upscale_factor
             )
             
             asset = await asyncio.to_thread(
                 self.services['storage'].save_asset,
                 user_id=user_id,
                 content=upscaled_b64,
                 asset_type="image",
                 mime_type="image/png",
                 prompt="Upscaled image",
                 model_id="imagen-4.0-upscale-preview"
             )
             
             return {
                 "images": [{
                     "data": upscaled_b64,
                     "mime_type": "image/png",
                     "storage_path": asset.storage_path
                 }]
             }
        except Exception as e:
            self.logger.error(f"Imagen Upscale failed: {e}")
            raise e
