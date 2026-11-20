#!/usr/bin/env python3
"""Entry program for the make.fun news-image-20261120 bounty.

Copies the pre-drawn poster (entry.png, made by draw_poster.py in this
repository) to the output directory. Standard library only, no network,
fully deterministic: the same input bytes are written every run.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def main():
    # MAKEFUN_OUTPUT_DIR is set by the grader; default to ./out locally.
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)
    print("wrote", dest)


if __name__ == "__main__":
    sys.exit(main())
