"""
Workflow API Routes - Visual Workflow Editor endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

from ..workflow.registry import WorkflowRegistry, get_workflow_registry

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])


# Request/Response models
class WorkflowInfo(BaseModel):
    workflow_id: str
    name: str
    description: str
    status: str
    version: int
    node_count: int
    edge_count: int
    created_at: str
    updated_at: str


class WorkflowResponse(BaseModel):
    workflow: WorkflowInfo
    nodes: List[Dict]
    edges: List[Dict]


class ExecutionResponse(BaseModel):
    workflow_id: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    nodes_executed: List[Dict] = []
    error: Optional[str] = None


@router.get("/", response_model=List[WorkflowInfo])
async def list_workflows(
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Workflow'ları listele
    """
    try:
        registry = get_workflow_registry()
        workflows = registry.list_workflows(status=status)
        
        return [WorkflowInfo(**wf) for wf in workflows[:limit]]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=WorkflowInfo)
async def create_workflow(request: dict = Body(...)):
    """
    Yeni workflow oluştur
    """
    try:
        registry = get_workflow_registry()
        workflow_id = await registry.create_workflow(
            name=request.get("name", "Untitled"),
            description=request.get("description", ""),
            template_id=request.get("template_id"),
            created_by=request.get("created_by")
        )
        
        workflow = registry.get_workflow(workflow_id)
        
        return WorkflowInfo(
            workflow_id=workflow.workflow_id,
            name=workflow.name,
            description=workflow.description,
            status=workflow.status,
            version=workflow.version,
            node_count=len(workflow.nodes),
            edge_count=len(workflow.edges),
            created_at=workflow.created_at.isoformat(),
            updated_at=workflow.updated_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    """
    Workflow detayı
    """
    try:
        registry = get_workflow_registry()
        workflow = registry.get_workflow(workflow_id)
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return WorkflowResponse(
            workflow=WorkflowInfo(
                workflow_id=workflow.workflow_id,
                name=workflow.name,
                description=workflow.description,
                status=workflow.status,
                version=workflow.version,
                node_count=len(workflow.nodes),
                edge_count=len(workflow.edges),
                created_at=workflow.created_at.isoformat(),
                updated_at=workflow.updated_at.isoformat()
            ),
            nodes=[node.to_dict() for node in workflow.nodes],
            edges=[edge.to_dict() for edge in workflow.edges]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    input_data: Dict[str, Any] = Body({})
):
    """
    Workflow çalıştır
    """
    try:
        registry = get_workflow_registry()
        result = await registry.execute_workflow(workflow_id, input_data)
        
        return ExecutionResponse(
            workflow_id=workflow_id,
            status=result.get("status", "unknown"),
            started_at=result.get("started_at", ""),
            completed_at=result.get("completed_at"),
            nodes_executed=result.get("nodes_executed", []),
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/executions")
async def get_workflow_executions(
    workflow_id: str,
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Workflow execution history
    """
    try:
        registry = get_workflow_registry()
        executions = registry.get_execution_history(workflow_id=workflow_id, limit=limit)
        
        return {
            "workflow_id": workflow_id,
            "executions": executions,
            "total": len(executions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/clone")
async def clone_workflow(
    workflow_id: str,
    request: dict = Body(...)
):
    """
    Workflow klonla
    """
    try:
        registry = get_workflow_registry()
        new_name = request.get("new_name", "Clone")
        new_id = await registry.clone_workflow(workflow_id, new_name)
        
        if not new_id:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {"workflow_id": new_id, "original_id": workflow_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """
    Workflow sil
    """
    try:
        registry = get_workflow_registry()
        success = await registry.delete_workflow(workflow_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {"success": True, "workflow_id": workflow_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_templates():
    """
    Template'leri listele
    """
    try:
        from ..workflow.registry import WorkflowTemplate
        
        templates = WorkflowTemplate.get_templates()
        
        return {"templates": templates, "total": len(templates)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """
    Template detayı
    """
    try:
        from ..workflow.registry import WorkflowTemplate
        
        workflow = WorkflowTemplate.get_template(template_id)
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "template_id": template_id,
            "workflow": workflow.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
