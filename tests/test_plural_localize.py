import json
from pathlib import Path
import plistlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from localize_plurals import SOURCE_FILE, generate

class PluralLocalizationTests(unittest.TestCase):
    def fixture(self, base):
        src = base / "source" / SOURCE_FILE
        src.parent.mkdir(parents=True, exist_ok=True)
        source = {"foo": {
            "NSStringLocalizedFormatKey": "%#@items@",
            "items": {
                "NSStringFormatSpecTypeKey": "NSStringPluralRuleType",
                "NSStringFormatValueTypeKey": "d",
                "one": "%d tab",
                "other": "%d tabs",
            },
        }}
        src.write_bytes(plistlib.dumps(source))
        translations = base / "vi.json"
        translations.write_text(json.dumps({
            "locale": "vi", "source": SOURCE_FILE,
            "entries": {"foo": {"items": {"one": "%d tab", "other": "%d tab"}}},
        }), encoding="utf-8")
        return translations, source

    def test_round_trip_preserves_format_structures(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            translations, expected = self.fixture(base)
            summary = generate(base / "source", base / "out", translations)
            self.assertEqual(summary["translated_plural_keys"], 1)
            self.assertEqual(summary["translated_branches"], 2)
            dest = base / "out" / SOURCE_FILE.replace("/en.lproj/", "/vi.lproj/")
            compiled = plistlib.loads(dest.read_bytes())
            self.assertEqual(compiled["foo"]["NSStringLocalizedFormatKey"], "%#@items@")
            self.assertEqual(compiled["foo"]["items"]["NSStringFormatValueTypeKey"], "d")
            self.assertEqual(compiled["foo"]["items"]["other"], "%d tab")

    def test_reject_missing_keys_or_corrupt_placeholders(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            path, _ = self.fixture(base)
            payload = json.loads(path.read_text())
            payload["entries"] = {"missing": {"items": {"other": "%d tab"}}}
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                generate(base / "source", base / "out", path)
            payload["entries"] = {"foo": {"items": {"other": "%@ tab"}}}
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                generate(base / "source", base / "out", path)
