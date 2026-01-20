import uuid

def generate_id():
    return str(uuid.uuid4())

PRODUCT_AD_WORKFLOW = {
    "id": "template-product-ad",
    "name": "Product Ad Workflow",
    "nodes": [
        {
            "id": "product-input",
            "type": "input",
            "position": {"x": 100, "y": 100},
            "data": {"label": "Product Photo", "type": "input", "inputType": "image", "value": ""}
        },
        {
            "id": "ad-copy-input",
            "type": "input",
            "position": {"x": 100, "y": 300},
            "data": {"label": "Ad Brief", "type": "input", "inputType": "text", "value": "A refreshing summer drink"}
        },
        {
            "id": "stylize-image",
            "type": "gemini_image",
            "position": {"x": 400, "y": 100},
            "data": {"label": "Stylize Product", "type": "gemini_image", "model": "gemini-3-pro-image-preview"}
        },
        {
            "id": "generate-video",
            "type": "veo_standard",
            "position": {"x": 700, "y": 100},
            "data": {"label": "Product Video", "type": "veo_standard", "model": "veo-3.1-fast-generate-preview"}
        },
        {
            "id": "speech-node",
            "type": "speech_gen",
            "position": {"x": 400, "y": 300},
            "data": {"label": "Voiceover", "type": "speech_gen", "model": ""}
        },
        {
            "id": "final-editor",
            "type": "editor",
            "position": {"x": 1000, "y": 200},
            "data": {
                "label": "Final Ad Assembly",
                "type": "editor",
                "config": {
                    "sequence": {
                        "videos": [{"nodeId": "generate-video", "volume": 100, "label": "Product Video"}],
                        "speech": [{"nodeId": "speech-node", "volume": 100, "label": "Voiceover"}]
                    }
                }
            }
        },
        {
            "id": "final-output",
            "type": "output",
            "position": {"x": 1300, "y": 200},
            "data": {"label": "Final Ad Video", "type": "output", "outputType": "video"}
        }
    ],
    "edges": [
        {"id": "e1", "source": "product-input", "target": "stylize-image", "sourceHandle": "output", "targetHandle": "image"},
        {"id": "e2", "source": "ad-copy-input", "target": "stylize-image", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e3", "source": "stylize-image", "target": "generate-video", "sourceHandle": "image", "targetHandle": "first_frame"},
        {"id": "e4", "source": "ad-copy-input", "target": "speech-node", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e5", "source": "generate-video", "target": "final-editor", "sourceHandle": "video", "targetHandle": "videos"},
        {"id": "e6", "source": "speech-node", "target": "final-editor", "sourceHandle": "audio", "targetHandle": "speech"},
        {"id": "e7", "source": "final-editor", "target": "final-output", "sourceHandle": "video", "targetHandle": "input"}
    ]
}

INFLUENCER_VIDEO_WORKFLOW = {
    "id": "template-influencer",
    "name": "Influencer Video",
    "nodes": [
        {
            "id": "script-input",
            "type": "input",
            "position": {"x": 100, "y": 100},
            "data": {"label": "Video Script", "type": "input", "inputType": "text", "value": "Hi guys, today I'm showing you..."}
        },
        {
            "id": "refine-script",
            "type": "gemini_text",
            "position": {"x": 400, "y": 100},
            "data": {"label": "Refine Script", "type": "gemini_text", "model": "gemini-3-flash-preview"}
        },
        {
            "id": "speech-node",
            "type": "speech_gen",
            "position": {"x": 700, "y": 100},
            "data": {"label": "Narration", "type": "speech_gen"}
        },
        {
            "id": "music-node",
            "type": "lyria_gen",
            "position": {"x": 700, "y": 300},
            "data": {"label": "Background Music", "type": "lyria_gen"}
        },
        {
            "id": "visuals-node",
            "type": "veo_standard",
            "position": {"x": 700, "y": 500},
            "data": {"label": "B-Roll Visuals", "type": "veo_standard", "model": "veo-3.1-fast-generate-preview"}
        },
        {
            "id": "refine-script-visuals",
            "type": "gemini_text",
            "position": {"x": 400, "y": 500},
            "data": {"label": "Visual Prompts", "type": "gemini_text", "model": "gemini-3-flash-preview"}
        },
        {
            "id": "final-editor",
            "type": "editor",
            "position": {"x": 1000, "y": 300},
            "data": {
                "label": "Influencer Video Edit",
                "type": "editor",
                "config": {
                    "sequence": {
                        "videos": [{"nodeId": "visuals-node", "volume": 100, "label": "B-Roll"}],
                        "speech": [{"nodeId": "speech-node", "volume": 100, "label": "Narration"}],
                        "background": [{"nodeId": "music-node", "volume": 20, "label": "Music"}]
                    }
                }
            }
        },
        {
            "id": "video-output",
            "type": "output",
            "position": {"x": 1300, "y": 300},
            "data": {"label": "Final Video", "type": "output", "outputType": "video"}
        }
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

FASHION_TRYON_WORKFLOW = {
    "id": "template-fashion-tryon",
    "name": "Fashion Virtual Tryon",
    "nodes": [
        {
            "id": "person-input",
            "type": "input",
            "position": {"x": 100, "y": 100},
            "data": {"label": "Person Image", "type": "input", "inputType": "image", "value": ""}
        },
        {
            "id": "clothing-input",
            "type": "input",
            "position": {"x": 100, "y": 400},
            "data": {"label": "Clothing Photo", "type": "input", "inputType": "image", "value": ""}
        },
        {
            "id": "tryon-node",
            "type": "gemini_image",
            "position": {"x": 400, "y": 250},
            "data": {"label": "Virtual Tryon", "type": "gemini_image", "model": "gemini-3-pro-image-preview"}
        },
        {
            "id": "upscale-node",
            "type": "imagen_upscale",
            "position": {"x": 700, "y": 250},
            "data": {"label": "Upscale Result", "type": "imagen_upscale"}
        },
        {
            "id": "image-output",
            "type": "output",
            "position": {"x": 1000, "y": 250},
            "data": {"label": "High Res Tryon", "type": "output", "outputType": "image"}
        }
    ],
    "edges": [
        {"id": "e1", "source": "person-input", "target": "tryon-node", "sourceHandle": "output", "targetHandle": "image"},
        {"id": "e2", "source": "clothing-input", "target": "tryon-node", "sourceHandle": "output", "targetHandle": "image"},
        {"id": "e3", "source": "tryon-node", "target": "upscale-node", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "e4", "source": "upscale-node", "target": "image-output", "sourceHandle": "image", "targetHandle": "input"}
    ]
}

LOOK_BOOK_WORKFLOW = {
    "id": "template-look-book",
    "name": "Look Book Creation",
    "nodes": [
        {
            "id": "brand-input",
            "type": "input",
            "position": {"x": 100, "y": 100},
            "data": {"label": "Brand Guidelines", "type": "input", "inputType": "text", "value": "Luxurious, minimalist fashion brand"}
        },
        {
            "id": "collection-input",
            "type": "input",
            "position": {"x": 100, "y": 300},
            "data": {"label": "Collection Theme", "type": "input", "inputType": "text", "value": "Ocean Breeze Collection"}
        },
        {
            "id": "generate-concepts",
            "type": "gemini_text",
            "position": {"x": 400, "y": 200},
            "data": {"label": "Look Book Concepts", "type": "gemini_text", "model": "gemini-3-flash-preview"}
        },
        {
            "id": "look-1",
            "type": "gemini_image",
            "position": {"x": 700, "y": 50},
            "data": {"label": "Look 1 Visual", "type": "gemini_image", "model": "gemini-3-pro-image-preview"}
        },
        {
            "id": "look-2",
            "type": "gemini_image",
            "position": {"x": 700, "y": 350},
            "data": {"label": "Look 2 Visual", "type": "gemini_image", "model": "gemini-3-pro-image-preview"}
        },
        {
            "id": "desc-1",
            "type": "gemini_text",
            "position": {"x": 1000, "y": 50},
            "data": {"label": "Look 1 Copy", "type": "gemini_text", "model": "gemini-3-flash-preview"}
        },
        {
            "id": "desc-2",
            "type": "gemini_text",
            "position": {"x": 1000, "y": 350},
            "data": {"label": "Look 2 Copy", "type": "gemini_text", "model": "gemini-3-flash-preview"}
        },
        {
            "id": "out-1",
            "type": "output",
            "position": {"x": 1300, "y": 50},
            "data": {"label": "Look 1 Final", "type": "output", "outputType": "image"}
        },
        {
            "id": "out-2",
            "type": "output",
            "position": {"x": 1300, "y": 350},
            "data": {"label": "Look 2 Final", "type": "output", "outputType": "image"}
        }
    ],
    "edges": [
        {"id": "e1", "source": "brand-input", "target": "generate-concepts", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e2", "source": "collection-input", "target": "generate-concepts", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e3", "source": "generate-concepts", "target": "look-1", "sourceHandle": "text", "targetHandle": "text"},
        {"id": "e4", "source": "generate-concepts", "target": "look-2", "sourceHandle": "text", "targetHandle": "text"},
        {"id": "e5", "source": "look-1", "target": "desc-1", "sourceHandle": "image", "targetHandle": "other"},
        {"id": "e6", "source": "look-2", "target": "desc-2", "sourceHandle": "image", "targetHandle": "other"},
        {"id": "e7", "source": "look-1", "target": "out-1", "sourceHandle": "image", "targetHandle": "input"},
        {"id": "e8", "source": "look-2", "target": "out-2", "sourceHandle": "image", "targetHandle": "input"}
    ]
}

EXAMPLE_WORKFLOWS = [
    PRODUCT_AD_WORKFLOW,
    INFLUENCER_VIDEO_WORKFLOW,
    FASHION_TRYON_WORKFLOW,
    LOOK_BOOK_WORKFLOW
]
