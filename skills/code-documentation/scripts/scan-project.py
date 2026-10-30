#!/usr/bin/env python3
"""scan-project.py - Codebase discovery script."""
import argparse
import os
import sys

DEFAULT_IGNORE_DIRS = {'.git', 'node_modules', '.venv', 'venv', 'dist', 'build', 'target', '__pycache__'}
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default=".")
    args = parser.parse_args()
    print("Scanning:", args.target)

if __name__ == "__main__":
    main()
