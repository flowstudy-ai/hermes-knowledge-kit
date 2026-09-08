#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys
import tempfile
import zipapp

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
DEFAULT_OUTPUT = ROOT / "dist" / "hermes-knowledge-kit.pyz"


def main() -> int:
    output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="hkk-build-") as tmp:
        stage = Path(tmp) / "app"
        shutil.copytree(SOURCE, stage, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (stage / "__main__.py").write_text("from hermes_knowledge_kit.cli import main\nraise SystemExit(main())\n", encoding="utf-8")
        zipapp.create_archive(
            stage,
            target=output,
            interpreter="/usr/bin/env python3",
            compressed=True,
        )
    output.chmod(0o755)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
