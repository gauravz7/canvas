from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional, Union
from services.gemini_service import gemini_service
from services.veo_service import veo_service
from services.storage_service import storage_service
from services.vertex_service import vertex_service
from google import genai
from google.genai import types
from services.log_service import log_service
import asyncio
import os
from config import model_config
import base64
import json

router = APIRouter()

@router.post("/content")
async def generate_content(
    prompt: str = Form(""),
    model_id: str = Form(model_config.DEFAULT_GEMINI_IMAGE_MODEL),
    aspect_ratio: str = Form("1:1"),
    image_size: str = Form("1K"),
    candidate_count: int = Form(1),
    response_modalities: Optional[str] = Form(None), # comma separated e.g. "TEXT,IMAGE"
    thinking_level: str = Form("LOW"), # Added missing param
    media_resolution: str = Form("MEDIA_RESOLUTION_UNSPECIFIED"), # Added missing param
    gcs_uris: Optional[str] = Form(None), # comma separated GCS URIs
    files: List[UploadFile] = File(None),
    user_id: str = Form("default_user"),
    use_grounding: bool = Form(False)
):
    try:
        contents = [prompt]
        
        # Add GCS URIs if provided
        if gcs_uris:
            uris = [u.strip() for u in gcs_uris.split(",")]
            for uri in uris:
                if uri.startswith("gs://"):
                    # We need to determine mime type, or let the SDK handle it if possible.
                    # For simplicity, we assume image if uri is provided in image context
                    mime_type = "image/png" if ".png" in uri.lower() else "image/jpeg" # Default to common image types
                    contents.append(types.Part.from_uri(
                        file_uri=uri,
                        mime_type=mime_type
                    ))

        if files:
            for file in files:
                file_content = await file.read()
                
                # Save input file to history
                await asyncio.to_thread(
                    storage_service.save_asset,
                    user_id=user_id,
                    content=file_content,
                    asset_type="image", # Assume image for now, logic could be smarter based on content_type
                    mime_type=file.content_type,
                    prompt="Input Image for Generation",
                    model_id=model_id,
                    meta_data={"role": "input"}
                )
                
                contents.append(types.Part.from_bytes(
                    data=file_content,
                    mime_type=file.content_type
                ))

        modalities = None
        if response_modalities:
            modalities = [m.strip() for m in response_modalities.split(",")]
        
        image_config = None
        if aspect_ratio or image_size or candidate_count:
            image_config = {
                "aspect_ratio": aspect_ratio,
                "image_size": image_size,
                "candidate_count": candidate_count
            }

        result = gemini_service.generate_content(
            model=model_id,
            contents=contents,
            thinking_level=thinking_level,
            media_resolution=media_resolution,
            response_modalities=modalities,
            image_config=image_config,
            use_google_search=use_grounding
        )
        
        if result and "candidates" in result:
             for i, candidate in enumerate(result["candidates"]):
                 if "content" in candidate: # Just to be safe with structure
                      pass # logic is complicated for raw result, let's look at `images` key if present from service
        
        # gemini_service.generate_content returns a dict with 'text', 'images' etc.
        # We need to intercept this.
        
        
        # Actually `result` from gemini_service.generate_content is already formatted:
        # { "text": ..., "images": [...], "thoughts": ... }
        
        # user_id is already passed as argument, do NOT overwrite it.

        
        # Handle Images
        if "images" in result:
            for img in result["images"]:
                # img is {"mime_type": ..., "data": base64_str}
                asset = await asyncio.to_thread(
                    storage_service.save_asset,
                    user_id=user_id,
                    content=img["data"],
                    asset_type="image",
                    mime_type=img["mime_type"],
                    prompt=prompt,
                    model_id=model_id,
                    meta_data={"candidate_count": candidate_count, "aspect_ratio": aspect_ratio}
                )
                img["storage_path"] = asset.storage_path # Add path to response for UI
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/video")
async def generate_video(
    prompt: str = Form(...),
    model_id: str = Form(model_config.DEFAULT_VEO_MODEL),
    duration_seconds: Optional[int] = Form(8),
    aspect_ratio: Optional[str] = Form("16:9"),
    resolution: Optional[str] = Form("720p"),
    generate_audio: Optional[bool] = Form(False),
    negative_prompt: Optional[str] = Form(None),
    sample_count: Optional[int] = Form(1),
    first_frame_uri: Optional[str] = Form(None),
    last_frame_uri: Optional[str] = Form(None),
    video_uri: Optional[str] = Form(None),
    reference_uris: Optional[str] = Form(None), # comma separated GCS URIs
    first_frame_file: Optional[UploadFile] = File(None),
    last_frame_file: Optional[UploadFile] = File(None),
    video_file: Optional[UploadFile] = File(None),
    reference_files: Optional[List[UploadFile]] = File(None),
    user_id: str = Form("default_user")
):
    try:
        config_params = {
            "duration_seconds": duration_seconds,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "generate_audio": generate_audio,
            "negative_prompt": negative_prompt,
            "sample_count": sample_count
        }

        # Helper to get media content (GCS URI or Bytes)
        async def get_media(uri, upload_file, prompt_desc="Input Media"):
            if uri and uri.startswith("gs://"):
                # Guess mime type for GCS URI if possible, default to video/mp4 for video context
                mime_type = "video/mp4" if "video" in prompt_desc.lower() else "image/jpeg"
                return {"content": uri, "mime_type": mime_type}
            if upload_file:
                content = await upload_file.read()
                # Save input to history
                await asyncio.to_thread(
                    storage_service.save_asset,
                    user_id=user_id,
                    content=content,
                    asset_type="image" if "image" in upload_file.content_type else "video",
                    mime_type=upload_file.content_type,
                    prompt=f"{prompt_desc} for Video",
                    model_id=model_id,
                    meta_data={"role": "input"}
                )
                return {"content": content, "mime_type": upload_file.content_type}
            return None

        # Extract all potential media inputs
        video_input_data = await get_media(video_uri, video_file, "Input Video")
        first_input_data = await get_media(first_frame_uri, first_frame_file, "First Frame")
        last_input_data = await get_media(last_frame_uri, last_frame_file, "Last Frame")
        
        video_input = video_input_data["content"] if video_input_data else None
        video_mime_type = video_input_data["mime_type"] if video_input_data else None
        
        first = first_input_data["content"] if first_input_data else None
        last = last_input_data["content"] if last_input_data else None
        
        references = []
        if reference_uris:
            references.extend([u.strip() for u in reference_uris.split(",")])
        if reference_files:
            for f in reference_files:
                content = await f.read()
                await asyncio.to_thread(
                    storage_service.save_asset,
                    user_id=user_id,
                    content=content,
                    asset_type="image",
                    mime_type=f.content_type,
                    prompt="Reference Image for Video",
                    model_id=model_id,
                    meta_data={"role": "input"}
                )
                references.append(content)

        # Dispatch based on Input Type
        res = None
        
        # 1. Video Extension (Video Input Present)
        if video_input:
            if "preview" not in model_id.lower():
                 raise HTTPException(status_code=400, detail="Video extension requires a preview model (e.g. veo-3.1-generate-preview).")
            res = await veo_service.extend_video_v31_preview(
                model_id=model_id,
                prompt=prompt,
                video_input=video_input,
                video_mime_type=video_mime_type,
                config_params=config_params
            )

        # 2. Subject Reference (References Present)
        elif references:
            if "preview" not in model_id.lower():
                 raise HTTPException(status_code=400, detail="Subject reference requires a preview model.")
            res = await veo_service.generate_video_v31_preview(
                model_id=model_id,
                prompt=prompt,
                reference_assets=references,
                config_params=config_params
            )
            
        # 3. Standard Generation (Text-to-Video or Image-to-Video)
        else:
            # Works for both Preview and Standard models
            res = await veo_service.generate_video_v31(
                model_id=model_id,
                prompt=prompt,
                first_frame=first,
                last_frame=last,
                config_params=config_params
            )

        # Process Response (Save & URL Generation)
        if res and "videos" in res:
            for vid in res["videos"]:
                content = vid.get("uri") or vid.get("data")
                if content:
                    asset = await asyncio.to_thread(
                        storage_service.save_asset,
                        user_id=user_id,
                        content=content,
                        asset_type="video",
                        mime_type=vid.get("mime_type", "video/mp4"),
                        prompt=prompt,
                        model_id=model_id,
                        meta_data=config_params
                    )
                    vid["storage_path"] = asset.storage_path
                
                # Generate playable URL
                if vid.get("uri"):
                    local_rel_path = await asyncio.to_thread(
                        storage_service.download_gcs_blob,
                        gcs_uri=vid["uri"],
                        user_id=user_id
                    )
                    if local_rel_path:
                        vid["url"] = f"/data/assets/{local_rel_path}"
                    else:
                        signed_url = vertex_service.get_signed_url(vid["uri"])
                        if signed_url:
                            vid["url"] = signed_url
                            
        return res

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upscale")
async def upscale_image(
    file: UploadFile = File(...),
    upscale_factor: str = Form("x2"),
    user_id: str = Form("default_user")
):
    try:
        content = await file.read()
        
        # Save input image
        await asyncio.to_thread(
            storage_service.save_asset,
            user_id=user_id,
            content=content,
            asset_type="image",
            mime_type=file.content_type,
            prompt="Original Image for Upscaling",
            model_id="input-upload",
            meta_data={"role": "input"}
        )

        # Call Vertex Service for upscaling
        b64_upscaled = await vertex_service.upscale_image(content, upscale_factor)
        
        # Save the upscaled image as a new asset
        asset = await asyncio.to_thread(
            storage_service.save_asset,
            user_id=user_id,
            content=b64_upscaled,
            asset_type="image",
            mime_type="image/png",
            prompt=f"Upscaled image ({upscale_factor})",
            model_id=model_config.DEFAULT_UPSCALE_MODEL,
            meta_data={"upscale_factor": upscale_factor}
        )
        
        return {
            "status": "success",
            "image": {
                "mime_type": "image/png",
                "data": b64_upscaled,
                "storage_path": asset.storage_path
            }
        }
    except Exception as e:
        log_service.error(f"Upscale failed: {str(e)}", "Router")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/music")
async def generate_music(
    prompt: str = Form(...),
    negative_prompt: str = Form(""),
    seed: int = Form(12345),
    user_id: str = Form("default_user")
):
    try:
        prediction = await vertex_service.generate_music(prompt, negative_prompt, seed)
        audio_content = prediction.get("audioContent") or prediction.get("bytesBase64Encoded")
        
        if not audio_content:
            raise Exception(f"No audio content found in prediction: {prediction.keys()}")
            
        mime_type = prediction.get("mimeType", "audio/wav")
        
        # Save the generated music as an asset
        asset = await asyncio.to_thread(
            storage_service.save_asset,
            user_id=user_id,
            content=audio_content, # This is base64 string
            asset_type="audio",
            mime_type=mime_type,
            prompt=prompt,
            model_id=model_config.DEFAULT_MUSIC_MODEL,
            meta_data={"negative_prompt": negative_prompt, "seed": seed}
        )
        
        return {
            "status": "success",
            "audio": {
                "mime_type": mime_type,
                "data": audio_content,
                "storage_path": asset.storage_path
            }
        }
    except Exception as e:
        log_service.error(f"Music generation failed: {str(e)}", "Router")
        raise HTTPException(status_code=500, detail=str(e))
