import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from localize import SOURCE_FILES, parse_strings, escape, formats, validate, generate
from patch_project import patch, remove_private_duck_sans
from patch_spm_lock import remove_private_ducksans_pin
from patch_unsigned_grdb import patch as patch_unsigned_grdb

class LocalizeTests(unittest.TestCase):
    def test_escapes(self):
        sample='/*comment*/\n"k\\\"1" = "Xin chào \\\"bạn\\\" \\nDòng 2";\n'
        self.assertEqual(parse_strings(sample),{'k"1':'Xin chào "bạn" \nDòng 2'})
        self.assertEqual(parse_strings(f'"a" = "{escape("Dòng 1\nDòng 2")}";')['a'],'Dòng 1\nDòng 2')
    def test_duplicate_keys(self):
        with self.assertRaises(ValueError):parse_strings('"x" = "A";\n"x" = "B";')
    def test_printf_placeholders(self):
        self.assertEqual(formats('Zoom (%d%%); %@'), formats('Thu phóng (%d%%); %@'))
        with self.assertRaises(ValueError):validate('Xóa %@?', 'Xóa %d?', 'delete')
    def test_generate_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); source=root/'source'; output=root/'output'
            for p in SOURCE_FILES:
                f=source/p;f.parent.mkdir(parents=True,exist_ok=True)
                f.write_text('"k" = "Hello %@";\n"u" = "Undo";\n',encoding='utf-8')
            payload={'locale':'vi','modules':{SOURCE_FILES[0]:{'k':'Xin chào %@'}}}
            translations=root/'vi.json';translations.write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
            coverage=generate(source,output,translations)
            self.assertEqual(coverage['translated'],1)
            self.assertEqual(coverage['total'],len(SOURCE_FILES)*2)
            result=(output/SOURCE_FILES[0].replace('/en.lproj/','/vi.lproj/')).read_text()
            self.assertIn('Xin chào %@',result)
            self.assertIn('"u" = "Undo";',result)
    def test_missing_key_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'src'
            for p in SOURCE_FILES:
                f=source/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text('"yes" = "Yes";',encoding='utf-8')
            t=root/'vi.json';t.write_text(json.dumps({'locale':'vi','modules':{SOURCE_FILES[0]:{'fake':'Không'}}}),encoding='utf-8')
            with self.assertRaises(ValueError):generate(source,root/'out',t)
    def test_font_removal_on_mock_pbx(self):
        mock="""		9FADFC4A2F5FC56400CA16F7 /* DuckSansFont in Frameworks */ = {isa = PBXBuildFile; productRef = 9FADFC492F5FC56400CA16F7 /* DuckSansFont */; };
		9FADFC492F5FC56400CA16F7 /* DuckSansFont */ = {
			isa = XCSwiftPackageProductDependency;
			package = 9FADFC482F5FC56400CA16F7 /* pkg */;
		};
		9FADFC482F5FC56400CA16F7 /* pkg */ = {
			isa = XCRemoteSwiftPackageReference;
			repositoryURL = "git@github.com:duckduckgo/private.git";
		};
				9FADFC4A2F5FC56400CA16F7 /* DuckSansFont in Frameworks */,
				9FADFC492F5FC56400CA16F7 /* DuckSansFont */,
				9FADFC482F5FC56400CA16F7 /* pkg */,
"""
        clean,n=remove_private_duck_sans(mock)
        self.assertEqual(n,6)
        self.assertNotIn('9FADFC48',clean)
        self.assertNotIn('9FADFC49',clean)
        self.assertNotIn('9FADFC4A',clean)
    def test_patch_idempotent(self):
        original='knownRegions = (\n\t\ten,\n\t\tfr,\n\t);'
        once,n=patch(original)
        twice,n2=patch(once)
        self.assertEqual(n,1)
        self.assertEqual(n2,0)
        self.assertEqual(once,twice)

    def test_swiftpm_lock_pin_cleanup(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'Package.resolved'
            data = {'version': 3, 'pins': [
                {'identity': 'native-apps-ducksans', 'state': {'version': '1.0.0'}},
                {'identity': 'good-public-package', 'state': {'version': '2.0.0'}},
            ]}
            path.write_text(json.dumps(data))
            self.assertEqual(remove_private_ducksans_pin(path), 1)
            self.assertEqual(remove_private_ducksans_pin(path), 0)
            remaining = json.loads(path.read_text())
            self.assertEqual([v['identity'] for v in remaining['pins']], ['good-public-package'])

    def test_markup_placeholders_preserved(self):
        validate('See [help](https://example.test/help) and {attachment}',
                 'Xem [trợ giúp](https://example.test/help) và {attachment}', 'help')
        with self.assertRaises(ValueError):
            validate('See [help](https://example.test/help)',
                     'Xem [trợ giúp](https://example.test/wrong)', 'bad-link')
        with self.assertRaises(ValueError):
            validate('Attach {attachment}', 'Đính kèm {file}', 'bad-token')

    def test_percent_discount_is_not_a_format_variable(self):
        self.assertEqual(formats('Get 25% off.'), {})
        self.assertEqual(formats('Save %d%% today'), {'%d': 1})
        validate('Get 25% off.', 'Giảm giá 25%.', 'discount')

    def test_unsigned_grdb_signing_guard(self):
        chunk = '/* Copy GRDB framework */ = {\\n'
        chunk += '  shellScript = "copy\\\\n/usr/bin/codesign --force --sign identity\\\\n";'
        chunk += '\\n\\t\\t};'
        fixed, changes = patch_unsigned_grdb(chunk)
        self.assertEqual(changes, 1)
        self.assertIn('Skipping GRDB framework signing in unsigned build', fixed)
        self.assertIn('/usr/bin/codesign', fixed)
        self.assertIn('\\\\nfi\\\\n', fixed)
        self.assertEqual(patch_unsigned_grdb(fixed), (fixed, 0))


if __name__=='__main__':unittest.main()
