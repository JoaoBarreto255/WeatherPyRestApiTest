"""script for process user request"""

import asyncio
from datetime import datetime

import click

import sys
from pathlib import Path

print(Path(__file__).parent.parent.parent.absolute())
# type: ignore
sys.path.append(str(Path(Path(__file__).parent, "..", "..").absolute()))
