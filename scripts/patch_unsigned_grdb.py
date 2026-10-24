#!/usr/bin/env python3
"""Skip ONLY GRDB.framework's explicit codesign phase for unsigned CI builds.

Keep framework copying intact; do not alter signed-release behavior.
"""
import argparse
from pathlib import Path

PHASE_MARKER = "/* Copy GRDB framework */ = {"
SCRIPT_END = r'\n";'
SIGN_COMMAND = "/usr/bin/codesign"
UNSIGNED_GUARD = (
    r'if [ \"\$\{CODE_SIGNING_ALLOWED\}\" = \"NO\" ]; then\n'
    r'    echo \"Skipping GRDB framework signing in unsigned build\"\n'
    r'else\n'
)
# Dollar-brace expressions are shell variables and must not be backslash escaped
UNSIGNED_GUARD = UNSIGNED_GUARD.replace(r'\$\{', '${').replace(r'\}', '}')


def patch(raw: str) -> tuple[str, int]:
    start = raw.find(PHASE_MARKER)
    if start < 0:
        raise ValueError("Cannot find upstream GRDB shell build phase")
    end = raw.find("\n\t\t};", start)
    if end < 0:
        raise ValueError("Unterminated GRDB shell build phase")
    chunk = raw[start:end]
    if "Skipping GRDB framework signing in unsigned build" in chunk:
        return raw, 0
    if chunk.count(SIGN_COMMAND) != 1 or not chunk.endswith(SCRIPT_END):
        raise ValueError("Upstream GRDB phase changed; refusing unsafe patch")
    chunk = chunk.replace(SIGN_COMMAND, UNSIGNED_GUARD + SIGN_COMMAND, 1)
    chunk = chunk[:-len(SCRIPT_END)] + r'\nfi\n";'
    return raw[:start] + chunk + raw[end:], 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_file", type=Path)
    args = parser.parse_args()
    original = args.project_file.read_text(encoding="utf-8")
    modified, count = patch(original)
    if modified != original:
        args.project_file.write_text(modified, encoding="utf-8")
    print(f"Patched {count} GRDB unsigned signing guard(s)")


if __name__ == "__main__":
    main()
