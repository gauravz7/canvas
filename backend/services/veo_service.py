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

    async def upscale_video(
        self,
        video_gcs_uri: str,
        config_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        config_params = config_params or {}
        output_uri = f"gs://{model_config.VEO_BUCKET}/veo_upscale/{uuid.uuid4()}/"

        import google.auth
        import google.auth.transport.requests
        import httpx

        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        if not creds.valid:
            creds.refresh(auth_req)

        endpoint = (
            f"https://{self.location}-aiplatform.googleapis.com/v1/"
            f"projects/{self.project_id}/locations/{self.location}/"
            f"publishers/google/models/veo-3.1-generate-001:predictLongRunning"
        )

        payload = {
            "instances": [{
                "video": {
                    "gcsUri": video_gcs_uri,
                    "mimeType": "video/mp4"
                }
            }],
            "parameters": {
                "task": "upscale",
                "resolution": config_params.get("resolution", "4k"),
                "aspectRatio": config_params.get("aspect_ratio", "16:9"),
                "compressionQuality": config_params.get("compression_quality", "optimized"),
                "storageUri": output_uri,
                "sharpness": config_params.get("sharpness", 1)
            }
        }

        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json"
        }

        log_service.info(f"Video upscale request: {video_gcs_uri} -> {output_uri}", "VeoService")

        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, json=payload, headers=headers, timeout=120.0)
            if response.status_code != 200:
                raise Exception(f"Video Upscale API Error {response.status_code}: {response.text}")
            op_data = response.json()

        op_name = op_data.get("name")
        if not op_name:
            raise Exception(f"No operation name in upscale response: {op_data}")

        log_service.info(f"Upscale operation started: {op_name}", "VeoService")

        # Extract operation ID and build the correct polling URL
        # op_name format: projects/.../locations/.../publishers/.../models/.../operations/{op_id}
        # Poll URL should be: projects/.../locations/.../operations/{op_id}
        if "/publishers/" in op_name:
            parts = op_name.split("/")
            op_id = parts[-1]
            poll_path = f"projects/{self.project_id}/locations/{self.location}/operations/{op_id}"
        else:
            poll_path = op_name

        poll_endpoint = f"https://{self.location}-aiplatform.googleapis.com/v1/{poll_path}"
        log_service.info(f"Upscale poll endpoint: {poll_endpoint}", "VeoService")

        poll_data = {}
        max_polls = 60
        for poll_count in range(max_polls):
            await asyncio.sleep(20)
            if not creds.valid:
                creds.refresh(auth_req)
            poll_headers = {"Authorization": f"Bearer {creds.token}"}

            try:
                async with httpx.AsyncClient() as client:
                    poll_resp = await client.get(poll_endpoint, headers=poll_headers, timeout=60.0)

                if poll_resp.status_code != 200:
                    log_service.warning(f"Upscale poll HTTP {poll_resp.status_code}: {poll_resp.text[:200]}", "VeoService")
                    continue

                resp_text = poll_resp.text.strip()
                if not resp_text:
                    log_service.warning(f"Upscale poll returned empty response", "VeoService")
                    continue

                poll_data = poll_resp.json()
            except Exception as e:
                log_service.warning(f"Upscale poll error (retrying): {e}", "VeoService")
                continue

            if poll_data.get("done"):
                log_service.info(f"Upscale complete after {poll_count + 1} polls: {op_name}", "VeoService")
                break

            log_service.info(f"Upscale polling #{poll_count + 1}: {op_name} done={poll_data.get('done', False)}", "VeoService")
        else:
            raise Exception(f"Video upscale timed out after {max_polls} polls")

        if "error" in poll_data:
            raise Exception(f"Video upscale failed: {poll_data['error']}")

        response_data = poll_data.get("response", poll_data.get("metadata", {}))
        videos = []

        if "videos" in response_data:
            for vid in response_data["videos"]:
                video_entry = {"mime_type": "video/mp4"}
                if isinstance(vid, dict):
                    video_entry["uri"] = vid.get("gcsUri") or vid.get("uri", "")
                elif isinstance(vid, str):
                    video_entry["uri"] = vid
                videos.append(video_entry)

        if not videos:
            from google.cloud import storage as gcs_storage
            try:
                bucket_name = output_uri.replace("gs://", "").split("/")[0]
                prefix = "/".join(output_uri.replace("gs://", "").split("/")[1:])
                client = gcs_storage.Client()
                bucket = client.bucket(bucket_name)
                blobs = list(bucket.list_blobs(prefix=prefix))
                for blob in blobs:
                    if blob.name.endswith(('.mp4', '.webm')):
                        videos.append({"uri": f"gs://{bucket_name}/{blob.name}", "mime_type": "video/mp4"})
                log_service.info(f"Found {len(videos)} upscaled videos in {output_uri}", "VeoService")
            except Exception as e:
                log_service.error(f"Failed to list upscaled videos: {e}", "VeoService")
                videos = [{"uri": output_uri, "mime_type": "video/mp4"}]

        return {"videos": videos, "output_uri": output_uri}

# Initialize singleton
veo_service = VeoService(project_id=settings.PROJECT_ID)
