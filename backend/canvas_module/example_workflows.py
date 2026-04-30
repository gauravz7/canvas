import uuid

def generate_id():
    return str(uuid.uuid4())


# ============================================================================
# 1. Product Ad (16:9) — Full video pipeline
# Customizable scaffold: empty inputs, structured pipeline
# Inputs: Product Photo + Brand Brief + Visual Style
# Outputs: Hero image (4K) + Final ad video with voice + music
# ============================================================================
PRODUCT_AD_WORKFLOW = {
    "id": "template-product-ad",
    "name": "Product Ad (16:9)",
    "nodes": [
        {
            "id": "product-photo",
            "type": "input",
            "position": {"x": 100, "y": 200},
            "data": {"label": "Product Photo", "type": "input", "inputType": "image", "value": ""}
        },
        {
            "id": "brand-brief",
            "type": "input",
            "position": {"x": 100, "y": 480},
            "data": {"label": "Brand Brief", "type": "input", "inputType": "text", "value": ""}
        },
        {
            "id": "visual-style",
            "type": "input",
            "position": {"x": 100, "y": 730},
            "data": {"label": "Visual Style", "type": "input", "inputType": "text", "value": ""}
        },
        {
            "id": "stylize-image",
            "type": "gemini_image",
            "position": {"x": 470, "y": 350},
            "data": {
                "label": "Stylize Product",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "16:9"},
                "value": "Create a professional product hero shot using the product photo, the brand brief, and the visual style. Photorealistic, premium quality, cinematic 16:9 widescreen."
            }
        },
        {
            "id": "image-upscale",
            "type": "imagen_upscale",
            "position": {"x": 850, "y": 100},
            "data": {"label": "Upscale Hero Image", "type": "imagen_upscale"}
        },
        {
            "id": "image-output",
            "type": "output",
            "position": {"x": 1200, "y": 100},
            "data": {"label": "Hero Image (4K)", "type": "output", "outputType": "image"}
        },
        {
            "id": "veo-animate",
            "type": "veo_standard",
            "position": {"x": 850, "y": 380},
            "data": {
                "label": "Animate Product",
                "type": "veo_standard",
                "model": "veo-3.1-lite-generate-001",
                "config": {
                    "aspect_ratio": "16:9",
                    "duration_seconds": 8,
                    "generate_audio": False
                },
                "value": "Cinematic product showcase. Smooth camera movement around the product. Subtle motion in the scene."
            }
        },
        {
            "id": "veo-upscale",
            "type": "veo_upscale",
            "position": {"x": 1200, "y": 380},
            "data": {
                "label": "Upscale to 4K",
                "type": "veo_upscale",
                "config": {"resolution": "4k", "aspect_ratio": "16:9", "sharpness": 2}
            }
        },
        {
            "id": "voice-gen",
            "type": "speech_gen",
            "position": {"x": 470, "y": 750},
            "data": {
                "label": "Voiceover",
                "type": "speech_gen",
                "config": {"model_id": "gemini-3.1-flash-tts-preview", "voice_name": "Charon", "language": "en"}
            }
        },
        {
            "id": "music-gen",
            "type": "lyria_clip",
            "position": {"x": 470, "y": 1020},
            "data": {
                "label": "Background Music",
                "type": "lyria_clip",
                "config": {"model_id": "lyria-3-clip-preview"}
            }
        },
        {
            "id": "ad-editor",
            "type": "editor",
            "position": {"x": 1550, "y": 600},
            "data": {
                "label": "Final Ad",
                "type": "editor",
                "config": {
                    "sequence": {
                        "videos": [{"nodeId": "veo-upscale", "volume": 0, "label": "4K Product Video"}],
                        "speech": [{"nodeId": "voice-gen", "volume": 100, "label": "Voiceover"}],
                        "background": [{"nodeId": "music-gen", "volume": 25, "label": "BG Music"}]
                    }
                }
            }
        },
        {
            "id": "final-output",
            "type": "output",
            "position": {"x": 1950, "y": 600},
            "data": {"label": "Final Ad Video", "type": "output", "outputType": "video"}
        }
    ],
    "edges": [
        {"id": "e1", "source": "product-photo", "target": "stylize-image", "sourceHandle": "output", "targetHandle": "image"},
        {"id": "e2", "source": "brand-brief", "target": "stylize-image", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e3", "source": "visual-style", "target": "stylize-image", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e4", "source": "stylize-image", "target": "image-upscale", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "e5", "source": "image-upscale", "target": "image-output", "sourceHandle": "image", "targetHandle": "input"},
        {"id": "e6", "source": "stylize-image", "target": "veo-animate", "sourceHandle": "image", "targetHandle": "first_frame"},
        {"id": "e7", "source": "brand-brief", "target": "veo-animate", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e8", "source": "veo-animate", "target": "veo-upscale", "sourceHandle": "video", "targetHandle": "video"},
        {"id": "e9", "source": "brand-brief", "target": "voice-gen", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e10", "source": "brand-brief", "target": "music-gen", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e11", "source": "veo-upscale", "target": "ad-editor", "sourceHandle": "video", "targetHandle": "videos"},
        {"id": "e12", "source": "voice-gen", "target": "ad-editor", "sourceHandle": "audio", "targetHandle": "speech"},
        {"id": "e13", "source": "music-gen", "target": "ad-editor", "sourceHandle": "audio", "targetHandle": "background"},
        {"id": "e14", "source": "ad-editor", "target": "final-output", "sourceHandle": "video", "targetHandle": "input"}
    ]
}


# ============================================================================
# 2. Cinema Shot with Character — 3 Cuts (16:9)
# Same scene, 3 framing variations using shared character reference
# ============================================================================
CINEMA_SHOT_WORKFLOW = {
    "id": "template-cinema-shot",
    "name": "Cinema Shot — 3 Cuts (16:9)",
    "nodes": [
        {
            "id": "character-input",
            "type": "input",
            "position": {"x": 100, "y": 200},
            "data": {"label": "Character (photo OR description)", "type": "input", "inputType": "image", "value": ""}
        },
        {
            "id": "character-desc",
            "type": "input",
            "position": {"x": 100, "y": 460},
            "data": {"label": "Character Description (if no photo)", "type": "input", "inputType": "text", "value": ""}
        },
        {
            "id": "scene-setting",
            "type": "input",
            "position": {"x": 100, "y": 710},
            "data": {"label": "Scene Setting", "type": "input", "inputType": "text", "value": ""}
        },
        {
            "id": "character-ref",
            "type": "gemini_image",
            "position": {"x": 470, "y": 350},
            "data": {
                "label": "Character Reference",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "16:9"},
                "value": "Cinematic full body portrait of the character in the scene setting. Professional movie still, dramatic lighting, photorealistic. This will serve as the character reference for all subsequent shots."
            }
        },
        {
            "id": "shot-wide",
            "type": "gemini_image",
            "position": {"x": 870, "y": 80},
            "data": {
                "label": "Shot 1: Wide Establishing",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "16:9"},
                "value": "WIDE ESTABLISHING SHOT. Show the same character from far away, atmospheric composition. Match character identity exactly. Same scene, same lighting, same time of day."
            }
        },
        {
            "id": "shot-medium",
            "type": "gemini_image",
            "position": {"x": 870, "y": 380},
            "data": {
                "label": "Shot 2: Medium Tracking",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "16:9"},
                "value": "MEDIUM TRACKING SHOT. The same character, side profile, walking through the scene. Match character identity exactly. Same scene, same lighting, same time of day."
            }
        },
        {
            "id": "shot-closeup",
            "type": "gemini_image",
            "position": {"x": 870, "y": 680},
            "data": {
                "label": "Shot 3: Dramatic Close-up",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "16:9"},
                "value": "DRAMATIC CLOSE-UP. The same character's face, intense expression, rim lighting. Match character identity exactly. Same scene, same lighting, same time of day."
            }
        },
        {
            "id": "video-wide",
            "type": "veo_standard",
            "position": {"x": 1280, "y": 80},
            "data": {
                "label": "Animate Wide Shot",
                "type": "veo_standard",
                "model": "veo-3.1-lite-generate-001",
                "config": {"aspect_ratio": "16:9", "duration_seconds": 8, "generate_audio": False},
                "value": "Slow camera push in. Atmospheric, cinematic motion. Subtle environmental movement."
            }
        },
        {
            "id": "video-medium",
            "type": "veo_standard",
            "position": {"x": 1280, "y": 380},
            "data": {
                "label": "Animate Medium Shot",
                "type": "veo_standard",
                "model": "veo-3.1-lite-generate-001",
                "config": {"aspect_ratio": "16:9", "duration_seconds": 8, "generate_audio": False},
                "value": "Smooth side-tracking shot. Character walks at steady pace. Subtle motion."
            }
        },
        {
            "id": "video-closeup",
            "type": "veo_standard",
            "position": {"x": 1280, "y": 680},
            "data": {
                "label": "Animate Close-up",
                "type": "veo_standard",
                "model": "veo-3.1-lite-generate-001",
                "config": {"aspect_ratio": "16:9", "duration_seconds": 8, "generate_audio": False},
                "value": "Slow zoom into character's face. Subtle micro-expression. Eyes shift focus."
            }
        },
        {
            "id": "cinema-score",
            "type": "lyria_pro",
            "position": {"x": 1280, "y": 980},
            "data": {
                "label": "Cinematic Score",
                "type": "lyria_pro",
                "config": {"model_id": "lyria-3-pro-preview"}
            }
        },
        {
            "id": "cinema-editor",
            "type": "editor",
            "position": {"x": 1700, "y": 380},
            "data": {
                "label": "Cinematic Sequence",
                "type": "editor",
                "config": {
                    "sequence": {
                        "videos": [
                            {"nodeId": "video-wide", "volume": 0, "label": "Wide"},
                            {"nodeId": "video-medium", "volume": 0, "label": "Medium"},
                            {"nodeId": "video-closeup", "volume": 0, "label": "Close-up"}
                        ],
                        "background": [
                            {"nodeId": "cinema-score", "volume": 80, "label": "Score"}
                        ]
                    }
                }
            }
        },
        {
            "id": "cinema-output",
            "type": "output",
            "position": {"x": 2100, "y": 380},
            "data": {"label": "Cinema Sequence", "type": "output", "outputType": "video"}
        }
    ],
    "edges": [
        {"id": "ec1", "source": "character-input", "target": "character-ref", "sourceHandle": "output", "targetHandle": "image"},
        {"id": "ec2", "source": "character-desc", "target": "character-ref", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ec3", "source": "scene-setting", "target": "character-ref", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ec4", "source": "character-ref", "target": "shot-wide", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "ec5", "source": "scene-setting", "target": "shot-wide", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ec6", "source": "character-ref", "target": "shot-medium", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "ec7", "source": "scene-setting", "target": "shot-medium", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ec8", "source": "character-ref", "target": "shot-closeup", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "ec9", "source": "scene-setting", "target": "shot-closeup", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ec10", "source": "shot-wide", "target": "video-wide", "sourceHandle": "image", "targetHandle": "first_frame"},
        {"id": "ec11", "source": "shot-medium", "target": "video-medium", "sourceHandle": "image", "targetHandle": "first_frame"},
        {"id": "ec12", "source": "shot-closeup", "target": "video-closeup", "sourceHandle": "image", "targetHandle": "first_frame"},
        {"id": "ec13", "source": "scene-setting", "target": "cinema-score", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ec14", "source": "character-ref", "target": "cinema-score", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "ec15", "source": "video-wide", "target": "cinema-editor", "sourceHandle": "video", "targetHandle": "videos"},
        {"id": "ec16", "source": "video-medium", "target": "cinema-editor", "sourceHandle": "video", "targetHandle": "videos"},
        {"id": "ec17", "source": "video-closeup", "target": "cinema-editor", "sourceHandle": "video", "targetHandle": "videos"},
        {"id": "ec18", "source": "cinema-score", "target": "cinema-editor", "sourceHandle": "audio", "targetHandle": "background"},
        {"id": "ec19", "source": "cinema-editor", "target": "cinema-output", "sourceHandle": "video", "targetHandle": "input"}
    ]
}


# ============================================================================
# 3. Virtual Try-On (16:9) — Full pipeline with motion video
# Order fix: VTO first (preserves face+garment), then background swap, then animate
# ============================================================================
VTO_WORKFLOW = {
    "id": "template-vto",
    "name": "Virtual Try-On (16:9)",
    "nodes": [
        {
            "id": "person-photo",
            "type": "input",
            "position": {"x": 100, "y": 100},
            "data": {"label": "Person Photo", "type": "input", "inputType": "image", "value": ""}
        },
        {
            "id": "garment-photo",
            "type": "input",
            "position": {"x": 100, "y": 400},
            "data": {"label": "Garment Photo", "type": "input", "inputType": "image", "value": ""}
        },
        {
            "id": "background-prompt",
            "type": "input",
            "position": {"x": 100, "y": 700},
            "data": {"label": "Background Description", "type": "input", "inputType": "text", "value": ""}
        },
        {
            "id": "motion-prompt",
            "type": "input",
            "position": {"x": 100, "y": 950},
            "data": {"label": "Motion Direction", "type": "input", "inputType": "text", "value": ""}
        },
        {
            "id": "vto-apply",
            "type": "gemini_image",
            "position": {"x": 470, "y": 200},
            "data": {
                "label": "Virtual Try-On",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "16:9"},
                "value": "Take the person from the first image and dress them in the garment from the second image. Maintain the person's identity (face, body, pose). The garment should fit naturally with realistic fabric drape, lighting, and shadows. Photorealistic, cinematic 16:9 widescreen."
            }
        },
        {
            "id": "background-swap",
            "type": "gemini_image",
            "position": {"x": 870, "y": 350},
            "data": {
                "label": "Replace Background",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "16:9"},
                "value": "Take the person and outfit from the input image. Place them in the new background described in the text. Keep the person's identity, garment, and pose identical. Match the lighting of the new background. Photorealistic 16:9 widescreen."
            }
        },
        {
            "id": "image-output",
            "type": "output",
            "position": {"x": 1280, "y": 100},
            "data": {"label": "Final VTO Image", "type": "output", "outputType": "image"}
        },
        {
            "id": "vto-animate",
            "type": "veo_standard",
            "position": {"x": 1280, "y": 400},
            "data": {
                "label": "Animate Person",
                "type": "veo_standard",
                "model": "veo-3.1-lite-generate-001",
                "config": {"aspect_ratio": "16:9", "duration_seconds": 8, "generate_audio": False}
            }
        },
        {
            "id": "video-upscale",
            "type": "veo_upscale",
            "position": {"x": 1640, "y": 400},
            "data": {
                "label": "Upscale to 4K",
                "type": "veo_upscale",
                "config": {"resolution": "4k", "aspect_ratio": "16:9", "sharpness": 2}
            }
        },
        {
            "id": "fashion-music",
            "type": "lyria_clip",
            "position": {"x": 870, "y": 750},
            "data": {
                "label": "Fashion Soundtrack",
                "type": "lyria_clip",
                "config": {"model_id": "lyria-3-clip-preview"}
            }
        },
        {
            "id": "vto-editor",
            "type": "editor",
            "position": {"x": 1990, "y": 500},
            "data": {
                "label": "Fashion Reel",
                "type": "editor",
                "config": {
                    "sequence": {
                        "videos": [{"nodeId": "video-upscale", "volume": 0, "label": "VTO Video"}],
                        "background": [{"nodeId": "fashion-music", "volume": 100, "label": "Music"}]
                    }
                }
            }
        },
        {
            "id": "final-reel",
            "type": "output",
            "position": {"x": 2390, "y": 500},
            "data": {"label": "Final Fashion Reel", "type": "output", "outputType": "video"}
        }
    ],
    "edges": [
        {"id": "ev1", "source": "person-photo", "target": "vto-apply", "sourceHandle": "output", "targetHandle": "image"},
        {"id": "ev2", "source": "garment-photo", "target": "vto-apply", "sourceHandle": "output", "targetHandle": "image"},
        {"id": "ev3", "source": "vto-apply", "target": "background-swap", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "ev4", "source": "background-prompt", "target": "background-swap", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ev5", "source": "background-swap", "target": "image-output", "sourceHandle": "image", "targetHandle": "input"},
        {"id": "ev6", "source": "background-swap", "target": "vto-animate", "sourceHandle": "image", "targetHandle": "first_frame"},
        {"id": "ev7", "source": "motion-prompt", "target": "vto-animate", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ev8", "source": "vto-animate", "target": "video-upscale", "sourceHandle": "video", "targetHandle": "video"},
        {"id": "ev9", "source": "background-prompt", "target": "fashion-music", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ev10", "source": "video-upscale", "target": "vto-editor", "sourceHandle": "video", "targetHandle": "videos"},
        {"id": "ev11", "source": "fashion-music", "target": "vto-editor", "sourceHandle": "audio", "targetHandle": "background"},
        {"id": "ev12", "source": "vto-editor", "target": "final-reel", "sourceHandle": "video", "targetHandle": "input"}
    ]
}


# ============================================================================
# Legacy templates (kept for backward compat)
# ============================================================================

INFLUENCER_VIDEO_WORKFLOW = {
    "id": "template-influencer",
    "name": "Influencer Video (16:9)",
    "nodes": [
        {"id": "script-input", "type": "input", "position": {"x": 100, "y": 100},
         "data": {"label": "Video Script", "type": "input", "inputType": "text", "value": ""}},
        {"id": "refine-script", "type": "gemini_text", "position": {"x": 400, "y": 100},
         "data": {"label": "Refine Script", "type": "gemini_text", "model": "gemini-3.1-flash-lite-preview"}},
        {"id": "speech-node", "type": "speech_gen", "position": {"x": 700, "y": 100},
         "data": {"label": "Narration", "type": "speech_gen"}},
        {"id": "music-node", "type": "lyria_clip", "position": {"x": 700, "y": 300},
         "data": {"label": "Background Music", "type": "lyria_clip"}},
        {"id": "visuals-node", "type": "veo_standard", "position": {"x": 700, "y": 500},
         "data": {"label": "B-Roll Visuals", "type": "veo_standard", "model": "veo-3.1-lite-generate-001",
                  "config": {"aspect_ratio": "16:9"}}},
        {"id": "refine-script-visuals", "type": "gemini_text", "position": {"x": 400, "y": 500},
         "data": {"label": "Visual Prompts", "type": "gemini_text", "model": "gemini-3.1-flash-lite-preview"}},
        {"id": "final-editor", "type": "editor", "position": {"x": 1000, "y": 300},
         "data": {"label": "Influencer Video Edit", "type": "editor",
                  "config": {"sequence": {
                      "videos": [{"nodeId": "visuals-node", "volume": 100, "label": "B-Roll"}],
                      "speech": [{"nodeId": "speech-node", "volume": 100, "label": "Narration"}],
                      "background": [{"nodeId": "music-node", "volume": 20, "label": "Music"}]
                  }}}},
        {"id": "video-output", "type": "output", "position": {"x": 1300, "y": 300},
         "data": {"label": "Final Video", "type": "output", "outputType": "video"}}
    ],
    "edges": [
        {"id": "e1", "source": "script-input", "target": "refine-script", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e2", "source": "refine-script", "target": "speech-node", "sourceHandle": "text", "targetHandle": "text"},
        {"id": "e3", "source": "refine-script", "target": "refine-script-visuals", "sourceHandle": "text", "targetHandle": "text"},
        {"id": "e4", "source": "refine-script-visuals", "target": "visuals-node", "sourceHandle": "text", "targetHandle": "text"},
        {"id": "e5", "source": "visuals-node", "target": "final-editor", "sourceHandle": "video", "targetHandle": "videos"},
        {"id": "e6", "source": "speech-node", "target": "final-editor", "sourceHandle": "audio", "targetHandle": "speech"},
        {"id": "e7", "source": "music-node", "target": "final-editor", "sourceHandle": "audio", "targetHandle": "background"},
        {"id": "e8", "source": "final-editor", "target": "video-output", "sourceHandle": "video", "targetHandle": "input"}
    ]
}

LOOK_BOOK_WORKFLOW = {
    "id": "template-look-book",
    "name": "Look Book Creation (16:9)",
    "nodes": [
        {"id": "brand-input", "type": "input", "position": {"x": 100, "y": 100},
         "data": {"label": "Brand Guidelines", "type": "input", "inputType": "text", "value": ""}},
        {"id": "collection-input", "type": "input", "position": {"x": 100, "y": 300},
         "data": {"label": "Collection Theme", "type": "input", "inputType": "text", "value": ""}},
        {"id": "generate-concepts", "type": "gemini_text", "position": {"x": 400, "y": 200},
         "data": {"label": "Look Book Concepts", "type": "gemini_text", "model": "gemini-3.1-flash-lite-preview"}},
        {"id": "look-1", "type": "gemini_image", "position": {"x": 700, "y": 50},
         "data": {"label": "Look 1", "type": "gemini_image", "model": "gemini-3.1-flash-image-preview",
                  "config": {"aspect_ratio": "16:9"}}},
        {"id": "look-2", "type": "gemini_image", "position": {"x": 700, "y": 350},
         "data": {"label": "Look 2", "type": "gemini_image", "model": "gemini-3.1-flash-image-preview",
                  "config": {"aspect_ratio": "16:9"}}},
        {"id": "out-1", "type": "output", "position": {"x": 1000, "y": 50},
         "data": {"label": "Look 1 Final", "type": "output", "outputType": "image"}},
        {"id": "out-2", "type": "output", "position": {"x": 1000, "y": 350},
         "data": {"label": "Look 2 Final", "type": "output", "outputType": "image"}}
    ],
    "edges": [
        {"id": "e1", "source": "brand-input", "target": "generate-concepts", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e2", "source": "collection-input", "target": "generate-concepts", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e3", "source": "generate-concepts", "target": "look-1", "sourceHandle": "text", "targetHandle": "text"},
        {"id": "e4", "source": "generate-concepts", "target": "look-2", "sourceHandle": "text", "targetHandle": "text"},
        {"id": "e7", "source": "look-1", "target": "out-1", "sourceHandle": "image", "targetHandle": "input"},
        {"id": "e8", "source": "look-2", "target": "out-2", "sourceHandle": "image", "targetHandle": "input"}
    ]
}


# ============================================================================
# Featured templates first, then legacy
# ============================================================================
EXAMPLE_WORKFLOWS = [
    PRODUCT_AD_WORKFLOW,
    CINEMA_SHOT_WORKFLOW,
    VTO_WORKFLOW,
    INFLUENCER_VIDEO_WORKFLOW,
    LOOK_BOOK_WORKFLOW,
]
