#!/usr/bin/env python3
"""Compatibility entry point for opt-in independent structured localization."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from seye.api.cli import main

if __name__ == '__main__':
    raise SystemExit(main())
