from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def create_manifest(paths: tuple[Path, ...], version: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "software_version": version,
        "files": [
            {"path": path.as_posix(), "sha256": file_sha256(path)}
            for path in sorted(paths, key=lambda item: item.as_posix())
        ],
    }


def write_manifest(manifest: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_manifest(manifest_path: Path) -> tuple[bool, tuple[str, ...]]:
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for item in raw.get("files", []):
        path = Path(item["path"])
        if not path.is_file():
            failures.append(f"missing:{path.as_posix()}")
        elif file_sha256(path) != item["sha256"]:
            failures.append(f"changed:{path.as_posix()}")
    return not failures, tuple(failures)
