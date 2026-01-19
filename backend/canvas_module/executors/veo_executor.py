from .base import BaseNodeExecutor
from backend.core.media_utils import extract_media_info
import asyncio
import base64
from typing import Any, Dict, List

class VeoExecutor(BaseNodeExecutor):
    """Executor for Veo Video Generation nodes."""

    async def execute(self, node: Any, inputs: Dict[str, Any], user_id: str, context: Dict[str, Any] = None) -> Any:
        prompt = self._get_prompt(node, inputs)
        config = node.data.config or {}
        model_id = node.data.model or self.services['config'].DEFAULT_VEO_MODEL

        try:
            if node.type == "veo_standard":
                return await self._execute_standard(node, inputs, prompt, model_id, config, user_id)
            elif node.type == "veo_extend":
                return await self._execute_extend(node, inputs, prompt, model_id, config, user_id)
            elif node.type == "veo_reference":
                return await self._execute_reference(node, inputs, prompt, model_id, config, user_id)
        except Exception as e:
            self.logger.error(f"Veo Execution Failed ({node.type}): {e}")
            raise e

    def _get_prompt(self, node: Any, inputs: Dict[str, Any]) -> str:
        text_inputs = inputs.get("text", []) or inputs.get("input", [])
        return text_inputs[0] if text_inputs else node.data.value or ""

    async def _execute_standard(self, node: Any, inputs: Dict[str, Any], prompt: str, model_id: str, config: Dict, user_id: str):
        first_frames = inputs.get("first_frame", [])
        last_frames = inputs.get("last_frame", [])
        
        first_frame_info = extract_media_info(first_frames[0]) if first_frames else {"data": None, "mime_type": None}
        last_frame_info = extract_media_info(last_frames[0]) if last_frames else {"data": None, "mime_type": None}

        response = await self.services['veo'].generate_video_v31(
            model_id=model_id,
            prompt=prompt,
            first_frame=first_frame_info["data"],
            last_frame=last_frame_info["data"],
            config_params=config
        )
        return await self._process_response(response, prompt, model_id, config, user_id)

    async def _execute_extend(self, node: Any, inputs: Dict[str, Any], prompt: str, model_id: str, config: Dict, user_id: str):
        video_inputs = inputs.get("video", [])
        video_info = extract_media_info(video_inputs[0]) if video_inputs else {"data": None, "mime_type": None}
        
        next_video_inputs = inputs.get("next_video", [])
        next_video_info = extract_media_info(next_video_inputs[0]) if next_video_inputs else {"data": None, "mime_type": None}

        response = await self.services['veo'].extend_video_v31_preview(
            model_id=model_id,
            prompt=prompt,
            video_input=video_info["data"],
            video_mime_type=video_info["mime_type"],
            next_video_input=next_video_info["data"],
            next_video_mime_type=next_video_info["mime_type"],
            config_params=config
        )
        return await self._process_response(response, prompt, model_id, config, user_id)

    async def _execute_reference(self, node: Any, inputs: Dict[str, Any], prompt: str, model_id: str, config: Dict, user_id: str):
        image_inputs = inputs.get("image", [])
        reference_assets = []
        for val in image_inputs[:3]:
            info = extract_media_info(val)
            if info["data"]:
                reference_assets.append(info["data"])
        
        response = await self.services['veo'].generate_video_v31_preview(
            model_id=model_id,
            prompt=prompt,
            reference_assets=reference_assets,
            config_params=config
        )
        return await self._process_response(response, prompt, model_id, config, user_id)

    async def _process_response(self, response: Dict, prompt: str, model_id: str, config: Dict, user_id: str):
        if "videos" in response:
            for video in response["videos"]:
                # Save Asset
                if "data" in video:
                    asset = await asyncio.to_thread(
                        self.services['storage'].save_asset,
                        user_id=user_id,
                        content=base64.b64decode(video["data"]) if isinstance(video["data"], str) else video["data"],
                        asset_type="video",
                        mime_type=video["mime_type"],
                        prompt=prompt[:100],
                        model_id="veo-3.1"
                    )
                    video["storage_path"] = asset.storage_path if asset else None
                
                # Generate Proxy URL
                if "uri" in video:
                    local_rel_path = await asyncio.to_thread(
                        self.services['storage'].download_gcs_blob,
                        gcs_uri=video["uri"],
                        user_id=user_id
                    )
                    if local_rel_path:
                         video["url"] = f"/data/assets/{local_rel_path}"
                    else:
                        signed_url = self.services['vertex'].get_signed_url(video["uri"])
                        if signed_url:
                            video["url"] = signed_url
                    
                    if "storage_path" not in video:
                        video["storage_path"] = video["uri"]

        return response
