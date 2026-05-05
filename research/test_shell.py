#!/usr/bin/env python3
"""Test PLATO Shell command execution"""
import urllib.request, json

BASE = "http://147.224.38.131:8848"

# Test connecting an agent
url = f"{BASE}/connect?agent=shell-test&room=harbor"
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
