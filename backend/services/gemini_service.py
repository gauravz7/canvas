from google import genai
from google.genai import types
import os
import base64
from typing import List, Optional, Union
import io

class GeminiService:
    def __init__(self, project_id: str, location: str = "global"):
        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )

    def generate_content(
        self,
        model: str,
        contents: list,
        thinking_level: str = "HIGH",
        media_resolution: str = None,
        response_modalities: list = None,
        image_config: dict = None,
        use_google_search: bool = False
    ):
        """Generates content using the google-genai SDK."""
        # Refine modalities: Many models don't support TEXT+IMAGE output simultaneously
        if not response_modalities:
            if "image" in model.lower():
                response_modalities = ["IMAGE"]
            else:
                response_modalities = ["TEXT"]
        elif "TEXT" in response_modalities and "IMAGE" in response_modalities:
            # Most modern Gemini models (2.0+) support interleaved text and image output.
            # We allow both if requested. Specialized logic for older models can be added if needed.
            pass

        config = types.GenerateContentConfig()
        
        if use_google_search:
            config.tools = [types.Tool(google_search=types.GoogleSearch())]

        if thinking_level and "thinking" in model.lower():
            config.thinking_config = types.ThinkingConfig(include_thoughts=True)

        if thinking_level:
            # Note: actual thinking level control might vary by model version,
            # but we pass it as a hint if the SDK supports it in future or use it for routing logic
            pass

        if media_resolution:
            # media_resolution is typically for video/image processing inputs
            # but can be used as a hint in config if supported
            pass

        if response_modalities:
            config.response_modalities = response_modalities

        # Handle multiple candidates sequentially if needed (as some models/modalities don't support batching)
        target_count = image_config.get("candidate_count", 1) if image_config else 1
        
        if image_config:
            config.image_config = types.ImageConfig(
                aspect_ratio=image_config.get("aspect_ratio"),
                image_size=image_config.get("image_size")
            )

        if target_count > 1 and "image" in model.lower():
            all_results = []
            # Remove candidate_count from config for individual calls if needed, 
            # though usually it's better to just loop if we know it fails.
            config.candidate_count = 1 
            for _ in range(target_count):
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=contents,
                        config=config
                    )
                    # Parse the single candidate
                    if not response.candidates:
                         continue
                         
                    candidate = response.candidates[0]
                    text_output = ""
                    thoughts = ""
                    images = []
                    
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.text:
                                if part.thought:
                                    thoughts += part.text + "\n"
                                else:
                                    text_output += part.text
                            if part.inline_data:
                                images.append({
                                    "mime_type": part.inline_data.mime_type,
                                    "data": base64.b64encode(part.inline_data.data).decode('utf-8')
                                })
                    
                    grounding_metadata = None
                    if candidate.grounding_metadata:
                         grounding_metadata = candidate.grounding_metadata.dict()

                    all_results.append({
                        "text": text_output,
                        "thoughts": thoughts,
                        "images": images,
                        "grounding_metadata": grounding_metadata
                    })
                except Exception as inner_e:
                    print(f"[DEBUG] Individual candidate call failed: {inner_e}")
                    pass 
            
            print(f"[DEBUG] Multimodal results collected: {len(all_results)}")
            if not all_results:
                return {"text": "", "thoughts": "", "images": [], "grounding_metadata": None}
            return all_results if len(all_results) > 1 else all_results[0]

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )

            # Parse response candidates
            results = []
            if response.candidates:
                print(f"[DEBUG] Found {len(response.candidates)} candidates")
                for candidate in response.candidates:
                    text_output = ""
                    thoughts = ""
                    images = []
                    
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.text:
                                if part.thought:
                                    thoughts += part.text + "\n"
                                else:
                                    text_output += part.text
                            if part.inline_data:
                                images.append({
                                    "mime_type": part.inline_data.mime_type,
                                    "data": base64.b64encode(part.inline_data.data).decode('utf-8')
                                })
                    
                    grounding_metadata = None
                    if candidate.grounding_metadata:
                        try:
                            grounding_metadata = candidate.grounding_metadata.model_dump()
                        except:
                            try:
                                grounding_metadata = candidate.grounding_metadata.dict()
                            except:
                                grounding_metadata = str(candidate.grounding_metadata)

                    results.append({
                        "text": text_output,
                        "thoughts": thoughts,
                        "images": images,
                        "grounding_metadata": grounding_metadata
                    })
            else:
                print("[DEBUG] No candidates found in response")

            if not results:
                return {"text": "", "thoughts": "", "images": [], "grounding_metadata": None}
            return results[0] if len(results) == 1 else results
        except Exception as e:
            raise Exception(f"Gemini Generation Error: {str(e)}")

# Initialize singleton
from core.config import get_settings
settings = get_settings()
gemini_service = GeminiService(project_id=settings.PROJECT_ID)
