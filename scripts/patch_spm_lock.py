#!/usr/bin/env python3
"""Remove the private Duck Sans SwiftPM pin for external contributor builds.

The source project's pbxproj must also have its matching product and remote
package references removed. We only modify an explicit known identity.
"""
import argparse
import json
from pathlib import Path


def remove_private_ducksans_pin(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    pins = payload.get("pins")
    if not isinstance(pins, list):
        raise ValueError("Missing SwiftPM pins array")
    kept = [p for p in pins if p.get("identity") != "native-apps-ducksans"]
    removed = len(pins) - len(kept)
    if removed > 1:
        raise ValueError("Multiple private Duck Sans pins: refusing to continue")
    if removed:
        payload["pins"] = kept
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return removed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("resolved_file", type=Path)
    args = parser.parse_args()
    print(f"Removed {remove_private_ducksans_pin(args.resolved_file)} private Duck Sans pin(s)")


if __name__ == "__main__":
    main()
