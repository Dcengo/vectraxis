"""Prompt CRUD router."""

from fastapi import APIRouter, HTTPException, Query

from vectraxis.api.dependencies import get_prompt_repo
from vectraxis.models.common import generate_id
from vectraxis.models.prompt import Prompt, PromptCreate, PromptUpdate

router = APIRouter()


@router.post("/", response_model=Prompt, status_code=201)
async def create_prompt(body: PromptCreate) -> Prompt:
    repo = get_prompt_repo()
    prompt = Prompt(
        id=generate_id(),
        **body.model_dump(),
    )
    return await repo.create(prompt)


@router.get("/", response_model=list[Prompt])
async def list_prompts(
    tags: str | None = Query(
        None,
        description="Comma-separated tags to filter by",
    ),
) -> list[Prompt]:
    repo = get_prompt_repo()
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    return await repo.list_all(tags=tag_list)


@router.get("/{prompt_id}", response_model=Prompt)
async def get_prompt(prompt_id: str) -> Prompt:
    repo = get_prompt_repo()
    prompt = await repo.get(prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.put("/{prompt_id}", response_model=Prompt)
async def update_prompt(prompt_id: str, body: PromptUpdate) -> Prompt:
    repo = get_prompt_repo()
    fields = body.model_dump(exclude_none=True)
    updated = await repo.update(prompt_id, **fields)
    if updated is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated


@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt(prompt_id: str) -> None:
    repo = get_prompt_repo()
    deleted = await repo.delete(prompt_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prompt not found")
