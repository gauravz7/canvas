import uuid

def generate_id():
    return str(uuid.uuid4())


# ============================================================================
# TEMPLATE 1: Product Ad Pro - Complete Ad Generation Pipeline
# ============================================================================
# Text input → Ad copy + Visual prompt → Hero image → 3 outputs:
#   1. Upscaled hero image (for static ads)
#   2. Veo video → Upscaled video (for video ads)
#   3. Lyria background music + Speech narration
# All combined via Video Editor
# ============================================================================

PRODUCT_AD_PRO_WORKFLOW = {
    "id": "template-product-ad-pro",
    "name": "Product Ad Pro",
    "nodes": [
        {
            "id": "product-brief",
            "type": "input",
            "position": {"x": 100, "y": 200},
            "data": {
                "label": "Product Brief",
                "type": "input",
                "inputType": "text",
                "value": "Premium noise-cancelling wireless headphones, sleek black design, targeting urban professionals who value focus and audio quality"
            }
        },
        {
            "id": "ad-style",
            "type": "input",
            "position": {"x": 100, "y": 450},
            "data": {
                "label": "Visual Style",
                "type": "input",
                "inputType": "text",
                "value": "Cinematic, modern, premium lifestyle photography. Soft natural lighting, shallow depth of field, urban setting"
            }
        },
        {
            "id": "ad-copy-gen",
            "type": "gemini_text",
            "position": {"x": 400, "y": 100},
            "data": {
                "label": "Generate Ad Copy",
                "type": "gemini_text",
                "model": "gemini-3.1-flash-lite-preview",
                "value": "Write a compelling 2-sentence voiceover script for this product. Be punchy, emotional, and memorable. Output ONLY the script text, no preamble."
            }
        },
        {
            "id": "visual-prompt-gen",
            "type": "gemini_text",
            "position": {"x": 400, "y": 350},
            "data": {
                "label": "Generate Visual Prompt",
                "type": "gemini_text",
                "model": "gemini-3.1-flash-lite-preview",
                "value": "Create a single detailed image generation prompt for a hero product shot. Combine the product description with the visual style. Output ONLY the prompt, no preamble."
            }
        },
        {
            "id": "hero-image",
            "type": "gemini_image",
            "position": {"x": 750, "y": 350},
            "data": {
                "label": "Hero Product Image",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "16:9"}
            }
        },
        {
            "id": "image-upscale",
            "type": "imagen_upscale",
            "position": {"x": 1100, "y": 100},
            "data": {
                "label": "Upscale Hero Image",
                "type": "imagen_upscale"
            }
        },
        {
            "id": "hero-image-output",
            "type": "output",
            "position": {"x": 1450, "y": 100},
            "data": {
                "label": "Final Hero Image",
                "type": "output",
                "outputType": "image"
            }
        },
        {
            "id": "video-gen",
            "type": "veo_standard",
            "position": {"x": 1100, "y": 320},
            "data": {
                "label": "Generate Product Video",
                "type": "veo_standard",
                "model": "veo-3.1-lite-generate-001",
                "config": {
                    "aspect_ratio": "16:9",
                    "duration_seconds": 8,
                    "generate_audio": False
                }
            }
        },
        {
            "id": "video-upscale",
            "type": "veo_upscale",
            "position": {"x": 1450, "y": 320},
            "data": {
                "label": "Upscale to 4K",
                "type": "veo_upscale",
                "config": {
                    "resolution": "4k",
                    "aspect_ratio": "16:9",
                    "sharpness": 2
                }
            }
        },
        {
            "id": "speech-narration",
            "type": "speech_gen",
            "position": {"x": 750, "y": 700},
            "data": {
                "label": "Voiceover",
                "type": "speech_gen",
                "config": {
                    "model_id": "gemini-3.1-flash-tts-preview",
                    "voice_name": "Charon",
                    "language": "en"
                }
            }
        },
        {
            "id": "music-bg",
            "type": "lyria_clip",
            "position": {"x": 750, "y": 950},
            "data": {
                "label": "Background Music",
                "type": "lyria_clip",
                "value": "Uplifting modern electronic instrumental, subtle, minimal, motivating energy, professional commercial music",
                "config": {"model_id": "lyria-3-clip-preview"}
            }
        },
        {
            "id": "ad-editor",
            "type": "editor",
            "position": {"x": 1800, "y": 500},
            "data": {
                "label": "Final Ad Assembly",
                "type": "editor",
                "config": {
                    "sequence": {
                        "videos": [
                            {"nodeId": "video-upscale", "volume": 0, "label": "4K Product Video"}
                        ],
                        "speech": [
                            {"nodeId": "speech-narration", "volume": 100, "label": "Voiceover"}
                        ],
                        "background": [
                            {"nodeId": "music-bg", "volume": 25, "label": "BG Music"}
                        ]
                    }
                }
            }
        },
        {
            "id": "final-ad-output",
            "type": "output",
            "position": {"x": 2200, "y": 500},
            "data": {
                "label": "Final Ad Video",
                "type": "output",
                "outputType": "video"
            }
        }
    ],
    "edges": [
        {"id": "e1", "source": "product-brief", "target": "ad-copy-gen", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e2", "source": "product-brief", "target": "visual-prompt-gen", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e3", "source": "ad-style", "target": "visual-prompt-gen", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e4", "source": "visual-prompt-gen", "target": "hero-image", "sourceHandle": "text", "targetHandle": "text"},
        {"id": "e5", "source": "hero-image", "target": "image-upscale", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "e6", "source": "image-upscale", "target": "hero-image-output", "sourceHandle": "image", "targetHandle": "input"},
        {"id": "e7", "source": "hero-image", "target": "video-gen", "sourceHandle": "image", "targetHandle": "first_frame"},
        {"id": "e8", "source": "product-brief", "target": "video-gen", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "e9", "source": "video-gen", "target": "video-upscale", "sourceHandle": "video", "targetHandle": "video"},
        {"id": "e10", "source": "ad-copy-gen", "target": "speech-narration", "sourceHandle": "text", "targetHandle": "text"},
        {"id": "e11", "source": "video-upscale", "target": "ad-editor", "sourceHandle": "video", "targetHandle": "videos"},
        {"id": "e12", "source": "speech-narration", "target": "ad-editor", "sourceHandle": "audio", "targetHandle": "speech"},
        {"id": "e13", "source": "music-bg", "target": "ad-editor", "sourceHandle": "audio", "targetHandle": "background"},
        {"id": "e14", "source": "ad-editor", "target": "final-ad-output", "sourceHandle": "video", "targetHandle": "input"}
    ]
}


# ============================================================================
# TEMPLATE 2: Cinema Shot with Character - 3 Shots Combined
# ============================================================================
# Character description → Reference image → 3 different cinematic shots
# (wide / medium / close-up) → 3 video clips → Editor combines into one
# cinematic sequence with score
# ============================================================================

CINEMA_SHOT_WORKFLOW = {
    "id": "template-cinema-shot",
    "name": "Cinema Shot with Character",
    "nodes": [
        {
            "id": "character-desc",
            "type": "input",
            "position": {"x": 100, "y": 200},
            "data": {
                "label": "Character Description",
                "type": "input",
                "inputType": "text",
                "value": "A weathered detective in his 40s, dark coat, intense blue eyes, slight stubble, wearing a vintage fedora. Film noir aesthetic."
            }
        },
        {
            "id": "scene-setting",
            "type": "input",
            "position": {"x": 100, "y": 450},
            "data": {
                "label": "Scene Setting",
                "type": "input",
                "inputType": "text",
                "value": "Rain-soaked neon-lit alley in 1940s Tokyo, steam rising from manholes, distant jazz music, moody cinematic lighting"
            }
        },
        {
            "id": "character-ref",
            "type": "gemini_image",
            "position": {"x": 450, "y": 300},
            "data": {
                "label": "Character Reference",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "16:9"},
                "value": "Cinematic full body portrait of the character described, professional movie still, dramatic lighting, photorealistic"
            }
        },
        {
            "id": "shot-1-wide",
            "type": "gemini_image",
            "position": {"x": 800, "y": 50},
            "data": {
                "label": "Shot 1: Wide Establishing",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "16:9"},
                "value": "WIDE ESTABLISHING SHOT: Show the character from behind walking into the scene from far away. Atmospheric, cinematic composition. Match the reference character exactly."
            }
        },
        {
            "id": "shot-2-medium",
            "type": "gemini_image",
            "position": {"x": 800, "y": 350},
            "data": {
                "label": "Shot 2: Medium Walking",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "16:9"},
                "value": "MEDIUM TRACKING SHOT: The character walks down the street, side profile. Show motion and atmosphere. Match the reference character exactly."
            }
        },
        {
            "id": "shot-3-closeup",
            "type": "gemini_image",
            "position": {"x": 800, "y": 650},
            "data": {
                "label": "Shot 3: Close-up Reveal",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "16:9"},
                "value": "DRAMATIC CLOSE-UP: The character pauses, looks directly into camera. Intense expression, rim lighting, raindrops on hat. Match the reference character exactly."
            }
        },
        {
            "id": "video-1",
            "type": "veo_standard",
            "position": {"x": 1200, "y": 50},
            "data": {
                "label": "Animate Shot 1",
                "type": "veo_standard",
                "model": "veo-3.1-lite-generate-001",
                "config": {
                    "aspect_ratio": "16:9",
                    "duration_seconds": 8,
                    "generate_audio": False
                },
                "value": "Slow camera push in. Character walks toward camera. Rain falls. Atmospheric movement."
            }
        },
        {
            "id": "video-2",
            "type": "veo_standard",
            "position": {"x": 1200, "y": 350},
            "data": {
                "label": "Animate Shot 2",
                "type": "veo_standard",
                "model": "veo-3.1-lite-generate-001",
                "config": {
                    "aspect_ratio": "16:9",
                    "duration_seconds": 8,
                    "generate_audio": False
                },
                "value": "Smooth side-tracking shot. Character walks at steady pace. Neon lights flicker. Rain falls."
            }
        },
        {
            "id": "video-3",
            "type": "veo_standard",
            "position": {"x": 1200, "y": 650},
            "data": {
                "label": "Animate Shot 3",
                "type": "veo_standard",
                "model": "veo-3.1-lite-generate-001",
                "config": {
                    "aspect_ratio": "16:9",
                    "duration_seconds": 8,
                    "generate_audio": False
                },
                "value": "Slow zoom into character's face. They turn to look at camera. Eyes widen slightly. Subtle micro-expression."
            }
        },
        {
            "id": "cinema-score",
            "type": "lyria_pro",
            "position": {"x": 1200, "y": 950},
            "data": {
                "label": "Cinematic Score",
                "type": "lyria_pro",
                "value": "Dark cinematic orchestral score, slow tempo, melancholic strings, subtle piano, film noir mood, moody and atmospheric, builds tension",
                "config": {"model_id": "lyria-3-pro-preview"}
            }
        },
        {
            "id": "scene-editor",
            "type": "editor",
            "position": {"x": 1600, "y": 350},
            "data": {
                "label": "Cinematic Sequence",
                "type": "editor",
                "config": {
                    "sequence": {
                        "videos": [
                            {"nodeId": "video-1", "volume": 0, "label": "Wide Shot"},
                            {"nodeId": "video-2", "volume": 0, "label": "Medium Shot"},
                            {"nodeId": "video-3", "volume": 0, "label": "Close-up"}
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
            "position": {"x": 2000, "y": 350},
            "data": {
                "label": "Cinematic Sequence",
                "type": "output",
                "outputType": "video"
            }
        }
    ],
    "edges": [
        {"id": "ec1", "source": "character-desc", "target": "character-ref", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ec2", "source": "scene-setting", "target": "character-ref", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ec3", "source": "character-ref", "target": "shot-1-wide", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "ec4", "source": "scene-setting", "target": "shot-1-wide", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ec5", "source": "character-ref", "target": "shot-2-medium", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "ec6", "source": "scene-setting", "target": "shot-2-medium", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ec7", "source": "character-ref", "target": "shot-3-closeup", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "ec8", "source": "scene-setting", "target": "shot-3-closeup", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ec9", "source": "shot-1-wide", "target": "video-1", "sourceHandle": "image", "targetHandle": "first_frame"},
        {"id": "ec10", "source": "shot-2-medium", "target": "video-2", "sourceHandle": "image", "targetHandle": "first_frame"},
        {"id": "ec11", "source": "shot-3-closeup", "target": "video-3", "sourceHandle": "image", "targetHandle": "first_frame"},
        {"id": "ec12", "source": "scene-setting", "target": "cinema-score", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ec13", "source": "character-ref", "target": "cinema-score", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "ec14", "source": "video-1", "target": "scene-editor", "sourceHandle": "video", "targetHandle": "videos"},
        {"id": "ec15", "source": "video-2", "target": "scene-editor", "sourceHandle": "video", "targetHandle": "videos"},
        {"id": "ec16", "source": "video-3", "target": "scene-editor", "sourceHandle": "video", "targetHandle": "videos"},
        {"id": "ec17", "source": "cinema-score", "target": "scene-editor", "sourceHandle": "audio", "targetHandle": "background"},
        {"id": "ec18", "source": "scene-editor", "target": "cinema-output", "sourceHandle": "video", "targetHandle": "input"}
    ]
}


# ============================================================================
# TEMPLATE 3: Virtual Try-On Studio - Full Pipeline
# ============================================================================
# Person photo → Background change → VTO with garment → Image-to-video motion
# Outputs: styled photo + motion video
# ============================================================================

VTO_STUDIO_WORKFLOW = {
    "id": "template-vto-studio",
    "name": "Virtual Try-On Studio",
    "nodes": [
        {
            "id": "person-photo",
            "type": "input",
            "position": {"x": 100, "y": 100},
            "data": {
                "label": "Person Photo",
                "type": "input",
                "inputType": "image",
                "value": ""
            }
        },
        {
            "id": "garment-photo",
            "type": "input",
            "position": {"x": 100, "y": 350},
            "data": {
                "label": "Garment Photo",
                "type": "input",
                "inputType": "image",
                "value": ""
            }
        },
        {
            "id": "background-prompt",
            "type": "input",
            "position": {"x": 100, "y": 600},
            "data": {
                "label": "New Background",
                "type": "input",
                "inputType": "text",
                "value": "Luxury rooftop terrace at golden hour, city skyline, warm cinematic lighting, fashion editorial style"
            }
        },
        {
            "id": "motion-prompt",
            "type": "input",
            "position": {"x": 100, "y": 850},
            "data": {
                "label": "Motion Direction",
                "type": "input",
                "inputType": "text",
                "value": "Person turns slowly toward the camera, hair flows in the wind, confident pose, subtle smile, fashion runway energy"
            }
        },
        {
            "id": "background-swap",
            "type": "gemini_image",
            "position": {"x": 500, "y": 250},
            "data": {
                "label": "Replace Background",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "9:16"},
                "value": "Take the person from the input image and place them in this new background. Keep the person identical (same face, body, clothing for now). Only change the environment. Photorealistic."
            }
        },
        {
            "id": "vto-apply",
            "type": "gemini_image",
            "position": {"x": 850, "y": 250},
            "data": {
                "label": "Apply Garment (VTO)",
                "type": "gemini_image",
                "model": "gemini-3.1-flash-image-preview",
                "config": {"aspect_ratio": "9:16"},
                "value": "Take the person from the first image and dress them in the garment shown in the second image. Maintain the person's identity, pose, body shape, and the new background. The garment should fit naturally with realistic fabric drape, lighting, and shadows."
            }
        },
        {
            "id": "vto-upscale",
            "type": "imagen_upscale",
            "position": {"x": 1200, "y": 100},
            "data": {
                "label": "Upscale Final Image",
                "type": "imagen_upscale"
            }
        },
        {
            "id": "vto-image-output",
            "type": "output",
            "position": {"x": 1550, "y": 100},
            "data": {
                "label": "Final VTO Image",
                "type": "output",
                "outputType": "image"
            }
        },
        {
            "id": "vto-to-video",
            "type": "veo_standard",
            "position": {"x": 1200, "y": 400},
            "data": {
                "label": "Animate as Video",
                "type": "veo_standard",
                "model": "veo-3.1-lite-generate-001",
                "config": {
                    "aspect_ratio": "9:16",
                    "duration_seconds": 8,
                    "generate_audio": False
                }
            }
        },
        {
            "id": "video-upscale-vto",
            "type": "veo_upscale",
            "position": {"x": 1550, "y": 400},
            "data": {
                "label": "Upscale Video to 4K",
                "type": "veo_upscale",
                "config": {
                    "resolution": "4k",
                    "aspect_ratio": "9:16",
                    "sharpness": 2
                }
            }
        },
        {
            "id": "fashion-music",
            "type": "lyria_clip",
            "position": {"x": 1200, "y": 700},
            "data": {
                "label": "Fashion Soundtrack",
                "type": "lyria_clip",
                "value": "Modern fashion runway music, sophisticated electronic, confident energy, sleek and stylish, minimal vocals, contemporary",
                "config": {"model_id": "lyria-3-clip-preview"}
            }
        },
        {
            "id": "vto-final-editor",
            "type": "editor",
            "position": {"x": 1900, "y": 500},
            "data": {
                "label": "Fashion Reel",
                "type": "editor",
                "config": {
                    "sequence": {
                        "videos": [
                            {"nodeId": "video-upscale-vto", "volume": 0, "label": "VTO Video"}
                        ],
                        "background": [
                            {"nodeId": "fashion-music", "volume": 100, "label": "Soundtrack"}
                        ]
                    }
                }
            }
        },
        {
            "id": "vto-final-output",
            "type": "output",
            "position": {"x": 2300, "y": 500},
            "data": {
                "label": "Final Fashion Reel",
                "type": "output",
                "outputType": "video"
            }
        }
    ],
    "edges": [
        {"id": "ev1", "source": "person-photo", "target": "background-swap", "sourceHandle": "output", "targetHandle": "image"},
        {"id": "ev2", "source": "background-prompt", "target": "background-swap", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ev3", "source": "background-swap", "target": "vto-apply", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "ev4", "source": "garment-photo", "target": "vto-apply", "sourceHandle": "output", "targetHandle": "image"},
        {"id": "ev5", "source": "vto-apply", "target": "vto-upscale", "sourceHandle": "image", "targetHandle": "image"},
        {"id": "ev6", "source": "vto-upscale", "target": "vto-image-output", "sourceHandle": "image", "targetHandle": "input"},
        {"id": "ev7", "source": "vto-apply", "target": "vto-to-video", "sourceHandle": "image", "targetHandle": "first_frame"},
        {"id": "ev8", "source": "motion-prompt", "target": "vto-to-video", "sourceHandle": "output", "targetHandle": "text"},
        {"id": "ev9", "source": "vto-to-video", "target": "video-upscale-vto", "sourceHandle": "video", "targetHandle": "video"},
        {"id": "ev10", "source": "video-upscale-vto", "target": "vto-final-editor", "sourceHandle": "video", "targetHandle": "videos"},
        {"id": "ev11", "source": "fashion-music", "target": "vto-final-editor", "sourceHandle": "audio", "targetHandle": "background"},
        {"id": "ev12", "source": "vto-final-editor", "target": "vto-final-output", "sourceHandle": "video", "targetHandle": "input"}
    ]
}


# ============================================================================
# Legacy templates (kept for backward compat with simpler use cases)
# ============================================================================

PRODUCT_AD_WORKFLOW = {
    "id": "template-product-ad",
    "name": "Product Ad (Simple)",
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
            "data": {"label": "Stylize Product", "type": "gemini_image", "model": "gemini-3.1-flash-image-preview"}
        },
        {
            "id": "generate-video",
            "type": "veo_standard",
            "position": {"x": 700, "y": 100},
            "data": {"label": "Product Video", "type": "veo_standard", "model": "veo-3.1-lite-generate-001"}
        },
        {
            "id": "speech-node",
            "type": "speech_gen",
            "position": {"x": 400, "y": 300},
            "data": {"label": "Voiceover", "type": "speech_gen"}
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
            "data": {"label": "Refine Script", "type": "gemini_text", "model": "gemini-3.1-flash-lite-preview"}
        },
        {
            "id": "speech-node",
            "type": "speech_gen",
            "position": {"x": 700, "y": 100},
            "data": {"label": "Narration", "type": "speech_gen"}
        },
        {
            "id": "music-node",
            "type": "lyria_clip",
            "position": {"x": 700, "y": 300},
            "data": {"label": "Background Music", "type": "lyria_clip"}
        },
        {
            "id": "visuals-node",
            "type": "veo_standard",
            "position": {"x": 700, "y": 500},
            "data": {"label": "B-Roll Visuals", "type": "veo_standard", "model": "veo-3.1-lite-generate-001"}
        },
        {
            "id": "refine-script-visuals",
            "type": "gemini_text",
            "position": {"x": 400, "y": 500},
            "data": {"label": "Visual Prompts", "type": "gemini_text", "model": "gemini-3.1-flash-lite-preview"}
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
    "name": "Fashion Try-On (Simple)",
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
            "data": {"label": "Virtual Try-On", "type": "gemini_image", "model": "gemini-3.1-flash-image-preview"}
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
            "data": {"label": "Look Book Concepts", "type": "gemini_text", "model": "gemini-3.1-flash-lite-preview"}
        },
        {
            "id": "look-1",
            "type": "gemini_image",
            "position": {"x": 700, "y": 50},
            "data": {"label": "Look 1 Visual", "type": "gemini_image", "model": "gemini-3.1-flash-image-preview"}
        },
        {
            "id": "look-2",
            "type": "gemini_image",
            "position": {"x": 700, "y": 350},
            "data": {"label": "Look 2 Visual", "type": "gemini_image", "model": "gemini-3.1-flash-image-preview"}
        },
        {
            "id": "out-1",
            "type": "output",
            "position": {"x": 1000, "y": 50},
            "data": {"label": "Look 1 Final", "type": "output", "outputType": "image"}
        },
        {
            "id": "out-2",
            "type": "output",
            "position": {"x": 1000, "y": 350},
            "data": {"label": "Look 2 Final", "type": "output", "outputType": "image"}
        }
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
# Featured templates appear FIRST in the templates list
# ============================================================================
EXAMPLE_WORKFLOWS = [
    PRODUCT_AD_PRO_WORKFLOW,
    CINEMA_SHOT_WORKFLOW,
    VTO_STUDIO_WORKFLOW,
    PRODUCT_AD_WORKFLOW,
    INFLUENCER_VIDEO_WORKFLOW,
    FASHION_TRYON_WORKFLOW,
    LOOK_BOOK_WORKFLOW,
]
