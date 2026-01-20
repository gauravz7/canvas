from .base import BaseNodeExecutor
import asyncio
import os
import subprocess
import json
import base64
import tempfile
from typing import Any, Dict, List
from datetime import datetime
import uuid

class EditorExecutor(BaseNodeExecutor):
    """
    Executor for the Editor node.
    Performs video concatenation and audio mixing using FFmpeg.
    """

    async def execute(self, node: Any, inputs: Dict[str, Any], user_id: str, context: Dict[str, Any] = None) -> Any:
        config = node.data.config or {}
        sequence = config.get("sequence", {"videos": [], "speech": [], "background": []})
        
        # 1. Resolve absolute paths for all inputs
        # We need a map of nodeId -> absolute_path
        media_map = {}
        
        # Helper to resolve an input value to a file path
        # Helper to resolve an input value to a file path
        def resolve_to_path(val):
            if not val: return None
            
            storage_path = None
            
            # 1. Direct storage_path check
            if isinstance(val, dict):
                storage_path = val.get("storage_path")
                
                # 2. Nested check (e.g. Veo results: {"videos": [{"storage_path": ...}]})
                if not storage_path:
                    for key in ["videos", "images", "audio"]:
                        if key in val and isinstance(val[key], list) and val[key]:
                            # Try the first item in the list
                            item = val[key][0]
                            if isinstance(item, dict):
                                storage_path = item.get("storage_path") or item.get("uri")
                                break
                            elif isinstance(item, str) and item.startswith("gs://"):
                                storage_path = item
                                break
                
                # If still no storage_path, but has 'url', it might be a relative path
                if not storage_path and "url" in val:
                    url = val["url"]
                    if url.startswith("/data/assets/"):
                        storage_path = url.replace("/data/assets/", "")

            # 3. Handle gs:// URIs (download if needed)
            if storage_path and storage_path.startswith("gs://"):
                try:
                    local_rel_path = self.services['storage'].download_gcs_blob(
                        gcs_uri=storage_path,
                        user_id=user_id
                    )
                    if local_rel_path:
                        # storage_service download puts it in assets_dir
                        abs_path = os.path.join(self.services['storage'].assets_dir, local_rel_path)
                        if os.path.exists(abs_path):
                            return abs_path
                except Exception as e:
                    self.logger.warning(f"Failed to download GCS blob {storage_path}: {e}")

            # 4. Resolve relative storage_path to absolute
            if storage_path and not storage_path.startswith("gs://"):
                base_dir = self.services['storage'].assets_dir
                abs_path = os.path.join(base_dir, storage_path)
                if os.path.exists(abs_path):
                    return abs_path
            
            # 5. Fallback: if it's raw data, write to a temp file
            data_info = self.services['engine']._extract_media_info(val)
            data = data_info.get("data")
            if data:
                # If it happens to be a gs:// URI extracted as data
                if isinstance(data, str) and data.startswith("gs://"):
                    # Recurse or handle here
                    return resolve_to_path({"storage_path": data})
                
                # Ensure we have bytes before writing to binary file
                if isinstance(data, str):
                    try:
                        # Try to see if it's base64 encoded string
                        if "," in data: data = data.split(",")[-1]
                        data = base64.b64decode(data)
                    except:
                        data = data.encode('utf-8')

                # Final byte check
                if not isinstance(data, bytes):
                    self.logger.warning(f"Data is not bytes even after processing: {type(data)}")
                    return None

                suffix = ".mp4" if "video" in data_info.get("mime_type", "") else ".mp3"
                if "wav" in data_info.get("mime_type", ""): suffix = ".wav"
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(data)
                    return tmp.name
                    
            return None

        # ... (rest of the gathering logic) ...
        if context is None:
            return {"error": "Execution context missing"}

        def get_path_for_node(node_id):
            result = context.get(node_id)
            if not result: return None
            return resolve_to_path(result)

        video_paths = []
        for v in sequence.get("videos", []):
            path = get_path_for_node(v["nodeId"])
            if path:
                video_paths.append({"path": path, "volume": v.get("volume", 100) / 100.0})

        speech_paths = []
        for s in sequence.get("speech", []):
            path = get_path_for_node(s["nodeId"])
            if path:
                speech_paths.append({"path": path, "volume": s.get("volume", 100) / 100.0})

        bg_paths = []
        for b in sequence.get("background", []):
            path = get_path_for_node(b["nodeId"])
            if path:
                bg_paths.append({"path": path, "volume": b.get("volume", 20) / 100.0})

        if not video_paths and not speech_paths and not bg_paths:
            return {"error": "No media inputs found"}

        # 2. FFmpeg Processing
        output_filename = f"edit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:4]}.mp4"
        output_path = os.path.join(self.services['storage'].assets_dir, user_id, "video", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            # Helper to get audio status and duration
            async def get_media_info(path):
                try:
                    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json", path]
                    proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, _ = await proc.communicate()
                    info = json.loads(stdout.decode())
                    has_a = any(s.get("codec_type") == "audio" for s in info.get("streams", []))
                    duration = float(info.get("format", {}).get("duration", 0))
                    return has_a, duration
                except Exception as e:
                    self.logger.warning(f"ffprobe failed for {path}: {e}")
                    return False, 0.0

            cmd = ["ffmpeg", "-y"]
            input_args = []
            filter_complex = []
            
            # Identify which segments have audio and their durations
            vid_info = []
            for v in video_paths:
                input_args.extend(["-i", v["path"]])
                info = await get_media_info(v["path"])
                vid_info.append(info)

            # Audio-only inputs (speech, bg)
            # (We already resolved paths, just need to add to input_args later)
            
            # Video processing
            for i, (v, (has_a, dur)) in enumerate(zip(video_paths, vid_info)):
                # Video stream: Scale and Pad
                filter_complex.append(f"[{i}:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v{i}]")
                
                # Audio stream: Use source if exists, otherwise generate silence
                if has_a:
                    filter_complex.append(f"[{i}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,volume={v['volume']}[va{i}]")
                else:
                    # Generate finite silence matching video duration
                    filter_complex.append(f"anullsrc=channel_layout=stereo:sample_rate=44100:d={dur},volume={v['volume']}[va{i}]")
            
            # Concatenate Normalized Videos
            if video_paths:
                if len(video_paths) > 1:
                    v_a_pads = "".join([f"[v{i}][va{i}]" for i in range(len(video_paths))])
                    filter_complex.append(f"{v_a_pads}concat=n={len(video_paths)}:v=1:a=1[vconcat][aconcat]")
                else:
                    # Single video optimization - but still need to map the processed streams
                    # Wait, if n=1 concat still works, but let's be explicit
                    filter_complex.append(f"[v0]copy[vconcat];[va0]acopy[aconcat]")
            
            # Speech inputs
            curr_idx = len(video_paths)
            speech_info = []
            for i, s in enumerate(speech_paths):
                input_args.extend(["-i", s["path"]])
                info = await get_media_info(s["path"])
                speech_info.append(info)
            
            for i, (s, (has_a, dur)) in enumerate(zip(speech_paths, speech_info)):
                idx = curr_idx + i
                if has_a:
                    filter_complex.append(f"[{idx}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,volume={s['volume']}[sa{i}]")
                else:
                    # This shouldn't really happen for speech/music nodes but let's be safe
                    filter_complex.append(f"anullsrc=channel_layout=stereo:sample_rate=44100:d={dur},volume={s['volume']}[sa{i}]")
            
            if speech_paths:
                if len(speech_paths) > 1:
                    sa_inputs = "".join([f"[sa{i}]" for i in range(len(speech_paths))])
                    filter_complex.append(f"{sa_inputs}concat=n={len(speech_paths)}:v=0:a=1[sconcat]")
                else:
                    filter_complex.append(f"[sa0]acopy[sconcat]")
            
            # Background inputs
            curr_idx = len(video_paths) + len(speech_paths)
            for i, b in enumerate(bg_paths):
                input_args.extend(["-i", b["path"]])
                # We assume background tracks have audio, but still resample
                filter_complex.append(f"[{curr_idx + i}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,volume={b['volume']}[ba{i}]")
            
            # FINAL MIX
            mix_inputs = []
            if video_paths: mix_inputs.append("[aconcat]")
            if speech_paths: mix_inputs.append("[sconcat]")
            if bg_paths: 
                # Concat BG tracks if multiple
                if len(bg_paths) > 1:
                    ba_inputs = "".join([f"[ba{i}]" for i in range(len(bg_paths))])
                    filter_complex.append(f"{ba_inputs}concat=n={len(bg_paths)}:v=0:a=1[baconcat]")
                    mix_inputs.append("[baconcat]")
                else:
                    mix_inputs.append("[ba0]")
            
            if len(mix_inputs) > 1:
                filter_complex.append(f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:duration=longest[afinal]")
            elif len(mix_inputs) == 1:
                filter_complex.append(f"{mix_inputs[0]}acopy[afinal]")
            
            cmd.extend(input_args)
            if filter_complex:
                # Note: if using anullsrc, we might need -shortest on the video part or specific duration
                # but anullsrc with :d=DURATION is better. 
                # For simplicity, we use the amix duration=longest and hope for the best.
                cmd.extend(["-filter_complex", ";".join(filter_complex)])
            
            if video_paths:
                cmd.extend(["-map", "[vconcat]"])
                if mix_inputs:
                    cmd.extend(["-map", "[afinal]"])
                else:
                    cmd.extend(["-map", "[aconcat]"])
            else:
                cmd.extend(["-map", "[afinal]"])

            cmd.extend(["-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-shortest", output_path])
            
            # Run FFmpeg
            self.logger.info(f"Running FFmpeg: {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"FFmpeg failed: {stderr.decode()}")
                return {"error": f"FFmpeg failed: {stderr.decode()[:1000]}"}

            # Return Asset Info
            storage_path = os.path.join(user_id, "video", output_filename)
            asset = await asyncio.to_thread(
                self.services['storage'].save_asset,
                user_id=user_id,
                content=open(output_path, "rb").read(),
                asset_type="video",
                mime_type="video/mp4",
                prompt="Edited Video Sequence",
                model_id="ffmpeg-editor"
            )

            return {
                "videos": [{
                    "url": f"/data/assets/{storage_path}",
                    "storage_path": storage_path,
                    "mime_type": "video/mp4"
                }]
            }

        except Exception as e:
            self.logger.error(f"Editor execution failed: {e}")
            return {"error": str(e)}
        finally:
            # Cleanup temp files if any (TODO)
            pass
