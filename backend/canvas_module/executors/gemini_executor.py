from .base import BaseNodeExecutor
from google.genai import types
import asyncio
from typing import Any, Dict, List, Union

class GeminiExecutor(BaseNodeExecutor):
    """Executor for Gemini Text and Image nodes."""

    async def execute(self, node: Any, inputs: Dict[str, Any], user_id: str, context: Dict[str, Any] = None) -> Any:
        try:
            prompt_base = node.data.value or ""
            contents = self._prepare_contents(inputs, prompt_base)
            
            if not contents and not prompt_base:
                return "" if "text" in node.type else {"images": []}

            model = node.data.model or self.services['config'].DEFAULT_GEMINI_IMAGE_MODEL
            
            if "text" in node.type:
                return await self._execute_text(node, model, contents)
            else:
                return await self._execute_image(node, model, contents, prompt_base, user_id)

        except Exception as e:
            self.logger.error(f"Gemini execution failed: {e}")
            raise e

    def _prepare_contents(self, inputs: Dict[str, Any], prompt_base: str) -> List[Any]:
        contents = []
        import base64

        def _parse_part(val: Any) -> Any:
            """Helper to parse a single input value into a Part or text string."""
            if not val:
                return None
            
            # Handle Direct Dictionary (e.g. from Speech Node directly)
            if isinstance(val, dict):
                # Check for wrapped audio/video/image keys
                if "audio" in val:
                    return _parse_part(val["audio"])
                if "video" in val:
                    return _parse_part(val["video"])
                if "image" in val:
                    return _parse_part(val["image"])
                if "images" in val and isinstance(val["images"], list):
                     # Flatten list of images if found?
                     # For now, just take the first or return multiple? 
                     # This helper returns one Part. We might need logic change if 1->Many.
                     pass 

                # Check for GCS URI ("storage_path", "uri", "gcs_uri")
                uri = val.get("storage_path") or val.get("uri") or val.get("gcs_uri")
                if uri and isinstance(uri, str) and uri.startswith("gs://"):
                     return types.Part.from_uri(
                         uri=uri,
                         mime_type=val.get("mime_type", "application/octet-stream")
                     )

                # Check for "data" + "mime_type" signature
                if "data" in val and "mime_type" in val:
                    try:
                        b64_data = val["data"]
                        if not b64_data: # If empty/None, skip
                            return None
                            
                        # Strip prefix if present (though usually backend keeps it raw)
                        if isinstance(b64_data, str) and "base64," in b64_data:
                            b64_data = b64_data.split("base64,")[1]
                        
                        return types.Part.from_data(
                            data=base64.b64decode(b64_data),
                            mime_type=val["mime_type"]
                        )
                    except Exception as e:
                        self.logger.warning(f"Failed to decode media part: {e}")
                        return None
                
                # Fallback: check for explicit text
                if "text" in val:
                    return str(val["text"])
            
            # Handle String (Text)
            if isinstance(val, (str, int, float)):
                return str(val)
                
            return None

        # Aggregate inputs from all relevant handles
        # "input" is generic, "text", "audio", "video", "image" are specific
        all_inputs = []
        all_inputs.extend(inputs.get("input", []))
        all_inputs.extend(inputs.get("text", []))
        all_inputs.extend(inputs.get("audio", []))
        all_inputs.extend(inputs.get("video", []))
        all_inputs.extend(inputs.get("image", []))

        # Process all inputs
        for val in all_inputs:
             part = _parse_part(val)
             if part:
                 contents.append(part)

        if prompt_base:
             contents.insert(0, prompt_base)
             
        return contents

    async def _execute_text(self, node: Any, model: str, contents: List[Any]) -> str:
        config = node.data.config or {}
        use_google_search = config.get("use_google_search", False)
        
        response = await asyncio.to_thread(
            self.services['gemini'].generate_content,
            model=model,
            contents=contents,
            use_google_search=use_google_search,
            response_modalities=["TEXT"]
        ) or {}
        
        if isinstance(response, dict):
            return response.get("text", "")
        return str(response)

    async def _execute_image(self, node: Any, model: str, contents: List[Any], prompt: str, user_id: str) -> Dict[str, Any]:
        config = node.data.config or {}
        aspect_ratio = config.get("aspect_ratio", "1:1")
        
        response = await asyncio.to_thread(
            self.services['gemini'].generate_content,
            model=model,
            contents=contents,
            image_config={"candidate_count": 1, "aspect_ratio": aspect_ratio},
            response_modalities=["IMAGE"]
        ) or {}

        # Save images
        if "images" in response:
            for img in response["images"]:
                asset = await asyncio.to_thread(
                    self.services['storage'].save_asset,
                    user_id=user_id,
                    content=img["data"],
                    asset_type="image",
                    mime_type=img["mime_type"],
                    prompt=prompt,
                    model_id=model
                )
                img["storage_path"] = asset.storage_path
        
        return {"images": response.get("images", [])}
