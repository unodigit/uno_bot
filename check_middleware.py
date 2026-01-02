#!/usr/bin/env python3
import sys
sys.path.append('/media/DATA/projects/autonomous-coding-uno-bot/unobot/.venv/lib/python3.11/site-packages')

from deepagents import middleware

print("Available middleware:")
print(dir(middleware))

print("\nAll members:")
for name in dir(middleware):
    if not name.startswith('_'):
        obj = getattr(middleware, name)
        print(f"  {name}: {type(obj)}")
