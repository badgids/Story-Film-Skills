# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Install the optional Story-Film Pi Todo/resource-status extension."""
from __future__ import annotations
import argparse, os, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main() -> int:
    ap=argparse.ArgumentParser(description='Install the optional Story-Film Pi extension.')
    ap.add_argument('--extensions-dir', default=os.environ.get('PI_EXTENSIONS_DIR') or str(Path.home()/'.pi/agent/extensions'))
    a=ap.parse_args(); destdir=Path(a.extensions_dir).expanduser(); destdir.mkdir(parents=True,exist_ok=True)
    src=ROOT/'extensions/story-film-progress/index.ts'
    if not src.is_file(): print('ERROR missing extension source'); return 1
    dest=destdir/'story-film-progress.ts'; shutil.copy2(src,dest)
    legacy=destdir/'badgids-story-film-progress.ts'
    if legacy.is_file(): legacy.unlink()
    print(dest); return 0
if __name__=='__main__': raise SystemExit(main())
