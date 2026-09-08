#!/usr/bin/env python3
from pathlib import Path
import re
import sys

SKIP_DIRS = {".git", ".sandbox", "__pycache__", "dist", "build", ".venv"}
BAD_NAMES = {".env", "auth.json", "credentials.json"}
BAD_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".key", ".pem"}
PATTERNS = [
    re.compile(("-----BEGIN " + "(?:RSA |EC |OPENSSH )?PRIVATE KEY-----").encode()),
    re.compile(("gh" + "p_[A-Za-z0-9]{30,}").encode()),
    re.compile(("AKIA" + "[A-Z0-9]{16}").encode()),
    re.compile(("sk-" + "[A-Za-z0-9_-]{24,}").encode()),
]
PRIVATE_TERMS = [term.encode() for term in ("PM" + "MG", "RE" + "DS", "Barba" + "cena")]


def scan(root: Path) -> list[str]:
    findings = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts) or not path.is_file():
            continue
        if path.name in BAD_NAMES or path.suffix.lower() in BAD_SUFFIXES:
            findings.append(f"arquivo proibido: {rel.as_posix()}")
            continue
        try:
            data = path.read_bytes()
        except OSError:
            findings.append(f"arquivo ilegível: {rel.as_posix()}")
            continue
        if b"\x00" in data[:4096]:
            continue
        if any(pattern.search(data) for pattern in PATTERNS):
            findings.append(f"padrão de segredo: {rel.as_posix()}")
        if any(term in data for term in PRIVATE_TERMS):
            findings.append(f"termo privado bloqueado: {rel.as_posix()}")
    return findings


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    findings = scan(root)
    if findings:
        print("RELEASE_SCAN FAIL")
        for finding in findings:
            print(finding)
        return 1
    print("RELEASE_SCAN PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
