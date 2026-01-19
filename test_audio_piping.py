
import asyncio
from backend.canvas_module.engine import WorkflowEngine
from backend.canvas_module.schemas import Workflow, Node, NodeType, Connection
from backend.services.vertex_service import vertex_service
from unittest.mock import MagicMock

# Mock Vertex Service to avoid real API calls and cost
vertex_service.synthesize_raw = MagicMock(return_value="UklGRigAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=") # Empty WAV

async def test_audio_piping():
    engine = WorkflowEngine()
    
    # Define Nodes
    speech_node = Node(
        id="speech-1",
        type=NodeType.SPEECH_GEN,
        data={"value": "Hello world", "config": {"model_id": "gemini-2.5-flash-tts", "voice_name": "Kore"}},
        position={"x": 0, "y": 0}
    )
    
    gemini_node = Node(
        id="gemini-1",
        type=NodeType.GEMINI_TEXT,
        data={"value": "Describe the audio", "model": "gemini-2.0-flash-exp"},
        position={"x": 200, "y": 0}
    )
    
    # Define Edge: Speech (audio) -> Gemini (other)
    edge = Connection(
        id="e1",
        source="speech-1",
        target="gemini-1",
        sourceHandle="audio",
        targetHandle="other"
    )
    
    workflow = Workflow(
        id="test-wf",
        nodes=[speech_node, gemini_node],
        edges=[edge]
    )
    
    # Mock Gemini Service to inspect inputs
    from backend.services.gemini_service import gemini_service
    gemini_service.generate_content = MagicMock(return_value={"text": "I heard audio."})
    
    print("Executing workflow...")
    results = await engine.execute_workflow(workflow)
    
    print("\nResults:")
    for nid, res in results.items():
        print(f"{nid}: {res.status}")
        if res.error:
            print(f"  Error: {res.error}")
        if res.output:
            print(f"  Output: {str(res.output)[:100]}...")

    # Inspect what Gemini received
    call_args = gemini_service.generate_content.call_args
    if call_args:
        contents = call_args.kwargs.get('contents')
        print("\nGemini Received Contents:", len(contents))
        for i, part in enumerate(contents):
            if hasattr(part, 'inline_data'):
                 print(f"Part {i}: Inline Data (mime={part.inline_data.mime_type}, size={len(part.inline_data.data)})")
            elif hasattr(part, 'file_data'):
                 print(f"Part {i}: File Data (uri={part.file_data.file_uri})")
            else:
                 print(f"Part {i}: {type(part)} - {part}")

if __name__ == "__main__":
    asyncio.run(test_audio_piping())
