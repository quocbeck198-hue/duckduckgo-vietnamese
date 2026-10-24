#!/usr/bin/env python3
"""Create safe Vietnamese .stringsdict plural resources from pinned upstream.

Only user-facing plural values change. Format selectors, variable names and
the parent plist structure remain identical to the upstream source.
"""
import argparse
import copy
import json
from pathlib import Path
import plistlib
from localize import validate

SOURCE_FILE = "iOS/DuckDuckGo/UserInterfaceResources/en.lproj/Localizable.stringsdict"

def generate(source_root: Path, output_root: Path, translations: Path) -> dict:
    src = source_root / SOURCE_FILE
    if not src.exists():
        raise FileNotFoundError(f"Missing plural source: {src}")
    raw = plistlib.loads(src.read_bytes())
    payload = json.loads(translations.read_text(encoding="utf-8"))
    if payload.get("locale") != "vi" or payload.get("source") != SOURCE_FILE:
        raise ValueError("Unexpected locale or source")
    override = payload.get("entries", {})
    if not isinstance(override, dict):
        raise ValueError("Plural translations must be a dictionary")
    extra = set(override) - set(raw)
    if extra:
        raise ValueError(f"Unknown plural source keys: {sorted(extra)}")
    output = copy.deepcopy(raw)
    count = 0
    for key, variables in override.items():
        if not isinstance(variables, dict):
            raise ValueError(f"{key}: invalid plural variable dictionary")
        for variable, categories in variables.items():
            reference = raw[key].get(variable)
            if not isinstance(reference, dict) or reference.get("NSStringFormatSpecTypeKey") != "NSStringPluralRuleType":
                raise ValueError(f"{key}: unknown or nonplural variable {variable}")
            if not isinstance(categories, dict):
                raise ValueError(f"{key}.{variable}: categories must be a dictionary")
            for category, text in categories.items():
                if category not in ("zero", "one", "two", "few", "many", "other") or category not in reference:
                    raise ValueError(f"{key}.{variable}: unknown source category {category}")
                validate(reference[category], text, f"{key}.{variable}.{category}")
                output[key][variable][category] = text
                count += 1
    dest = output_root / SOURCE_FILE.replace("/en.lproj/", "/vi.lproj/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(plistlib.dumps(output, fmt=plistlib.FMT_XML, sort_keys=False))
    # plistlib round-trip is a prerequisite before publishing a broken resource.
    assert plistlib.loads(dest.read_bytes()) == output
    report = {
        "locale": "vi",
        "source": SOURCE_FILE,
        "source_plural_keys": len(raw),
        "translated_plural_keys": len(override),
        "translated_branches": count,
        "note": "Other branches retain original English without changing plural rules.",
        "output": str(dest.relative_to(output_root)),
    }
    (output_root / "plural_coverage.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--translations", type=Path, default=Path(__file__).resolve().parents[1] / "translations/plurals_vi.json")
    args = ap.parse_args()
    report = generate(args.source, args.output, args.translations)
    print(f"Plural localizations: {report['translated_plural_keys']}/{report['source_plural_keys']} keys; {report['translated_branches']} branches")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
