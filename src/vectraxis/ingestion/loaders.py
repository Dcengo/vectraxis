"""Ingestion loaders for reading data from various file formats."""

import csv
import json
from pathlib import Path
from typing import Protocol, runtime_checkable

from vectraxis.models.ingestion import RawRecord


@runtime_checkable
class Loader(Protocol):
    """Protocol that all loaders must implement."""

    def load(self, source: Path, source_id: str) -> list[RawRecord]: ...


class CSVLoader:
    """Loads records from a CSV file. Each row becomes a RawRecord."""

    def load(self, source: Path, source_id: str) -> list[RawRecord]:
        if not source.exists():
            raise FileNotFoundError(f"CSV file not found: {source}")

        records: list[RawRecord] = []
        with source.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for index, row in enumerate(reader):
                records.append(
                    RawRecord(
                        source_id=source_id,
                        data=dict(row),
                        record_index=index,
                    )
                )
        return records


class JSONLoader:
    """Loads records from a JSON file containing an array of objects."""

    def load(self, source: Path, source_id: str) -> list[RawRecord]:
        if not source.exists():
            raise FileNotFoundError(f"JSON file not found: {source}")

        try:
            with source.open(encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {source}: {exc}") from exc

        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            msg = (
                f"Expected a JSON array or object in {source}, "
                f"got {type(data).__name__}"
            )
            raise ValueError(msg)

        records: list[RawRecord] = []
        for index, item in enumerate(data):
            records.append(
                RawRecord(
                    source_id=source_id,
                    data=item,
                    record_index=index,
                )
            )
        return records


class TextDocumentLoader:
    """Loads a text file as a single RawRecord with data={"content": <text>}."""

    def load(self, source: Path, source_id: str) -> list[RawRecord]:
        if not source.exists():
            raise FileNotFoundError(f"Text file not found: {source}")

        content = source.read_text(encoding="utf-8")
        return [
            RawRecord(
                source_id=source_id,
                data={"content": content},
                record_index=0,
            )
        ]
