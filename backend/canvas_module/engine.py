import asyncio
from typing import Dict, Any, List, Set, Union, Optional
from .schemas import Workflow, Node, NodeType, ExecutionResult
from services.gemini_service import gemini_service
from services.storage_service import storage_service
from services.vertex_service import vertex_service
from services.veo_service import veo_service
from config import model_config
import logging
import base64
import re
import json
from google.genai import types
from sqlalchemy.orm import Session
from models import Workflow as WorkflowModel
import hashlib
import copy
from .executors.editor_executor import EditorExecutor

class ExecutionCache:
    _instance = None
    _cache = {} # Dict[str, Any] where key is hash(node_id + inputs_hash + config_hash)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExecutionCache, cls).__new__(cls)
            cls._instance._cache = {}
        return cls._instance

    def get(self, key: str) -> Any:
        return self._cache.get(key)

    def set(self, key: str, value: Any):
        self._cache[key] = value

    def clear(self):
        self._cache = {}


logger = logging.getLogger(__name__)

class WorkflowEngine:
    def __init__(self):
        self.cache = ExecutionCache()
        self.services = {
            'gemini': gemini_service,
            'veo': veo_service,
            'vertex': vertex_service,
            'storage': storage_service,
            'engine': self
        }
        self.executors = {
            'editor': EditorExecutor(self.services)
        }
        self.active_tasks: Dict[str, asyncio.Task] = {}

    def _compute_cache_key(self, node: Node, inputs: Dict[str, Any]) -> str:
        """Computes a stable hash for cache key based on node config and resolved inputs."""
        try:
            # 1. Config Hash
            config_str = json.dumps(node.data.config or {}, sort_keys=True)
            
            # 2. Inputs Hash
            # We need to stabilize inputs. If they are complex objects, we might need special handling.
            # implementing a simple recursive serializer for hashable representation
            def stable_repr(obj):
                if isinstance(obj, dict):
                    return json.dumps({k: stable_repr(v) for k, v in sorted(obj.items())}, sort_keys=True)
                if isinstance(obj, list):
                    return json.dumps([stable_repr(x) for x in obj], sort_keys=True)
                return str(obj)

            inputs_str = stable_repr(inputs)
            
            # 3. Model/Value Hash
            core_data = f"{node.type}:{node.data.model}:{node.data.value}"
            
            raw_key = f"{node.id}:{core_data}:{config_str}:{inputs_str}"
            return hashlib.sha256(raw_key.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to compute cache key for {node.id}: {e}")
            return None


    def _parse_input(self, val: Any) -> Union[str, types.Part]:
        """
        Parses input value. If it's a data URL (image, video, audio), converts to types.Part.
        Otherwise returns string representation.
        """
        if isinstance(val, str) and val.strip().startswith("data:"):
            # Format: data:[<mediatype>][;base64],<data>
            match = re.match(r'data:([^;]+);base64,(.+)', val)
            if match:
                mime_type = match.group(1)
                b64_data = match.group(2)
                try:
                    # use inline_data with types.Blob for multimodal inputs
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

    def _extract_media_bytes(self, val: Any) -> Optional[bytes]:
        """
        Robustly extracts raw bytes from various input formats:
        - bytes directly
        - base64 data URLs (string)
        - dict with "data" (and "mime_type")
        - dict with "images", "videos", or "audio" lists (extracts first item)
        """
        if val is None:
            return None
            
        # 1. Handle bytes
        if isinstance(val, bytes):
            return val
            
        # 2. Handle data URLs
        if isinstance(val, str) and val.strip().startswith("data:"):
            match = re.match(r'data:([^;]+);base64,(.+)', val)
            if match:
                try:
                    return base64.b64decode(match.group(2))
                except Exception as e:
                    logger.warning(f"Failed to decode base64 from string: {e}")
                    return None
        
        # 3. Handle dictionaries
        if isinstance(val, dict):
            # Check for direct "data" key
            if "data" in val:
                try:
                    data = val["data"]
                    return base64.b64decode(data) if isinstance(data, str) else data
                except Exception as e:
                    logger.warning(f"Failed to extract direct data from dict: {e}")
            
            # Check for lists: "images", "videos", "audio"
            for key in ["images", "videos", "audio"]:
                if key in val and isinstance(val[key], list) and val[key]:
                    # Recurse on the first item
                    return self._extract_media_bytes(val[key][0])
                    
        return None

    def _extract_media_info(self, val: Any) -> Dict[str, Any]:
        """Extracts media bytes and mime_type from various input formats."""
        if val is None:
            return {"data": None, "mime_type": None}
            
        # Handle dict with "data" and "mime_type"
        if isinstance(val, dict):
            if "data" in val:
                data = val["data"]
                bytes_data = base64.b64decode(data) if isinstance(data, str) else data
                return {"data": bytes_data, "mime_type": val.get("mime_type")}
            
            # Check for direct uri/url if no data
            if "uri" in val:
                return {"data": val["uri"], "mime_type": val.get("mime_type")}
            if "url" in val:
                # If it's a local proxy URL, we might want to return the storage_path if we can, 
                # but veo_service is better with gs:// or local bytes.
                # However, if we only have the URL, it might be better than nothing.
                pass

            # Recurse for nested "images", "videos", "audio" lists or dicts
            for key in ["images", "videos", "audio"]:
                if key in val and val[key]:
                    if isinstance(val[key], list):
                        return self._extract_media_info(val[key][0])
                    elif isinstance(val[key], dict):
                        return self._extract_media_info(val[key])
                    
        # Fallback to _extract_media_bytes for other formats (bytes, data URL)
        bytes_data = self._extract_media_bytes(val)
        mime_type = None
        if isinstance(val, str) and val.strip().startswith("data:"):
            match = re.match(r'data:([^;]+);base64,(.+)', val)
            if match:
                mime_type = match.group(1)
        
        return {"data": bytes_data, "mime_type": mime_type}

    async def stream_workflow_execution(self, workflow: Workflow, node_ids: List[str] = None, user_id: str = "default", db: Session = None, use_cache: bool = False, execution_id: str = None):
        """
        Streams execution events for the workflow.
        Yields JSON strings formatted as SSE data.
        """
        if execution_id:
            # Register current task
            self.active_tasks[execution_id] = asyncio.current_task()
            logger.info(f"[KILL] Task registered: {execution_id}")

        try:
            context: Dict[str, Any] = {}
            
            # 1. Build Dependency Graph
            deps: Dict[str, List[str]] = {node.id: [] for node in workflow.nodes}
            for edge in workflow.edges:
                if edge.target in deps:
                    deps[edge.target].append(edge.source)
            
            # 2. Determine Nodes to Execute
            if node_ids:
                node_map = {node.id: node for node in workflow.nodes}
                nodes_to_run = [node_map[nid] for nid in node_ids if nid in node_map]
            else:
                nodes_to_run = self._topological_sort(workflow.nodes, deps)

            # 3. Execute Nodes
            for node in nodes_to_run:
                try:
                    # Signal node start
                    yield f"data: {json.dumps({'type': 'node_started', 'node_id': node.id})}\n\n"
                    
                    # Resolve Inputs
                    inputs = self._resolve_inputs(node, workflow.edges, context)
                    
                    # Execute Node Logic
                    output = await self._execute_node(node, inputs, user_id, db, context=context, use_cache=use_cache)
                    
                    # Store Output
                    context[node.id] = output
                    
                    # Signal node completion
                    res = ExecutionResult(node_id=node.id, status="completed", output=output)
                    yield f"data: {json.dumps({'type': 'node_completed', 'node_id': node.id, 'result': res.model_dump()})}\n\n"
                    
                except asyncio.CancelledError:
                    logger.info(f"[KILL] Execution {execution_id} was cancelled during node {node.id}.")
                    yield f"data: {json.dumps({'type': 'execution_cancelled', 'execution_id': execution_id})}\n\n"
                    raise
                except Exception as e:
                    logger.error(f"Error executing node {node.id}: {e}")
                    res = ExecutionResult(node_id=node.id, status="failed", output=None, error=str(e))
                    yield f"data: {json.dumps({'type': 'node_failed', 'node_id': node.id, 'result': res.model_dump()})}\n\n"
            
            yield f"data: {json.dumps({'type': 'workflow_completed'})}\n\n"
        finally:
            if execution_id and execution_id in self.active_tasks:
                del self.active_tasks[execution_id]
                logger.info(f"[KILL] Task cleaned up: {execution_id}")

    async def execute_workflow(self, workflow: Workflow, node_ids: List[str] = None, user_id: str = "default", db: Session = None, depth: int = 0, use_cache: bool = False) -> Dict[str, ExecutionResult]:
        """
        Executes the workflow.
        If node_ids is provided, only executes those nodes.
        """
        if depth > 10:
            raise Exception("Max workflow recursion depth (10) reached.")
            
        execution_results: Dict[str, ExecutionResult] = {}
        context: Dict[str, Any] = {} # Store potential outputs here by node_id

        # 1. Build Dependency Graph
        # Map: Target Node -> [Source Nodes]
        deps: Dict[str, List[str]] = {node.id: [] for node in workflow.nodes}
        for edge in workflow.edges:
            if edge.target in deps:
                deps[edge.target].append(edge.source)
        
        # 2. Determine Nodes to Execute
        nodes_to_run = []
        if node_ids:
            # Validate IDs
            node_map = {node.id: node for node in workflow.nodes}
            nodes_to_run = [node_map[nid] for nid in node_ids if nid in node_map]
            
            # Pre-populate context with existing outputs from nodes NOT in this run
            # This allows partial execution to use upstream data
            for node in workflow.nodes:
                if node.id not in node_ids and node.data.executionResult:
                    # executionResult is likely a dict from the frontend JSON
                    if isinstance(node.data.executionResult, dict) and 'output' in node.data.executionResult:
                         context[node.id] = node.data.executionResult['output']
                         logger.info(f"[FLOW] Loaded existing context for {node.id}")
        else:
            # Topological Sort for full execution
            # Simple approach: Khan's algorithm or just layered execution
            # Given we have the deps, let's do a simple topological sort
            nodes_to_run = self._topological_sort(workflow.nodes, deps)

        # 3. Execute Nodes
        # For MVP, we run sequentially in topo order. Parallel execution can be added later using asyncio.gather for independent nodes.
        for node in nodes_to_run:
            try:
                # Resolve Inputs
                inputs = self._resolve_inputs(node, workflow.edges, context)
                
                # Execute Node Logic
                output = await self._execute_node(node, inputs, user_id, db, depth, context=context, use_cache=use_cache)
                
                # Store Output
                context[node.id] = output
                execution_results[node.id] = ExecutionResult(
                    node_id=node.id,
                    status="completed",
                    output=output
                )
            except Exception as e:
                logger.error(f"Error executing node {node.id}: {e}")
                execution_results[node.id] = ExecutionResult(
                    node_id=node.id,
                    status="failed",
                    output=None,
                    error=str(e)
                )
                # If a node fails, dependent nodes might fail too. 
                # For now, we continue, but downstream might fail due to missing context.
        
        return execution_results

    def cancel_execution(self, execution_id: str):
        """Cancels an active execution task."""
        if execution_id in self.active_tasks:
            task = self.active_tasks[execution_id]
            task.cancel()
            logger.info(f"[KILL] Cancel requested for: {execution_id}")
            return True
        logger.warning(f"[KILL] Cancellation failed: Execution {execution_id} not found.")
        return False

    def _topological_sort(self, nodes: List[Node], deps: Dict[str, List[str]]) -> List[Node]:
        """
        Returns a list of nodes in topological order.
        """
        # Calculate in-degree
        in_degree = {node.id: 0 for node in nodes}
        for u in deps:
            for v in deps:
                if u in deps[v]: # u is a dependency of v
                     in_degree[v] += 1
        
        # Actually deps is Target -> Sources (so Sources are dependencies)
        # So in_degree of v is len(deps[v])
        in_degree = {node.id: len(deps[node.id]) for node in nodes}
        
        queue = [node for node in nodes if in_degree[node.id] == 0]
        sorted_nodes = []
        
        while queue:
            u = queue.pop(0)
            sorted_nodes.append(u)
            
            # Find nodes v where u is a dependency (i.e. u -> v)
            # We need the alignment: deps[v] contains u
            for v_node in nodes:
                if u.id in deps[v_node.id]:
                    in_degree[v_node.id] -= 1
                    if in_degree[v_node.id] == 0:
                        queue.append(v_node)
        
        if len(sorted_nodes) != len(nodes):
            # Graph has cycle or disconnected parts? 
            # Disconnected parts are handled by queue init. Cycle is the problem.
            # Fallback to original order or just return what we have
             pass
        
        return sorted_nodes

    def _flatten(self, val: Any) -> List[Any]:
        """Recursively flattens a list of inputs."""
        if not isinstance(val, list):
            return [val]
        flat_list = []
        for item in val:
            flat_list.extend(self._flatten(item))
        return flat_list

    def _resolve_inputs(self, node: Node, edges: List[Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolves input values for the node from connected edges and context.
        Aggregates multiple connections to the same handle into a flattened list.
        """
        inputs = {}
        
        # Find edges connected to this node's inputs
        target_edges = [e for e in edges if e.target == node.id]
        
        for edge in target_edges:
            source_id = edge.source
            if source_id in context:
                key = edge.targetHandle or "input"
                val = context[source_id]
                
                if key not in inputs:
                    inputs[key] = []
                
                # Flatten the value (it might be a list from a previous node's multi-output)
                # Check for sourceHandle extraction
                if edge.sourceHandle and isinstance(val, dict) and edge.sourceHandle in val:
                    val = val[edge.sourceHandle]
                
                flat_val = self._flatten(val)
                inputs[key].extend(flat_val)
                logger.info(f"[FLOW] Shared data from {source_id} to {node.id} on handle {key} ({len(flat_val)} items)")
        
        return inputs

    async def _execute_node(self, node: Node, inputs: Dict[str, Any], user_id: str, db: Session = None, depth: int = 0, context: Dict[str, Any] = None, use_cache: bool = False) -> Any:
        # 0. Check Cache
        cache_key = None
        if use_cache:
            cache_key = self._compute_cache_key(node, inputs)
            if cache_key:
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    logger.info(f"[CACHE HIT] Node {node.id}")
                    return cached_result
        
        result = await self._execute_node_logic(node, inputs, user_id, db, depth, context)
        
        # Cache Result
        if use_cache and cache_key and result is not None:
             # Verify result is serializable/cacheable? In-memory is fine for objects.
             self.cache.set(cache_key, result)
             
        return result

    async def _execute_node_logic(self, node: Node, inputs: Dict[str, Any], user_id: str, db: Session = None, depth: int = 0, context: Dict[str, Any] = None) -> Any:

        # 1. INPUT Node
        if node.type == NodeType.INPUT:
            return node.data.value

        # 2. GEMINI TEXT & IMAGE Nodes (Unified logic for multimodal inputs)
        if node.type in [NodeType.GEMINI_TEXT, NodeType.GEMINI_IMAGE]:
            prompt_base = node.data.value or ""
            contents = []
            
            # Aggregate inputs based on handles
            # We explicitly look for 'text' and 'image' handles
            text_inputs = inputs.get("text", [])
            image_inputs = inputs.get("image", [])
            other_inputs = inputs.get("other", [])
            
            # Legacy/default handle support
            if not text_inputs and not image_inputs:
                text_inputs = inputs.get("input", [])

            # Process text inputs
            for val in text_inputs:
                if isinstance(val, dict):
                    if "text" in val:
                        contents.append(val["text"])
                    else:
                        # Fallback: Check if this dict contains media (User might have connected Audio->Text input)
                        media_info = self._extract_media_info(val)
                        if media_info["data"] and media_info["mime_type"]:
                             logger.info(f"[GEMINI] Found media in 'text' input: {media_info['mime_type']}")
                             if isinstance(media_info["data"], str) and media_info["data"].startswith("gs://"):
                                 contents.append(types.Part.from_uri(
                                     file_uri=media_info["data"],
                                     mime_type=media_info["mime_type"]
                                 ))
                             else:
                                 contents.append(types.Part(
                                     inline_data=types.Blob(
                                         data=media_info["data"],
                                         mime_type=media_info["mime_type"]
                                     )
                                 ))
                elif isinstance(val, str):
                    contents.append(val)
                elif val is not None and not isinstance(val, (list, dict)):
                    contents.append(str(val))
            
            # Process image inputs
            for val in image_inputs:
                if isinstance(val, dict) and "images" in val:
                    for img in val["images"]:
                        contents.append(self._parse_input(f"data:{img['mime_type']};base64,{img['data']}"))
                elif isinstance(val, dict) and "data" in val and "mime_type" in val:
                    # Handle single image dict directly
                    contents.append(self._parse_input(f"data:{val['mime_type']};base64,{val['data']}"))
                else:
                    parsed = self._parse_input(val)
                    if parsed and not isinstance(parsed, str): # It's a types.Part for image/video/etc
                        contents.append(parsed)
                    elif isinstance(val, str) and val.startswith("data:"):
                         contents.append(parsed) 
            
            # Process 'other' inputs (video, audio, docs, or generic files)
            for val in other_inputs:
                logger.info(f"[GEMINI] Processing 'other' input: {str(val)[:100]}...")
                # 1. Try to extract media (audio/video/image)
                media_info = self._extract_media_info(val)
                logger.info(f"[GEMINI] Extracted media info: mime={media_info.get('mime_type')}, data_type={type(media_info.get('data'))}")
                
                if media_info["data"] and media_info["mime_type"]:
                     # Check if data is a GCS URI
                     if isinstance(media_info["data"], str) and media_info["data"].startswith("gs://"):
                         logger.info(f"[GEMINI] Using GCS URI for input: {media_info['data']}")
                         contents.append(types.Part.from_uri(
                             file_uri=media_info["data"],
                             mime_type=media_info["mime_type"]
                         ))
                     else:
                         # Created types.Part with inline data
                         logger.info(f"[GEMINI] Using Inline Data for input (size={len(media_info['data']) if isinstance(media_info['data'], (bytes, str)) else 'unknown'})")
                         contents.append(types.Part(
                             inline_data=types.Blob(
                                 data=media_info["data"],
                                 mime_type=media_info["mime_type"]
                             )
                         ))
                     continue

                # 2. Fallback to existing logic if no media detected
                parsed = self._parse_input(val)
                # If it's a dict containing 'text', we treat it as text
                if isinstance(val, dict) and "text" in val:
                    contents.append(val["text"])
                # If it's a dict containing 'images' we skip for 'other' (should use image handle)
                # otherwise we append the parsed types.Part
                elif not isinstance(parsed, str):
                    contents.append(parsed)
                elif isinstance(val, str):
                    contents.append(parsed)

            if prompt_base:
                # If prompt_base contains {{input}}, we only replace if we have text inputs? 
                # Simpler: just insert it at the beginning.
                contents.insert(0, prompt_base)

            if not contents and not prompt_base:
                 return "" if node.type == NodeType.GEMINI_TEXT else {"images": []}

            # Config & Execution
            config = node.data.config or {}
            model = node.data.model
            
            if node.type == NodeType.GEMINI_TEXT:
                model = model or model_config.DEFAULT_GEMINI_TEXT_MODEL
                use_google_search = config.get("use_google_search", False)
                include_thoughts = config.get("include_thoughts", True)
                
                response = await asyncio.to_thread(
                    gemini_service.generate_content,
                    model=model,
                    contents=contents,
                    use_google_search=use_google_search,
                    thinking_level="HIGH" if include_thoughts else None,
                    response_modalities=["TEXT"] # Force text for text node
                ) or {}
                # Ensure output is a direct STRING for GEMINI_TEXT node 
                # (to avoid downstream JSON dumps)
                if isinstance(response, dict):
                    return response.get("text", "")
                elif isinstance(response, list) and response:
                    return response[0].get("text", "")
                return str(response) if response else ""
                
            else: # NodeType.GEMINI_IMAGE
                model = model or model_config.DEFAULT_GEMINI_IMAGE_MODEL
                aspect_ratio = config.get("aspect_ratio", "1:1")
                
                response = await asyncio.to_thread(
                    gemini_service.generate_content,
                    model=model,
                    contents=contents,
                    image_config={"candidate_count": 1, "aspect_ratio": aspect_ratio},
                    response_modalities=["IMAGE"] # Request IMAGE only as requested
                ) or {}
                
                # Save generated images
                if "images" in response:
                    for img in response["images"]:
                        asset = await asyncio.to_thread(
                            storage_service.save_asset,
                            user_id=user_id,
                            content=img["data"],
                            asset_type="image",
                            mime_type=img["mime_type"],
                            prompt=prompt_base,
                            model_id=model
                        )
                        img["storage_path"] = asset.storage_path
                
                # Ensure output is ONLY images for GEMINI_IMAGE node
                return {"images": response.get("images", []) if isinstance(response, dict) else []}

        # 3. IMAGEN UPSCALE Node
        if node.type == NodeType.IMAGEN_UPSCALE:
            image_inputs = inputs.get("image", []) or inputs.get("input", [])
            
            # Find the first image to upscale
            image_to_upscale = None
            for val in image_inputs:
                extracted = self._extract_media_bytes(val)
                if extracted:
                    image_to_upscale = extracted
                    break
            
            if not image_to_upscale:
                return {"error": "No image found to upscale"}
            
            config = node.data.config or {}
            upscale_factor = config.get("upscale_factor", "x2")
            
            # Call VertexService
            
            upscaled_b64 = await vertex_service.upscale_image(
                image_bytes=image_to_upscale,
                upscale_factor=upscale_factor
            )
            
            # Save to storage
            asset = await asyncio.to_thread(
                storage_service.save_asset,
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

        # 4. SPEECH GEN Node
        if node.type == NodeType.SPEECH_GEN:
            text_inputs = inputs.get("text", []) or inputs.get("input", [])
            prompt = text_inputs[0] if text_inputs else node.data.value or ""
            
            if not prompt:
                return {"error": "No text input for speech generation"}
            
            config = node.data.config or {}
            # Robust fallback for model_id and voice_name
            model_id = config.get("model_id") or "gemini-2.5-flash-tts"
            voice_name = config.get("voice_name") or "Kore"
            
            # Construct payload for Journey/Gemini voices
            payload = {
                "input": {"text": prompt},
                "voice": {
                    "languageCode": "en-US",
                    "name": voice_name,
                    "model_name": model_id
                },
                "audioConfig": {"audioEncoding": "LINEAR16"}
            }
            # Remove model_name if None (sanity check)
            if not payload["voice"]["model_name"]:
                del payload["voice"]["model_name"]
            
            logger.info(f"[TTS] Generating speech with voice={voice_name}, model={model_id}")

            # Call VertexService
            b64_audio = await vertex_service.synthesize_raw(payload)

            audio_content = base64.b64decode(b64_audio)
            
            # Save to storage
            asset = await asyncio.to_thread(
                storage_service.save_asset,
                user_id=user_id,
                content=audio_content,
                asset_type="audio",
                mime_type="audio/wav",
                prompt=prompt[:100],
                model_id=model_id,
                meta_data={"voice_name": voice_name}
            )
            
            return {
                "audio": {
                    "data": b64_audio,
                    "mime_type": "audio/wav",
                    "storage_path": asset.storage_path
                }
            }

        # 5. LYRIA GEN Node
        if node.type == NodeType.LYRIA_GEN:
            text_inputs = inputs.get("text", []) or inputs.get("input", [])
            prompt = text_inputs[0] if text_inputs else node.data.value or ""
            
            if not prompt:
                return {"error": "No prompt for music generation"}
            
            # Call VertexService
            result = await vertex_service.generate_music(prompt=prompt)
            b64_audio = result.get("audioContent")
            audio_content = base64.b64decode(b64_audio)
            
            # Save to storage
            asset = await asyncio.to_thread(
                storage_service.save_asset,
                user_id=user_id,
                content=audio_content,
                asset_type="audio",
                mime_type="audio/mp3",
                prompt=prompt[:100],
                model_id="lyria-002"
            )
            
            return {
                "audio": {
                    "data": b64_audio,
                    "mime_type": "audio/mp3",
                    "storage_path": asset.storage_path
                }
            }

        # 6. VEO Nodes
        if node.type in [NodeType.VEO_STANDARD, NodeType.VEO_EXTEND, NodeType.VEO_REFERENCE]:
            text_inputs = inputs.get("text", []) or inputs.get("input", [])
            prompt = text_inputs[0] if text_inputs else node.data.value or ""
            
            config = node.data.config or {}
            
            if node.type == NodeType.VEO_STANDARD:
                first_frames = inputs.get("first_frame", [])
                last_frames = inputs.get("last_frame", [])
                
                first_frame_info = self._extract_media_info(first_frames[0]) if first_frames else {"data": None, "mime_type": None}
                last_frame_info = self._extract_media_info(last_frames[0]) if last_frames else {"data": None, "mime_type": None}

                response = await veo_service.generate_video_v31(
                    model_id=node.data.model or model_config.DEFAULT_VEO_MODEL,
                    prompt=prompt,
                    first_frame=first_frame_info["data"],
                    last_frame=last_frame_info["data"],
                    config_params=config
                )
            
            elif node.type == NodeType.VEO_EXTEND:
                video_inputs = inputs.get("video", [])
                video_info = self._extract_media_info(video_inputs[0]) if video_inputs else {"data": None, "mime_type": None}
                
                next_video_inputs = inputs.get("next_video", [])
                next_video_info = self._extract_media_info(next_video_inputs[0]) if next_video_inputs else {"data": None, "mime_type": None}

                response = await veo_service.extend_video_v31_preview(
                    model_id=node.data.model or model_config.DEFAULT_VEO_MODEL,
                    prompt=prompt,
                    video_input=video_info["data"],
                    video_mime_type=video_info["mime_type"],
                    next_video_input=next_video_info["data"],
                    next_video_mime_type=next_video_info["mime_type"],
                    config_params=config
                )
            
            elif node.type == NodeType.VEO_REFERENCE:
                image_inputs = inputs.get("image", [])
                reference_assets = []
                for val in image_inputs[:3]:
                    info = self._extract_media_info(val)
                    if info["data"]:
                        reference_assets.append(info["data"])
                
                response = await veo_service.generate_video_v31_preview(
                    model_id=node.data.model or model_config.DEFAULT_VEO_MODEL,
                    prompt=prompt,
                    reference_assets=reference_assets,
                    config_params=config
                )

            # Save generated videos and sign URIs
            if "videos" in response:
                for video in response["videos"]:
                    if "data" in video:
                        asset = await asyncio.to_thread(
                            storage_service.save_asset,
                            user_id=user_id,
                            content=base64.b64decode(video["data"]) if isinstance(video["data"], str) else video["data"],
                            asset_type="video",
                            mime_type=video["mime_type"],
                            prompt=prompt[:100],
                            model_id="veo-3.1"
                        )
                        video["storage_path"] = asset.storage_path if asset else None
                    
                    if "uri" in video:
                        # 1. Download locally for reliable proxying
                        local_rel_path = await asyncio.to_thread(
                            storage_service.download_gcs_blob,
                            gcs_uri=video["uri"],
                            user_id=user_id
                        )
                        
                        if local_rel_path:
                            # Set the proxy URL for the frontend
                            # The frontend expects /data/assets/... but storage_service returns user_id/...
                            # Wait, storage_service and engine.py have different expectations of relative path.
                            # In storage_service.save_asset, relative_path is user_id/asset_type/filename.
                            # The FastAPI server mounts /data to the 'data' directory.
                            # So the full path is /data/assets/{user_id}/{type}/{filename}
                            video["url"] = f"/data/assets/{local_rel_path}"
                            logger.info(f"Local proxy URL for video: {video['url']}")
                        else:
                            # Fallback to signed URL if download fails
                            signed_url = vertex_service.get_signed_url(video["uri"])
                            if signed_url:
                                video["url"] = signed_url
                        
                        # Also save it as a reference asset if not already saved
                        if "storage_path" not in video:
                            video["storage_path"] = video["uri"]
            
            return response

        # 7. OUTPUT Node
        if node.type == NodeType.OUTPUT:
             # If multiple inputs, just return the first one or a list?
             # React Flow usually connects 1 source to 1 target per handle, 
             # but we support multiple sources to same handle.
             res_list = inputs.get("input", [])
             return res_list[0] if res_list else None

        # 8. WORKFLOW Node (Nested)
        if node.type == NodeType.WORKFLOW:
            if not node.data.workflow_id:
                return {"error": "No workflow ID specified"}
            
            if not db:
                 return {"error": "Database session not available for nested workflow"}

            # Fetch workflow
            wf_model = db.query(WorkflowModel).filter(WorkflowModel.id == node.data.workflow_id).first()
            if not wf_model:
                return {"error": f"Workflow {node.data.workflow_id} not found"}
            
            # Parse into Schema
            try:
                nested_workflow = Workflow(**wf_model.data)
            except Exception as e:
                return {"error": f"Invalid nested workflow data: {e}"}
            
            # Prepare Inputs (Inject into nested INPUT node)
            # The inputs dict here is keyed by 'targetHandle', which for WorkflowNode corresponds to the nested INPUT node's ID.
            for n in nested_workflow.nodes:
                if n.type == NodeType.INPUT:
                    # Check if we have input for this specific node ID
                    if n.id in inputs:
                        raw_vals = inputs[n.id]
                        # Input nodes usually take a single value in 'value'
                        if raw_vals:
                            n.data.value = raw_vals[0]
                    # Fallback: check 'input' key if no specific ID match (legacy behavior or default handle)
                    elif "input" in inputs and not n.data.value:
                         raw_vals = inputs["input"]
                         if raw_vals:
                             n.data.value = raw_vals[0]

            # Execute Recursively
            results = await self.execute_workflow(nested_workflow, user_id=user_id, db=db, depth=depth+1)
            
            # Collect Outputs from nested OUTPUT node
            output_nodes = [n for n in nested_workflow.nodes if n.type == NodeType.OUTPUT]
            final_output = {}
            
            for out_node in output_nodes:
                 if out_node.id in results and results[out_node.id].status == "completed":
                      # Key the output by the OUTPUT node's ID
                      # This allows the parent to extract it via sourceHandle (which will match this ID)
                      final_output[out_node.id] = results[out_node.id].output
            
            return final_output

        # 9. EDITOR Node
        if node.type == NodeType.EDITOR:
            return await self.executors['editor'].execute(node, inputs, user_id, context)

        return None

        return None
