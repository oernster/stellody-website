from __future__ import annotations

from pathlib import Path


def test_all_python_files_are_at_most_400_lines() -> None:
    project_root = Path(__file__).resolve().parents[1]

    ignore_dirs = {
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        "build",
        "dist",
    }

    py_files = [
        p
        for p in project_root.rglob("*.py")
        if not any(part in ignore_dirs for part in p.parts)
    ]

    violations: list[tuple[int, Path]] = []
    for path in py_files:
        # Use a forgiving read to avoid failing the style test on file-encoding issues.
        line_count = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
        if line_count > 400:
            violations.append((line_count, path))

    assert not violations, "Python files must be <= 400 lines. Violations:\n" + "\n".join(
        f"{count} {path.relative_to(project_root)}" for count, path in sorted(violations, reverse=True)
    )

