#!/usr/bin/env python3
"""Generate a Vietnamese .lproj overlay from an upstream Apple .strings source tree.

Uses only Python stdlib; does not run Xcode, modify the original checkout in-place
unless --output points there, or promise that strings not in vi.json are translated.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

STRINGS_RE = re.compile(r'^\s*"((?:\\.|[^"\\])*)"\s*=\s*"((?:\\.|[^"\\])*)"\s*;\s*$', re.M)
FORMAT_RE = re.compile(r'%(?!%)(?:[1-9]\d*\$)?[-+ #0]*(?:\d+|\*)?(?:\.\d+)?(?:ll|hh|[hlzjt])?[@diuoxXfFeEgGcCsSpPaADUOX]')
MARKDOWN_LINK_RE = re.compile(r'\]\(([^)\n]+)\)')
NAMED_TOKEN_RE = re.compile(r'\{[A-Za-z][A-Za-z0-9_.-]*\}')
SOURCE_FILES = [
  'iOS/DuckDuckGo/UserInterfaceResources/en.lproj/Localizable.strings',
  'iOS/DuckDuckGo/en.lproj/InfoPlist.strings',
  'iOS/Widgets/en.lproj/Localizable.strings',
  'iOS/PacketTunnelProvider/en.lproj/Localizable.strings',
  'iOS/LocalPackages/SyncUI-iOS/Sources/SyncUI-iOS/Resources/en.lproj/Localizable.strings',
  'iOS/LocalPackages/SitePermissions/Sources/SitePermissions/Resources/en.lproj/Localizable.strings',
]


def unescape(value: str) -> str:
    """Decode escaping used in .strings without mangling raw UTF-8 characters."""
    mapping = {'n': '\n', 'r': '\r', 't': '\t', '"': '"', "'": "'", '\\': '\\'}
    return re.sub(r'\\(.)', lambda m: mapping.get(m.group(1), '\\' + m.group(1)), value)


def escape(value: str) -> str:
    return (value.replace('\\', '\\\\').replace('"', '\\"')
            .replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t'))


def parse_strings(text: str) -> dict[str, str]:
    pairs = STRINGS_RE.findall(text)
    if not pairs:
        raise ValueError('Không đọc được mục .strings nào')
    result = {}
    for raw_key, raw_value in pairs:
        key = unescape(raw_key)
        if key in result:
            raise ValueError(f'Trùng khóa: {key!r}')
        result[key] = unescape(raw_value)
    return result


def formats(value: str) -> Counter:
    value = value.replace('%%', '')
    return Counter(FORMAT_RE.findall(value))


def validate(source: str, translated: str, key: str) -> None:
    if not isinstance(translated, str) or not translated.strip():
        raise ValueError(f'{key}: Bản dịch rỗng hoặc không phải chuỗi')
    if formats(source) != formats(translated):
        raise ValueError(f'{key}: Sai biến định dạng: {formats(source)} != {formats(translated)}')
    if Counter(MARKDOWN_LINK_RE.findall(source)) != Counter(MARKDOWN_LINK_RE.findall(translated)):
        raise ValueError(f'{key}: Bản dịch làm thay đổi đích liên kết Markdown')
    if Counter(NAMED_TOKEN_RE.findall(source)) != Counter(NAMED_TOKEN_RE.findall(translated)):
        raise ValueError(f'{key}: Bản dịch làm thay đổi biến dạng {{name}}')


def generate(source_root: Path, out_root: Path, translations: Path, strict: bool=True) -> dict:
    payload = json.loads(translations.read_text(encoding='utf-8'))
    if payload.get('locale') != 'vi':
        raise ValueError('Locale phải là vi')
    overrides = payload['modules']
    unknown_modules = set(overrides) - set(SOURCE_FILES)
    if unknown_modules:
        raise ValueError(f'Mô-đun không được hỗ trợ: {sorted(unknown_modules)}')
    report = {'locale': 'vi', 'modules': {}, 'total': 0, 'translated': 0,
              'note': 'Translated counts only reviewed overrides; all other keys retain English.'}
    for path in SOURCE_FILES:
        src = source_root / path
        if not src.is_file():
            raise FileNotFoundError(f'Thiếu nguồn: {src}')
        english = parse_strings(src.read_text(encoding='utf-8-sig'))
        custom = overrides.get(path, {})
        absent = sorted(set(custom) - set(english))
        if absent and strict:
            raise ValueError(f'{path}: {len(absent)} khóa không tồn tại trong nguồn: {absent[:10]}')
        dest = out_root / path.replace('/en.lproj/', '/vi.lproj/')
        dest.parent.mkdir(parents=True, exist_ok=True)
        lines = ['/* Vietnamese localization; generated from pinned DuckDuckGo source. */',
                 '/* Missing translations explicitly use original English; see coverage.json. */', '']
        covered = 0
        for key, original in sorted(english.items()):
            vi = custom.get(key, original)
            if key in custom:
                validate(original, vi, key)
                covered += 1
            lines.append(f'"{escape(key)}" = "{escape(vi)}";')
        dest.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        report['modules'][path] = {'total':len(english), 'translated':covered,
                                   'fallback_english':len(english)-covered,
                                   'missing_override_keys': absent,
                                   'output':str(dest.relative_to(out_root))}
        report['total'] += len(english)
        report['translated'] += covered
        print(f'{dest.relative_to(out_root)}: {covered}/{len(english)} bản dịch')
    report['coverage_pct'] = round(100*report['translated']/report['total'], 2) if report['total'] else 0
    (out_root / 'coverage.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return report


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--source', type=Path, required=True, help='Gốc mã nguồn DuckDuckGo có iOS/...')
    cli.add_argument('--output', type=Path, required=True, help='Thư mục đầu ra không ghi vào nguồn')
    cli.add_argument('--translations', type=Path, default=Path(__file__).parents[1]/'translations/vi.json')
    cli.add_argument('--allow-missing-keys', action='store_true', help='Chỉ cho phép khi cập nhật khóa upstream')
    args = cli.parse_args()
    try:
        r=generate(args.source, args.output, args.translations, strict=not args.allow_missing_keys)
        print(f'Đã Việt hóa {r["translated"]}/{r["total"]} chuỗi ({r["coverage_pct"]}%).')
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as e:
        print(f'LỖI: {e}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
