#!/usr/bin/env python3
"""scan-project.py - Codebase discovery script."""
import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default=".")
    args = parser.parse_args()
    print("Scanning:", args.target)

if __name__ == "__main__":
    main()
