import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.vertex_service import vertex_service, settings

async def test_tts():
    print(f"Endpoint: {settings.TTS_API_ENDPOINT}")
    print("Testing TTS with Journey Voice payload...")
    try:
        payload = {
            "input": {"text": "Hello world"},
            "audioConfig": {"audioEncoding": "LINEAR16"},
            "voice": {
                "languageCode": "en-US",
                "name": "Kore",
                "model_name": "gemini-2.5-flash-tts" 
            },


        }
        
        # We need credentials. If not set, it might fail if local auth not cached.
        # Ensure PROJECT_ID is set
        os.environ["GOOGLE_CLOUD_PROJECT"] = "vital-octagon-19612"
        
        response = await vertex_service.synthesize_raw(payload)
        print(f"Success! Received {len(response)} bytes of audio.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_tts())
