from __future__ import annotations

from pathlib import Path
import sys

EXCLUDED_DIRS = {"venv", ".venv", ".git", "__pycache__"}
OUTPUT_FILE = "ALL_PYTHON_SOURCES.txt"


def should_exclude(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)


def print_progress(current, total, bar_width=40):
    progress = current / total
    filled = int(bar_width * progress)
    bar = "#" * filled + "-" * (bar_width - filled)
    sys.stdout.write(f"\r[{bar}] {progress * 100:6.2f}% ({current}/{total} files)")
    sys.stdout.flush()


def main(src_dir: Path):
    py_files = sorted(
        p for p in src_dir.rglob("*.py") if p.is_file() and not should_exclude(p)
    )

    total_files = len(py_files)
    if total_files == 0:
        print("No Python files found.")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(
            "# ============================================================\n"
            "# CONCATENATED PYTHON SOURCE FILE\n"
            "# Each section is a file from the original directory tree\n"
            "# ============================================================\n\n"
        )

        for idx, path in enumerate(py_files, start=1):
            rel_path = path.relative_to(src_dir)

            out.write("\n")
            out.write("#" * 80 + "\n")
            out.write(f"# FILE: {rel_path}\n")
            out.write("#" * 80 + "\n\n")

            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = path.read_text(encoding="utf-8", errors="replace")

            out.write(content.rstrip())
            out.write("\n\n")

            print_progress(idx, total_files)

    print(f"\nDone. Wrote {total_files} files into {OUTPUT_FILE}")


if __name__ == "__main__":
    main(Path("."))
