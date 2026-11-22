#!/usr/bin/env python3
"""Entry point: copy the pre-rendered news image to the output dir.

Standard library only. Deterministic: the same bytes every run.
The image itself is drawn by draw.py (run at build time); this file
only places it where the grader reads it.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst, os.path.getsize(dst), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
