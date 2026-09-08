#!/usr/bin/env python3
from pathlib import Path
import os
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
DEFAULT_OUTPUT = ROOT / "dist" / "hermes-knowledge-kit.pyz"


def _entry(name: str, data: bytes) -> tuple[zipfile.ZipInfo, bytes]:
    info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (0o100644 << 16)
    return info, data


def main() -> int:
    output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    files = {
        path.relative_to(SOURCE).as_posix(): path.read_bytes()
        for path in SOURCE.rglob("*")
        if path.is_file() and path.suffix != ".pyc" and "__pycache__" not in path.parts
    }
    files["__main__.py"] = b"from hermes_knowledge_kit.cli import main\nraise SystemExit(main())\n"
    temporary = output.with_name(f".{output.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("wb") as stream:
            stream.write(b"#!/usr/bin/env python3\n")
            with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                for name in sorted(files):
                    info, data = _entry(name, files[name])
                    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    output.chmod(0o755)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
