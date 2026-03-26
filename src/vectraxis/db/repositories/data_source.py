"""DataSource repository protocol and implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from vectraxis.models.ingestion import DataSource, DataSourceType

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@runtime_checkable
class DataSourceRepository(Protocol):
    async def create(self, source: DataSource) -> DataSource: ...
    async def get(self, source_id: str) -> DataSource | None: ...
    async def list_all(self) -> list[DataSource]: ...
    async def delete(self, source_id: str) -> bool: ...


class InMemoryDataSourceRepository:
    """In-memory implementation for testing."""

    def __init__(self) -> None:
        self._sources: dict[str, DataSource] = {}

    async def create(self, source: DataSource) -> DataSource:
        self._sources[source.id] = source
        return source

    async def get(self, source_id: str) -> DataSource | None:
        return self._sources.get(source_id)

    async def list_all(self) -> list[DataSource]:
        return list(self._sources.values())

    async def delete(self, source_id: str) -> bool:
        return self._sources.pop(source_id, None) is not None


class PostgresDataSourceRepository:
    """PostgreSQL implementation using async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, source: DataSource) -> DataSource:
        from vectraxis.db.models import DataSourceRow

        row = DataSourceRow(
            id=source.id,
            name=source.name,
            source_type=source.source_type.value,
            file_path=source.file_path,
            metadata_=source.metadata,
            record_count=source.record_count,
        )
        self._session.add(row)
        await self._session.commit()
        return source

    async def get(self, source_id: str) -> DataSource | None:
        from sqlalchemy import select

        from vectraxis.db.models import DataSourceRow

        stmt = select(DataSourceRow).where(DataSourceRow.id == source_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return DataSource(
            id=row.id,
            name=row.name,
            source_type=DataSourceType(row.source_type),
            file_path=row.file_path,
            metadata=row.metadata_,
            record_count=row.record_count,
        )

    async def list_all(self) -> list[DataSource]:
        from sqlalchemy import select

        from vectraxis.db.models import DataSourceRow

        stmt = select(DataSourceRow)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [
            DataSource(
                id=r.id,
                name=r.name,
                source_type=DataSourceType(r.source_type),
                file_path=r.file_path,
                metadata=r.metadata_,
                record_count=r.record_count,
            )
            for r in rows
        ]

    async def delete(self, source_id: str) -> bool:
        from sqlalchemy import delete

        from vectraxis.db.models import DataSourceRow

        stmt = delete(DataSourceRow).where(DataSourceRow.id == source_id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0  # type: ignore[attr-defined, no-any-return]
