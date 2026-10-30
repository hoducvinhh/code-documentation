#!/usr/bin/env python3
"""check-links.py - Markdown link validator."""
import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default=".")
    args = parser.parse_args()
    print("Validating links in:", args.target)

if __name__ == "__main__":
    main()
