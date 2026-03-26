"""Workflow CRUD + execution router."""

from fastapi import APIRouter, HTTPException

from vectraxis.api.dependencies import (
    get_data_source_repo,
    get_prompt_repo,
    get_retriever,
    get_settings,
    get_workflow_repo,
)
from vectraxis.models.common import generate_id
from vectraxis.models.workflow import (
    Workflow,
    WorkflowCreate,
    WorkflowRunResult,
    WorkflowUpdate,
)

router = APIRouter()


@router.post("/", response_model=Workflow, status_code=201)
async def create_workflow(body: WorkflowCreate) -> Workflow:
    repo = get_workflow_repo()
    workflow = Workflow(
        id=generate_id(),
        **body.model_dump(),
    )
    return await repo.create(workflow)


@router.get("/", response_model=list[Workflow])
async def list_workflows() -> list[Workflow]:
    repo = get_workflow_repo()
    return await repo.list_all()


@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str) -> Workflow:
    repo = get_workflow_repo()
    workflow = await repo.get(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow(workflow_id: str, body: WorkflowUpdate) -> Workflow:
    repo = get_workflow_repo()
    fields = body.model_dump(exclude_none=True)
    updated = await repo.update(workflow_id, **fields)
    if updated is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return updated


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str) -> None:
    repo = get_workflow_repo()
    deleted = await repo.delete(workflow_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workflow not found")


@router.post("/{workflow_id}/run", response_model=WorkflowRunResult)
async def run_workflow(workflow_id: str) -> WorkflowRunResult:
    workflow_repo = get_workflow_repo()
    workflow = await workflow_repo.get(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    from vectraxis.workflows.engine import WorkflowEngine

    settings = get_settings()
    engine = WorkflowEngine(
        prompt_repo=get_prompt_repo(),
        data_source_repo=get_data_source_repo(),
        retriever=get_retriever(),
        settings=settings,
    )
    return await engine.run(workflow)
