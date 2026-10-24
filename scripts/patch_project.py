#!/usr/bin/env python3
"""Insert 'vi' into knownRegions lists of DuckDuckGo iOS .pbxproj (idempotent).

This is not a substitute for Xcode resource membership verification.
"""
import argparse
from pathlib import Path
import re

PAT=re.compile(r'(knownRegions\s*=\s*\()(.*?)(\);)',re.S)

def patch(raw):
    replacements=0
    def repl(match):
        nonlocal replacements
        lines=match.group(2)
        if re.search(r'(?m)^\s*vi\s*,\s*$',lines):
            return match.group(0)
        replacements+=1
        return match.group(1)+lines.rstrip()+ '\n\t\t\t\tvi,\n\t\t\t'+match.group(3)
    out,n=PAT.subn(repl,raw)
    if n==0:
        raise ValueError('Không tìm thấy knownRegions trong .pbxproj')
    return out,replacements

def remove_private_duck_sans(raw: str) -> tuple[str, int]:
    """Remove references to private licensed DuckSansFont SPM package.

    This is the upstream-documented external-contributor workaround. If upstream
    changes these object IDs, fail loudly rather than modifying unrelated data.
    """
    build_id='9FADFC4A2F5FC56400CA16F7'
    product_id='9FADFC492F5FC56400CA16F7'
    remote_id='9FADFC482F5FC56400CA16F7'
    if not all(x in raw for x in (build_id, product_id, remote_id)):
        raise ValueError('Không nhận diện được dependency DuckSansFont (upstream có thể đã đổi)')
    # Remove the three object definitions first, then their list references.
    changed=0
    for obj_id in (build_id,product_id,remote_id):
        if obj_id == build_id:
            pattern=re.compile(r'^\t\t'+obj_id+r' /\*[^\n]*\*/ = \{[^\n]*\};\n',re.M)
        else:
            pattern=re.compile(r'^\t\t'+obj_id+r' /\*[^\n]*\*/ = \{\n.*?^\t\t\};\n',re.M|re.S)
        raw,n=pattern.subn('',raw,count=1)
        if n != 1:
            raise ValueError(f'Không thể xóa object DuckSansFont: {obj_id}')
        changed+=n
    for obj_id in (build_id,product_id,remote_id):
        raw,n=re.subn(r'^\s*'+obj_id+r' /\*[^\n]*\*/[,]?\n','\n',raw,flags=re.M)
        if n != 1:
            raise ValueError(f'Không thể xóa tham chiếu font: {obj_id}; tìm được {n}')
        changed+=n
    if any(x in raw for x in (build_id,product_id,remote_id)):
        raise ValueError('Vẫn còn tham chiếu DuckSansFont')
    return raw,changed


def main():
    p=argparse.ArgumentParser()
    p.add_argument('project_file',type=Path)
    p.add_argument('--remove-private-font',action='store_true')
    a=p.parse_args()
    before=a.project_file.read_text(encoding='utf-8')
    after,count=patch(before)
    if a.remove_private_font:
        after,removed=remove_private_duck_sans(after)
        print(f'Đã loại {removed} mục liên quan gói DuckSansFont độc quyền')
    if after != before:
        a.project_file.write_text(after,encoding='utf-8')
    print(f'knownRegions: {count} mục mới vi; project={a.project_file}')

if __name__=='__main__':
    main()
