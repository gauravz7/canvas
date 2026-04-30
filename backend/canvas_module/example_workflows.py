import uuid

def generate_id():
    return str(uuid.uuid4())


# ============================================================================
# Templates use the SAME node defaults as drag-drop from the toolbar.
# Generic labels, no custom prompts, no special configs.
# Only structurally-required config: aspect_ratio for 16:9 widescreen,
# editor sequence to map connected nodes to slots.
# ============================================================================


def _node(node_id, node_type, x, y, label, extra_data=None):
    """Create a node matching the canvas drag-drop structure."""
    data = {
        "label": label,
        "type": node_type,
        "value": "",
        "model": "",
    }
    if node_type == "input":
        data["inputType"] = (extra_data or {}).pop("inputType", "text")
    if node_type == "output":
        data["outputType"] = (extra_data or {}).pop("outputType", "text")
    if extra_data:
        data.update(extra_data)
    return {
        "id": node_id,
        "type": node_type,
        "position": {"x": x, "y": y},
        "data": data
    }


def _edge(eid, source, target, source_handle="output", target_handle="input"):
    return {
        "id": eid,
        "source": source,
        "target": target,
        "sourceHandle": source_handle,
        "targetHandle": target_handle
    }


# ============================================================================
# 1. Product Ad (16:9)
# ============================================================================
PRODUCT_AD_WORKFLOW = {
    "id": "template-product-ad",
    "name": "Product Ad (16:9)",
    "nodes": [
        _node("product-photo", "input", 100, 200, "Text Input", {"inputType": "image"}),
        _node("brand-brief", "input", 100, 480, "Text Input", {"inputType": "text"}),
        _node("visual-style", "input", 100, 730, "Text Input", {"inputType": "text"}),
        _node("stylize-image", "gemini_image", 470, 350, "Gemini Image",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("image-upscale", "imagen_upscale", 850, 100, "Image Upscaler"),
        _node("image-output", "output", 1200, 100, "Image Output", {"outputType": "image"}),
        _node("veo-animate", "veo_standard", 850, 380, "Veo Standard",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("veo-upscale", "veo_upscale", 1200, 380, "Video Upscale",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("voice-gen", "speech_gen", 470, 750, "Speech Gen"),
        _node("music-gen", "lyria_clip", 470, 1020, "Lyria Clip"),
        _node("ad-editor", "editor", 1550, 600, "Video Editor", {
            "config": {
                "sequence": {
                    "videos": [{"nodeId": "veo-upscale", "volume": 0, "label": "Video Upscale"}],
                    "speech": [{"nodeId": "voice-gen", "volume": 100, "label": "Speech Gen"}],
                    "background": [{"nodeId": "music-gen", "volume": 25, "label": "Lyria Clip"}]
                }
            }
        }),
        _node("final-output", "output", 1950, 600, "Video Output", {"outputType": "video"}),
    ],
    "edges": [
        _edge("e1", "product-photo", "stylize-image", "output", "image"),
        _edge("e2", "brand-brief", "stylize-image", "output", "text"),
        _edge("e3", "visual-style", "stylize-image", "output", "text"),
        _edge("e4", "stylize-image", "image-upscale", "image", "image"),
        _edge("e5", "image-upscale", "image-output", "image", "input"),
        _edge("e6", "stylize-image", "veo-animate", "image", "first_frame"),
        _edge("e7", "brand-brief", "veo-animate", "output", "text"),
        _edge("e8", "veo-animate", "veo-upscale", "video", "video"),
        _edge("e9", "brand-brief", "voice-gen", "output", "text"),
        _edge("e10", "brand-brief", "music-gen", "output", "text"),
        _edge("e11", "veo-upscale", "ad-editor", "video", "videos"),
        _edge("e12", "voice-gen", "ad-editor", "audio", "speech"),
        _edge("e13", "music-gen", "ad-editor", "audio", "background"),
        _edge("e14", "ad-editor", "final-output", "video", "input"),
    ]
}


# ============================================================================
# 2. Cinema Shot — 3 Cuts (16:9)
# ============================================================================
CINEMA_SHOT_WORKFLOW = {
    "id": "template-cinema-shot",
    "name": "Cinema Shot — 3 Cuts (16:9)",
    "nodes": [
        _node("character-input", "input", 100, 200, "Text Input", {"inputType": "image"}),
        _node("character-desc", "input", 100, 460, "Text Input", {"inputType": "text"}),
        _node("scene-setting", "input", 100, 710, "Text Input", {"inputType": "text"}),
        _node("character-ref", "gemini_image", 470, 350, "Gemini Image",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("shot-wide", "gemini_image", 870, 80, "Gemini Image",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("shot-medium", "gemini_image", 870, 380, "Gemini Image",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("shot-closeup", "gemini_image", 870, 680, "Gemini Image",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("video-wide", "veo_standard", 1280, 80, "Veo Standard",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("video-medium", "veo_standard", 1280, 380, "Veo Standard",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("video-closeup", "veo_standard", 1280, 680, "Veo Standard",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("cinema-score", "lyria_pro", 1280, 980, "Lyria Pro"),
        _node("cinema-editor", "editor", 1700, 380, "Video Editor", {
            "config": {
                "sequence": {
                    "videos": [
                        {"nodeId": "video-wide", "volume": 0, "label": "Veo Standard"},
                        {"nodeId": "video-medium", "volume": 0, "label": "Veo Standard"},
                        {"nodeId": "video-closeup", "volume": 0, "label": "Veo Standard"}
                    ],
                    "background": [{"nodeId": "cinema-score", "volume": 80, "label": "Lyria Pro"}]
                }
            }
        }),
        _node("cinema-output", "output", 2100, 380, "Video Output", {"outputType": "video"}),
    ],
    "edges": [
        _edge("ec1", "character-input", "character-ref", "output", "image"),
        _edge("ec2", "character-desc", "character-ref", "output", "text"),
        _edge("ec3", "scene-setting", "character-ref", "output", "text"),
        _edge("ec4", "character-ref", "shot-wide", "image", "image"),
        _edge("ec5", "scene-setting", "shot-wide", "output", "text"),
        _edge("ec6", "character-ref", "shot-medium", "image", "image"),
        _edge("ec7", "scene-setting", "shot-medium", "output", "text"),
        _edge("ec8", "character-ref", "shot-closeup", "image", "image"),
        _edge("ec9", "scene-setting", "shot-closeup", "output", "text"),
        _edge("ec10", "shot-wide", "video-wide", "image", "first_frame"),
        _edge("ec11", "shot-medium", "video-medium", "image", "first_frame"),
        _edge("ec12", "shot-closeup", "video-closeup", "image", "first_frame"),
        _edge("ec13", "scene-setting", "cinema-score", "output", "text"),
        _edge("ec14", "character-ref", "cinema-score", "image", "image"),
        _edge("ec15", "video-wide", "cinema-editor", "video", "videos"),
        _edge("ec16", "video-medium", "cinema-editor", "video", "videos"),
        _edge("ec17", "video-closeup", "cinema-editor", "video", "videos"),
        _edge("ec18", "cinema-score", "cinema-editor", "audio", "background"),
        _edge("ec19", "cinema-editor", "cinema-output", "video", "input"),
    ]
}


# ============================================================================
# 3. Virtual Try-On (16:9)
# ============================================================================
VTO_WORKFLOW = {
    "id": "template-vto",
    "name": "Virtual Try-On (16:9)",
    "nodes": [
        _node("person-photo", "input", 100, 100, "Text Input", {"inputType": "image"}),
        _node("garment-photo", "input", 100, 400, "Text Input", {"inputType": "image"}),
        _node("background-prompt", "input", 100, 700, "Text Input", {"inputType": "text"}),
        _node("motion-prompt", "input", 100, 950, "Text Input", {"inputType": "text"}),
        _node("vto-apply", "gemini_image", 470, 200, "Gemini Image",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("background-swap", "gemini_image", 870, 350, "Gemini Image",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("image-output", "output", 1280, 100, "Image Output", {"outputType": "image"}),
        _node("vto-animate", "veo_standard", 1280, 400, "Veo Standard",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("video-upscale", "veo_upscale", 1640, 400, "Video Upscale",
              {"config": {"aspect_ratio": "16:9"}}),
        _node("fashion-music", "lyria_clip", 870, 750, "Lyria Clip"),
        _node("vto-editor", "editor", 1990, 500, "Video Editor", {
            "config": {
                "sequence": {
                    "videos": [{"nodeId": "video-upscale", "volume": 0, "label": "Video Upscale"}],
                    "background": [{"nodeId": "fashion-music", "volume": 100, "label": "Lyria Clip"}]
                }
            }
        }),
        _node("final-reel", "output", 2390, 500, "Video Output", {"outputType": "video"}),
    ],
    "edges": [
        _edge("ev1", "person-photo", "vto-apply", "output", "image"),
        _edge("ev2", "garment-photo", "vto-apply", "output", "image"),
        _edge("ev3", "vto-apply", "background-swap", "image", "image"),
        _edge("ev4", "background-prompt", "background-swap", "output", "text"),
        _edge("ev5", "background-swap", "image-output", "image", "input"),
        _edge("ev6", "background-swap", "vto-animate", "image", "first_frame"),
        _edge("ev7", "motion-prompt", "vto-animate", "output", "text"),
        _edge("ev8", "vto-animate", "video-upscale", "video", "video"),
        _edge("ev9", "background-prompt", "fashion-music", "output", "text"),
        _edge("ev10", "video-upscale", "vto-editor", "video", "videos"),
        _edge("ev11", "fashion-music", "vto-editor", "audio", "background"),
        _edge("ev12", "vto-editor", "final-reel", "video", "input"),
    ]
}


EXAMPLE_WORKFLOWS = [
    PRODUCT_AD_WORKFLOW,
    CINEMA_SHOT_WORKFLOW,
    VTO_WORKFLOW,
]
