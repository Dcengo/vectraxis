"""Workflow repository protocol and implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from vectraxis.models.common import generate_id
from vectraxis.models.workflow import Workflow, WorkflowEdge, WorkflowNode

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@runtime_checkable
class WorkflowRepository(Protocol):
    async def create(self, workflow: Workflow) -> Workflow: ...
    async def get(self, workflow_id: str) -> Workflow | None: ...
    async def list_all(self) -> list[Workflow]: ...
    async def update(self, workflow_id: str, **fields: object) -> Workflow | None: ...
    async def delete(self, workflow_id: str) -> bool: ...


class InMemoryWorkflowRepository:
    """In-memory implementation for testing."""

    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}

    async def create(self, workflow: Workflow) -> Workflow:
        if not workflow.id:
            workflow = workflow.model_copy(update={"id": generate_id()})
        self._workflows[workflow.id] = workflow
        return workflow

    async def get(self, workflow_id: str) -> Workflow | None:
        return self._workflows.get(workflow_id)

    async def list_all(self) -> list[Workflow]:
        return list(self._workflows.values())

    async def update(self, workflow_id: str, **fields: object) -> Workflow | None:
        existing = self._workflows.get(workflow_id)
        if existing is None:
            return None
        update_data = {k: v for k, v in fields.items() if v is not None}
        update_data["version"] = existing.version + 1
        updated = existing.model_copy(update=update_data)
        self._workflows[workflow_id] = updated
        return updated

    async def delete(self, workflow_id: str) -> bool:
        return self._workflows.pop(workflow_id, None) is not None


class PostgresWorkflowRepository:
    """PostgreSQL implementation using async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, workflow: Workflow) -> Workflow:
        from vectraxis.db.models import WorkflowRow

        row = WorkflowRow(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            nodes=[n.model_dump() for n in workflow.nodes],
            edges=[e.model_dump() for e in workflow.edges],
            tags=workflow.tags,
            version=workflow.version,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return self._row_to_workflow(row)

    async def get(self, workflow_id: str) -> Workflow | None:
        from sqlalchemy import select

        from vectraxis.db.models import WorkflowRow

        stmt = select(WorkflowRow).where(WorkflowRow.id == workflow_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._row_to_workflow(row) if row else None

    async def list_all(self) -> list[Workflow]:
        from sqlalchemy import select

        from vectraxis.db.models import WorkflowRow

        stmt = select(WorkflowRow)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [self._row_to_workflow(r) for r in rows]

    async def update(self, workflow_id: str, **fields: object) -> Workflow | None:
        from sqlalchemy import select

        from vectraxis.db.models import WorkflowRow

        stmt = select(WorkflowRow).where(WorkflowRow.id == workflow_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        for key, value in fields.items():
            if value is not None:
                if key == "nodes" and isinstance(value, list):
                    row.nodes = [
                        n.model_dump() if hasattr(n, "model_dump") else n for n in value
                    ]
                elif key == "edges" and isinstance(value, list):
                    row.edges = [
                        e.model_dump() if hasattr(e, "model_dump") else e for e in value
                    ]
                elif hasattr(row, key):
                    setattr(row, key, value)
        row.version = row.version + 1
        await self._session.commit()
        await self._session.refresh(row)
        return self._row_to_workflow(row)

    async def delete(self, workflow_id: str) -> bool:
        from sqlalchemy import delete

        from vectraxis.db.models import WorkflowRow

        stmt = delete(WorkflowRow).where(WorkflowRow.id == workflow_id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0  # type: ignore[attr-defined, no-any-return]

    @staticmethod
    def _row_to_workflow(row: object) -> Workflow:
        from vectraxis.db.models import WorkflowRow

        if not isinstance(row, WorkflowRow):
            raise TypeError(f"Expected WorkflowRow, got {type(row)}")
        return Workflow(
            id=row.id,
            name=row.name,
            description=row.description,
            nodes=[WorkflowNode(**n) for n in row.nodes],
            edges=[WorkflowEdge(**e) for e in row.edges],
            tags=row.tags,
            version=row.version,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
