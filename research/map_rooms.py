#!/usr/bin/env python3
"""BFS room mapper for PLATO MUD"""
import urllib.request, urllib.parse, json, time

BASE = "http://147.224.38.131:4042"
AGENT = "cartographer-test"

visited = {}
queue = ["harbor"]

while queue:
    room = queue.pop(0)
    if room in visited:
        continue
    try:
        # First move to the room
        url = f"{BASE}/move?agent={AGENT}&room={room}"
        with urllib.request.urlopen(url, timeout=15) as resp:
            move_data = json.loads(resp.read().decode())
        # Then look to get exit mappings
        url2 = f"{BASE}/look?agent={AGENT}"
        with urllib.request.urlopen(url2, timeout=15) as resp2:
            look_data = json.loads(resp2.read().decode())
        # Merge move data with look data (look has proper exit dict)
        data = {**move_data, **look_data, "exits": look_data.get("exits", move_data.get("exits", {}))}
        visited[room] = data
        exits = data.get("exits", {})
        if isinstance(exits, dict):
            for dest in exits.values():
                if dest not in visited and dest not in queue:
                    queue.append(dest)
        elif isinstance(exits, list):
            for dest in exits:
                if dest not in visited and dest not in queue:
                    queue.append(dest)
        time.sleep(0.3)
    except Exception as e:
        visited[room] = {"error": str(e), "room": room}

print(json.dumps(visited, indent=2))
