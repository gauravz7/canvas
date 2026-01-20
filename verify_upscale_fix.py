import json

def extract_upscaled_image(data):
    # This simulates the logic added to vertex_service.py
    if "predictions" not in data or not data["predictions"]:
        raise Exception(f"No predictions in response: {data}")
    
    prediction = data["predictions"][0]
    
    # 1. Try direct bytesBase64Encoded
    if isinstance(prediction, dict) and "bytesBase64Encoded" in prediction:
        return prediction["bytesBase64Encoded"]
    
    # 2. Try nested in an "image" key
    if isinstance(prediction, dict) and "image" in prediction and isinstance(prediction["image"], dict):
        if "bytesBase64Encoded" in prediction["image"]:
            return prediction["image"]["bytesBase64Encoded"]
    
    # 3. If prediction is already a string, assume it's the base64 data
    if isinstance(prediction, str):
        return prediction
        
    return None

# Test cases
test_cases = [
    {
        "name": "Direct bytesBase64Encoded",
        "data": {"predictions": [{"bytesBase64Encoded": "direct_b64"}]},
        "expected": "direct_b64"
    },
    {
        "name": "Nested image.bytesBase64Encoded",
        "data": {"predictions": [{"image": {"bytesBase64Encoded": "nested_b64"}}]},
        "expected": "nested_b64"
    },
    {
        "name": "Direct string prediction",
        "data": {"predictions": ["string_b64"]},
        "expected": "string_b64"
    },
    {
        "name": "Missing key (fails)",
        "data": {"predictions": [{"something_else": "oops"}]},
        "expected": None
    }
]

for tc in test_cases:
    print(f"Testing: {tc['name']}")
    try:
        result = extract_upscaled_image(tc['data'])
        if result == tc['expected']:
            print(f"  ✅ Success: Got {result}")
        else:
            print(f"  ❌ Failure: Expected {tc['expected']}, got {result}")
    except Exception as e:
        if tc['expected'] is None:
             print(f"  ✅ Success: Caught expected error: {e}")
        else:
             print(f"  ❌ Failure: Unexpected error: {e}")
