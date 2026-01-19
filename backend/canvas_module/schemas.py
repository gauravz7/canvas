from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum

class NodeType(str, Enum):
    INPUT = "input" # Text or File input
    OUTPUT = "output" # View result
    GEMINI_TEXT = "gemini_text"
    GEMINI_IMAGE = "gemini_image"
    IMAGEN_UPSCALE = "imagen_upscale"
    SPEECH_GEN = "speech_gen"
    LYRIA_GEN = "lyria_gen"
    VEO_STANDARD = "veo_standard"
    VEO_EXTEND = "veo_extend"
    VEO_REFERENCE = "veo_reference"
    WORKFLOW = "workflow" # Nested workflow

class ParamType(str, Enum):
    STRING = "string"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NUMBER = "number"
    SELECT = "select"

class Connection(BaseModel):
    id: str
    source: str # Node ID
    target: str # Node ID
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None

class NodeData(BaseModel):
    label: str = ""
    value: Any = None # Static value for input nodes
    model: str = "gemini-3-pro-preview" # Default model
    system_instruction: Optional[str] = None
    output_key: str = "output" # Key to store output in execution context
    prompt_template: Optional[str] = None # e.g. "Describe {{input_node_id.output}}"
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # Context/Workflow Reference
    workflow_id: Optional[str] = None # For nested workflows

    # Frontend-specific fields
    inputType: Optional[str] = None
    outputType: Optional[str] = None
    status: Optional[str] = "idle" # "idle", "running", "completed", "failed"
    executionResult: Optional[Any] = None
    
    # Other extra fields (React Flow might add more)
    model_config = {
        "extra": "allow"
    }

class Node(BaseModel):
    id: str
    type: NodeType
    position: Dict[str, float]
    data: NodeData
    
class Workflow(BaseModel):
    id: str
    name: str = "Untitled Workflow"
    nodes: List[Node]
    edges: List[Connection]
    
class ExecutionRequest(BaseModel):
    workflow: Workflow
    node_ids: Optional[List[str]] = None
    use_cache: bool = False # Default to False as per user request 
    # Current design: User likely wants to "Run Node" which implies running that node given current context, 
    # or "Run Workflow" which runs everything.
    # For now, if node_ids is present, we might assume the frontend ensures inputs are ready or we re-run deps.
    # Simpler approach: partial execution re-runs dependencies if they are not cached/valid.
    # For MVP: "Run Node" might just run that SINGLE node, assuming inputs are static or previously computed?
    # Let's stick to: if node_ids provided, execute those. 

class ExecutionResult(BaseModel):
    node_id: str
    status: str # "completed", "failed"
    output: Any
    error: Optional[str] = None

class WorkflowExecutionResponse(BaseModel):
    results: Dict[str, ExecutionResult]
    status: str

class BatchExecutionRequest(BaseModel):
    inputs: List[Any] # List of input values (passed to the workflow's input node)

class BatchExecutionResponse(BaseModel):
    results: List[Any] # List of outputs corresponding to inputs

