"""Prompt repository protocol and implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from vectraxis.models.common import generate_id
from vectraxis.models.prompt import Prompt

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@runtime_checkable
class PromptRepository(Protocol):
    async def create(self, prompt: Prompt) -> Prompt: ...
    async def get(self, prompt_id: str) -> Prompt | None: ...
    async def get_by_name(self, name: str) -> Prompt | None: ...
    async def list_all(self, tags: list[str] | None = None) -> list[Prompt]: ...
    async def update(self, prompt_id: str, **fields: object) -> Prompt | None: ...
    async def delete(self, prompt_id: str) -> bool: ...


class InMemoryPromptRepository:
    """In-memory implementation for testing."""

    def __init__(self) -> None:
        self._prompts: dict[str, Prompt] = {}

    async def create(self, prompt: Prompt) -> Prompt:
        if not prompt.id:
            prompt = prompt.model_copy(update={"id": generate_id()})
        self._prompts[prompt.id] = prompt
        return prompt

    async def get(self, prompt_id: str) -> Prompt | None:
        return self._prompts.get(prompt_id)

    async def get_by_name(self, name: str) -> Prompt | None:
        for p in self._prompts.values():
            if p.name == name:
                return p
        return None

    async def list_all(self, tags: list[str] | None = None) -> list[Prompt]:
        prompts = list(self._prompts.values())
        if tags:
            prompts = [p for p in prompts if any(t in p.tags for t in tags)]
        return prompts

    async def update(self, prompt_id: str, **fields: object) -> Prompt | None:
        existing = self._prompts.get(prompt_id)
        if existing is None:
            return None
        update_data = {k: v for k, v in fields.items() if v is not None}
        update_data["version"] = existing.version + 1
        updated = existing.model_copy(update=update_data)
        self._prompts[prompt_id] = updated
        return updated

    async def delete(self, prompt_id: str) -> bool:
        return self._prompts.pop(prompt_id, None) is not None


class PostgresPromptRepository:
    """PostgreSQL implementation using async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, prompt: Prompt) -> Prompt:
        from vectraxis.db.models import PromptRow

        row = PromptRow(
            id=prompt.id,
            name=prompt.name,
            description=prompt.description,
            system_prompt=prompt.system_prompt,
            user_prompt_template=prompt.user_prompt_template,
            model=prompt.model,
            agent_type=prompt.agent_type,
            output_json_schema=prompt.output_json_schema,
            temperature=prompt.temperature,
            max_tokens=prompt.max_tokens,
            variables=prompt.variables,
            tags=prompt.tags,
            version=prompt.version,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return self._row_to_prompt(row)

    async def get(self, prompt_id: str) -> Prompt | None:
        from sqlalchemy import select

        from vectraxis.db.models import PromptRow

        stmt = select(PromptRow).where(PromptRow.id == prompt_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._row_to_prompt(row) if row else None

    async def get_by_name(self, name: str) -> Prompt | None:
        from sqlalchemy import select

        from vectraxis.db.models import PromptRow

        stmt = select(PromptRow).where(PromptRow.name == name)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._row_to_prompt(row) if row else None

    async def list_all(self, tags: list[str] | None = None) -> list[Prompt]:
        from sqlalchemy import select

        from vectraxis.db.models import PromptRow

        stmt = select(PromptRow)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        prompts = [self._row_to_prompt(r) for r in rows]
        if tags:
            prompts = [p for p in prompts if any(t in p.tags for t in tags)]
        return prompts

    async def update(self, prompt_id: str, **fields: object) -> Prompt | None:
        from sqlalchemy import select

        from vectraxis.db.models import PromptRow

        stmt = select(PromptRow).where(PromptRow.id == prompt_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        for key, value in fields.items():
            if value is not None and hasattr(row, key):
                setattr(row, key, value)
        row.version = row.version + 1
        await self._session.commit()
        await self._session.refresh(row)
        return self._row_to_prompt(row)

    async def delete(self, prompt_id: str) -> bool:
        from sqlalchemy import delete

        from vectraxis.db.models import PromptRow

        stmt = delete(PromptRow).where(PromptRow.id == prompt_id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0  # type: ignore[attr-defined, no-any-return]

    @staticmethod
    def _row_to_prompt(row: object) -> Prompt:
        from vectraxis.db.models import PromptRow

        if not isinstance(row, PromptRow):
            raise TypeError(f"Expected PromptRow, got {type(row)}")
        return Prompt(
            id=row.id,
            name=row.name,
            description=row.description,
            system_prompt=row.system_prompt,
            user_prompt_template=row.user_prompt_template,
            model=row.model,
            agent_type=row.agent_type,
            output_json_schema=row.output_json_schema,
            temperature=row.temperature,
            max_tokens=row.max_tokens,
            variables=row.variables,
            tags=row.tags,
            version=row.version,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
