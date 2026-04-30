import uuid

def generate_id():
    return str(uuid.uuid4())


# ============================================================================
# Templates use ONLY default node configs (no pre-filled values).
# Users see the standard nodes from the toolbar, structurally connected.
# All templates default to 16:9 widescreen.
# ============================================================================


# ============================================================================
# 1. Product Ad (16:9)
# Inputs: Product Photo + Brand Brief + Visual Style
# Outputs: Hero Image (4K) + Final Ad Video with voice + music
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
            "data": {"label": "Stylize Product", "type": "gemini_image", "config": {"aspect_ratio": "16:9"}}
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
            "data": {"label": "Animate Product", "type": "veo_standard", "config": {"aspect_ratio": "16:9"}}
        },
        {
            "id": "veo-upscale",
            "type": "veo_upscale",
            "position": {"x": 1200, "y": 380},
            "data": {"label": "Upscale to 4K", "type": "veo_upscale", "config": {"resolution": "4k", "aspect_ratio": "16:9"}}
        },
        {
            "id": "voice-gen",
            "type": "speech_gen",
            "position": {"x": 470, "y": 750},
            "data": {"label": "Voiceover", "type": "speech_gen"}
        },
        {
            "id": "music-gen",
            "type": "lyria_clip",
            "position": {"x": 470, "y": 1020},
            "data": {"label": "Background Music", "type": "lyria_clip"}
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
                        "videos": [{"nodeId": "veo-upscale", "volume": 0, "label": "Video"}],
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
# 2. Cinema Shot — 3 Cuts (16:9)
# Same scene, 3 framing variations with shared character reference
# ============================================================================
CINEMA_SHOT_WORKFLOW = {
    "id": "template-cinema-shot",
    "name": "Cinema Shot — 3 Cuts (16:9)",
    "nodes": [
        {
            "id": "character-input",
            "type": "input",
            "position": {"x": 100, "y": 200},
            "data": {"label": "Character Photo", "type": "input", "inputType": "image", "value": ""}
        },
        {
            "id": "character-desc",
            "type": "input",
            "position": {"x": 100, "y": 460},
            "data": {"label": "Character Description", "type": "input", "inputType": "text", "value": ""}
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
            "data": {"label": "Character Reference", "type": "gemini_image", "config": {"aspect_ratio": "16:9"}}
        },
        {
            "id": "shot-wide",
            "type": "gemini_image",
            "position": {"x": 870, "y": 80},
            "data": {"label": "Shot 1: Wide", "type": "gemini_image", "config": {"aspect_ratio": "16:9"}}
        },
        {
            "id": "shot-medium",
            "type": "gemini_image",
            "position": {"x": 870, "y": 380},
            "data": {"label": "Shot 2: Medium", "type": "gemini_image", "config": {"aspect_ratio": "16:9"}}
        },
        {
            "id": "shot-closeup",
            "type": "gemini_image",
            "position": {"x": 870, "y": 680},
            "data": {"label": "Shot 3: Close-up", "type": "gemini_image", "config": {"aspect_ratio": "16:9"}}
        },
        {
            "id": "video-wide",
            "type": "veo_standard",
            "position": {"x": 1280, "y": 80},
            "data": {"label": "Animate Wide", "type": "veo_standard", "config": {"aspect_ratio": "16:9"}}
        },
        {
            "id": "video-medium",
            "type": "veo_standard",
            "position": {"x": 1280, "y": 380},
            "data": {"label": "Animate Medium", "type": "veo_standard", "config": {"aspect_ratio": "16:9"}}
        },
        {
            "id": "video-closeup",
            "type": "veo_standard",
            "position": {"x": 1280, "y": 680},
            "data": {"label": "Animate Close-up", "type": "veo_standard", "config": {"aspect_ratio": "16:9"}}
        },
        {
            "id": "cinema-score",
            "type": "lyria_pro",
            "position": {"x": 1280, "y": 980},
            "data": {"label": "Cinematic Score", "type": "lyria_pro"}
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
                        "background": [{"nodeId": "cinema-score", "volume": 80, "label": "Score"}]
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
# 3. Virtual Try-On (16:9)
# VTO first (preserves face), then background swap, then animate
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
            "data": {"label": "Virtual Try-On", "type": "gemini_image", "config": {"aspect_ratio": "16:9"}}
        },
        {
            "id": "background-swap",
            "type": "gemini_image",
            "position": {"x": 870, "y": 350},
            "data": {"label": "Replace Background", "type": "gemini_image", "config": {"aspect_ratio": "16:9"}}
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
            "data": {"label": "Animate Person", "type": "veo_standard", "config": {"aspect_ratio": "16:9"}}
        },
        {
            "id": "video-upscale",
            "type": "veo_upscale",
            "position": {"x": 1640, "y": 400},
            "data": {"label": "Upscale to 4K", "type": "veo_upscale", "config": {"resolution": "4k", "aspect_ratio": "16:9"}}
        },
        {
            "id": "fashion-music",
            "type": "lyria_clip",
            "position": {"x": 870, "y": 750},
            "data": {"label": "Fashion Soundtrack", "type": "lyria_clip"}
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
                        "videos": [{"nodeId": "video-upscale", "volume": 0, "label": "Video"}],
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


EXAMPLE_WORKFLOWS = [
    PRODUCT_AD_WORKFLOW,
    CINEMA_SHOT_WORKFLOW,
    VTO_WORKFLOW,
]
