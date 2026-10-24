#!/usr/bin/env python3
"""Download only 6 upstream English localization inputs; no Git clone needed."""
from pathlib import Path
import argparse
import json
import sys
from urllib.request import Request, urlopen
from urllib.parse import quote
from localize import SOURCE_FILES

BASE = 'https://raw.githubusercontent.com/duckduckgo/apple-browsers'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('upstream'))
    ap.add_argument('--sha', default=None)
    a=ap.parse_args()
    if a.sha is None:
        a.sha=json.loads((Path(__file__).parents[1]/'upstream.json').read_text())['commit']
    if len(a.sha)!=40 or any(c not in '0123456789abcdef' for c in a.sha):
        sys.exit('SHA cần là 40 ký tự hex')
    for rel in SOURCE_FILES:
        url=f'{BASE}/{a.sha}/{quote(rel, safe="/")}'
        dest=a.source/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        req=Request(url,headers={'User-Agent':'DuckDuckGo-Vietnamese-Localization/0.1'})
        with urlopen(req,timeout=60) as response:
            body=response.read()
        body.decode('utf-8-sig')
        dest.write_bytes(body)
        print(f'{dest} ({len(body)} bytes)')

if __name__=='__main__':
    main()
