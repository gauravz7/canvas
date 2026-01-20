from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database import get_db
from models import Workflow as WorkflowModel
from .schemas import Workflow, ExecutionRequest, WorkflowExecutionResponse, NodeType, BatchExecutionRequest, BatchExecutionResponse
from .engine import WorkflowEngine
import json
import uuid
from .example_workflows import EXAMPLE_WORKFLOWS

from fastapi.responses import StreamingResponse
from datetime import datetime
from pydantic import BaseModel

class WorkflowSummary(BaseModel):
    id: str
    name: str
    updated_at: Optional[datetime] = None

class WorkflowListResponse(BaseModel):
    workflows: List[WorkflowSummary]

router = APIRouter()
engine = WorkflowEngine()

@router.post("/execute/stream")
async def stream_execute_workflow(request: ExecutionRequest, db: Session = Depends(get_db)):
    return StreamingResponse(
        engine.stream_workflow_execution(
            request.workflow, 
            request.node_ids, 
            db=db, 
            use_cache=request.use_cache,
            execution_id=request.execution_id
        ),
        media_type="text/event-stream"
    )

@router.post("/execute/cancel/{execution_id}")
async def cancel_workflow(execution_id: str):
    success = engine.cancel_execution(execution_id)
    if success:
        return {"status": "success", "message": f"Execution {execution_id} cancelled"}
    else:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found or already finished")

@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(request: ExecutionRequest, db: Session = Depends(get_db)):
    try:
        results = await engine.execute_workflow(request.workflow, request.node_ids, db=db, use_cache=request.use_cache)
        
        # Determine overall status
        status = "completed"
        for res in results.values():
            if res.status == "failed":
                status = "failed"
                break
                
        return WorkflowExecutionResponse(
            results=results,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
async def save_workflow(workflow: Workflow, user_id: str = "default_user", db: Session = Depends(get_db)):
    try:
        # Check if exists
        db_workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow.id).first()
        
        workflow_data = workflow.model_dump() # Pydantic v2
        
        if db_workflow:
            db_workflow.name = workflow.name
            db_workflow.data = workflow_data
            # SQLAlchemy handles JSON type and updated_at (onupdate)
        else:
            db_workflow = WorkflowModel(
                id=workflow.id,
                name=workflow.name,
                data=workflow_data,
                user_id=user_id
            )
            db.add(db_workflow)
            
        db.commit()
        return {"status": "success", "id": workflow.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=WorkflowListResponse)
async def list_workflows(user_id: str = "default_user", db: Session = Depends(get_db)):
    """
    List all saved workflows for the user.
    """
    workflows = db.query(WorkflowModel).filter(WorkflowModel.user_id == user_id).order_by(WorkflowModel.updated_at.desc()).all()
    
    return WorkflowListResponse(
        workflows=[
            WorkflowSummary(
                id=wf.id,
                name=wf.name,
                updated_at=wf.updated_at
            ) for wf in workflows
        ]
    )
@router.get("/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """
    Get a specific workflow by ID.
    """
    db_workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return db_workflow.data


@router.get("/templates/examples")
async def get_example_workflows():
    """
    Returns the predefined example workflows.
    """
    return {"workflows": EXAMPLE_WORKFLOWS}


@router.post("/import")
async def import_workflow(workflow: Workflow, user_id: str = Body("default_user"), db: Session = Depends(get_db)):
    """
    Imports a workflow from JSON. 
    Ideally the frontend sends the JSON, we validate it against `Workflow` schema (done by FastAPI automatically),
    and then save it as a new workflow (or update if ID matches and user confirms? For now, we save).
    """
    # If we want to force a NEW ID for import to avoid collisions, we could do it here.
    # But usually import keeps ID or generates new one. 
    # Let's generate a new ID to be safe if it conflicts? 
    # Or just upsert.
    # User request: "import and export as a json". 
    # Usually import implies "Loading" into the canvas. 
    # But we can also save it to DB.
    
    # We will just return the valid workflow structure to be used by Frontend?
    # Or save it? "Validates and saves imported JSON" was the plan.
    
    # Check if ID exists
    exists = db.query(WorkflowModel).filter(WorkflowModel.id == workflow.id).first()
    if exists:
        # If it exists, maybe we just update it?
        # Or we generate a new ID?
        # Let's just upsert.
        pass
        
    return await save_workflow(workflow, user_id, db)

@router.post("/{workflow_id}/batch", response_model=BatchExecutionResponse)
async def batch_execute_workflow(
    workflow_id: str, 
    request: BatchExecutionRequest, 
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """
    Executes a saved workflow in batch mode for a list of inputs.
    """
    # 1. Fetch Workflow
    wf_model = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not wf_model:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    outputs = []
    
    # 2. Loop through inputs
    for val in request.inputs:
        # Create fresh workflow instance from saved data
        try:
            # wf_model.data is a dict (JSON), compatible with Workflow schema
            workflow = Workflow(**wf_model.data)
        except Exception as e:
             # If schema invalid, we can't run
             raise HTTPException(status_code=500, detail=f"Saved workflow data is invalid: {e}")
             
        # Inject Input
        # Strategy: Find first INPUT node and set its value
        input_nodes = [n for n in workflow.nodes if n.type == NodeType.INPUT]
        if input_nodes:
            input_nodes[0].data.value = val
        
        # Execute
        # We run the whole workflow (node_ids=None)
        try:
            results = await engine.execute_workflow(workflow, user_id=user_id, db=db)
            
            # Extract Output
            output_nodes = [n for n in workflow.nodes if n.type == NodeType.OUTPUT]
            start_output = None
            if output_nodes:
                 out_node = output_nodes[0]
                 if out_node.id in results and results[out_node.id].status == "completed":
                      start_output = results[out_node.id].output
            
            outputs.append(start_output)
            
        except Exception as e:
            # If one fails, we log and append error or None?
            # For batch, usually we want results aligned with inputs.
            outputs.append({"error": str(e)})

    return BatchExecutionResponse(results=outputs)

@router.post("/cache/clear")
async def clear_cache():
    """
    Clears the execution cache.
    """
    engine.cache.clear()
    return {"status": "success", "message": "Cache cleared"}
