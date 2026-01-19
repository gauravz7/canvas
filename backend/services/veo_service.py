from google import genai
from google.genai import types
import os
import base64
import asyncio
from typing import List, Optional, Union, Dict, Any
from core.config import get_settings
from config import model_config
from .log_service import log_service
import logging
import uuid

logger = logging.getLogger(__name__)
settings = get_settings()

class VeoService:
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self._client_us = None
        self._client_global = None

    @property
    def client_us(self):
        if not self._client_us:
            self._client_us = genai.Client(
                vertexai=True,
                project=self.project_id,
                location="us-central1"
            )
        return self._client_us

    @property
    def client_global(self):
        if not self._client_global:
            self._client_global = genai.Client(
                vertexai=True,
                project=self.project_id,
                location="global"
            )
        return self._client_global

    def _normalize_media_input(self, media_input: Union[str, bytes], mime_type: str) -> types.Image:
        """Unified normalization for GCS URI and Local bytes for Veo inputs."""
        if isinstance(media_input, str) and media_input.startswith("gs://"):
            return types.Image(gcs_uri=media_input, mime_type=mime_type)
        elif isinstance(media_input, bytes):
            return types.Image(image_bytes=media_input, mime_type=mime_type)
        return None

    async def _poll_operation(self, client: genai.Client, operation):
        """Polls a long-running operation until completion."""
        # Extremely robust name extraction
        try:
            if hasattr(operation, 'name'):
                op_name = operation.name
            elif isinstance(operation, str):
                op_name = operation
            else:
                op_name = str(operation)
        except Exception as e:
            op_name = "unknown_operation"
            logger.error(f"Failed to get op_name: {e}")

        log_service.info(f"Start polling for operation: {op_name}", "VeoService")

        # Ensure we have an operation object for the while loop
        if not hasattr(operation, 'done'):
            try:
                operation = client.operations.get(types.GenerateVideosOperation(name=op_name))
            except Exception as e:
                log_service.error(f"Initial hydration failed for {op_name}: {e}", "VeoService")
                raise

        while True:
            try:
                if operation.done:
                    break
            except AttributeError:
                # Handle potential stale object state
                operation = client.operations.get(types.GenerateVideosOperation(name=op_name))
                if operation.done: break

            await asyncio.sleep(20)
            try:
                # Use fresh ref for every SDK call to ensure robustness
                op_ref = types.GenerateVideosOperation(name=op_name)
                refreshed = client.operations.get(op_ref)
                
                if hasattr(refreshed, 'done'):
                    operation = refreshed
                    log_service.info(f"Polled status for {op_name}: Done={operation.done}", "VeoService")
                else:
                     log_service.warning(f"Refreshed object missing 'done' attribute", "VeoService")

            except Exception as e:
                logger.warning(f"Polling error (retrying): {e}")
                log_service.warning(f"Polling error: {e}", "VeoService")
        
        if operation.result:
            return operation.result
        if operation.error:
            error_msg = None
            if isinstance(operation.error, dict):
                error_msg = operation.error.get('message')
            elif hasattr(operation.error, 'message'):
                error_msg = operation.error.message
            
            if not error_msg:
                error_msg = str(operation.error)
            raise Exception(f"Video Generation Failed: {error_msg}")
        return operation

    async def generate_video_v31(
        self,
        model_id: str,
        prompt: str,
        first_frame: Optional[Union[str, bytes]] = None,
        last_frame: Optional[Union[str, bytes]] = None,
        config_params: Dict[str, Any] = None
    ):
        """Standard/Fast Veo 3.1 generation (Text/Image-to-Video)."""
        config_params = config_params or {}
        
        output_uri = f"gs://{model_config.VEO_BUCKET}/veo_outputs/{uuid.uuid4()}"

        # Build config
        config = types.GenerateVideosConfig(
            duration_seconds=config_params.get("duration_seconds", 8),
            aspect_ratio=config_params.get("aspect_ratio", "16:9"),
            resolution=config_params.get("resolution", "720p"),
            generate_audio=config_params.get("generate_audio", False),
            negative_prompt=config_params.get("negative_prompt"),
            number_of_videos=config_params.get("sample_count", 1),
            outputGcsUri=output_uri
        )

        # Normalize images
        img_input = None
        if first_frame:
            img_input = self._normalize_media_input(first_frame, "image/jpeg")
        
        if last_frame:
            config.last_frame = self._normalize_media_input(last_frame, "image/jpeg")

        operation = self.client_global.models.generate_videos(
            model=model_id,
            prompt=prompt,
            image=img_input,
            config=config
        )
        # Robust name extraction for logging
        op_name = getattr(operation, 'name', str(operation))
        log_service.info(f"Started video generation: {model_id}. Operation: {op_name}", "VeoService")

        result = await self._poll_operation(self.client_global, operation)
        return self._format_response(result)

    async def generate_video_v31_preview(
        self,
        model_id: str,
        prompt: str,
        reference_assets: List[Union[str, bytes]],
        config_params: Dict[str, Any] = None
    ):
        """Veo 3.1 Preview (Subject-to-Video)."""
        config_params = config_params or {}
        
        # Build references
        reference_images = []
        for asset in reference_assets[:3]: # Max 3
            img = self._normalize_media_input(asset, "image/jpeg")
            if img:
                reference_images.append(
                    types.VideoGenerationReferenceImage(
                        image=img,
                        reference_type="asset" # Mandatory for Veo 3.1
                    )
                )
        
        output_uri = f"gs://{model_config.VEO_BUCKET}/veo_outputs/{uuid.uuid4()}"

        config = types.GenerateVideosConfig(
            reference_images=reference_images,
            duration_seconds=config_params.get("duration_seconds", 8),
            aspect_ratio=config_params.get("aspect_ratio", "16:9"),
            resolution=config_params.get("resolution", "720p"),
            generate_audio=config_params.get("generate_audio", False),
            number_of_videos=config_params.get("sample_count", 1),
            outputGcsUri=output_uri
        )

        try:
            operation = self.client_global.models.generate_videos(
                model=model_id,
                prompt=prompt,
                config=config
            )
        except Exception as e:
            log_service.error(f"Veo Preview Generation Failed: {str(e)}", "VeoService")
            raise e

        result = await self._poll_operation(self.client_global, operation)
        return self._format_response(result)

    async def extend_video_v31_preview(
        self,
        model_id: str,
        prompt: str,
        video_input: Union[str, bytes],
        video_mime_type: Optional[str] = None,
        next_video_input: Optional[Union[str, bytes]] = None,
        next_video_mime_type: Optional[str] = None,
        config_params: Dict[str, Any] = None
    ):
        """Veo 3.1 Preview Video Extension / Transition."""
        config_params = config_params or {}
        
        # Video input normalization
        video = None
        if isinstance(video_input, str) and video_input.startswith("gs://"):
            video = types.Video(uri=video_input, mime_type=video_mime_type)
        elif isinstance(video_input, bytes):
            video = types.Video(video_bytes=video_input, mime_type=video_mime_type)
        
        # Next video input normalization
        next_video = None
        if next_video_input:
            if isinstance(next_video_input, str) and next_video_input.startswith("gs://"):
                next_video = types.Video(uri=next_video_input, mime_type=next_video_mime_type)
            elif isinstance(next_video_input, bytes):
                next_video = types.Video(video_bytes=next_video_input, mime_type=next_video_mime_type)
        
        output_uri = f"gs://{model_config.VEO_BUCKET}/veo_outputs/{uuid.uuid4()}"

        config = types.GenerateVideosConfig(
            aspect_ratio=config_params.get("aspect_ratio", "16:9"),
            resolution=config_params.get("resolution", "720p"),
            duration_seconds=7, # Fixed 7s for extension
            generate_audio=config_params.get("generate_audio", False),
            outputGcsUri=output_uri
        )

        log_service.info(f"Video extension config: {config}", "VeoService")
        log_service.info(f"Input Video: {video}", "VeoService")
        log_service.info(f"Next Video (ignored for now): {next_video}", "VeoService")
        log_service.info(f"Output URI: {output_uri}", "VeoService")

        # The SDK seems to only support 'video' as a kwarg for generation. 
        # next_video (transitions) might be in a newer SDK or different method.
        operation = self.client_global.models.generate_videos(
            model=model_id,
            prompt=prompt,
            video=video,
            # next_video=next_video, # This was causing the crash
            config=config
        )

        result = await self._poll_operation(self.client_global, operation)
        return self._format_response(result)

    def _format_response(self, result: types.GenerateVideosResponse):
        """Extracts videos and returns as a list of dicts."""
        videos = []
        if result and result.generated_videos:
            for gv in result.generated_videos:
                video_data = {
                    "mime_type": gv.video.mime_type or "video/mp4"
                }
                if gv.video.uri:
                    video_data["uri"] = gv.video.uri
                if gv.video.video_bytes:
                    video_data["data"] = base64.b64encode(gv.video.video_bytes).decode('utf-8')
                videos.append(video_data)
        
        return {
            "videos": videos,
            "rai_filtered_count": result.rai_media_filtered_count if result else 0
        }

# Initialize singleton
veo_service = VeoService(project_id=settings.PROJECT_ID)
