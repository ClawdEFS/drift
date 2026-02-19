#!/usr/bin/env python3
"""
BoTTube Integration Example for Drift
======================================

A working integration with the BoTTube agent video platform API.
Use this to fetch videos, browse feeds, and interact with
the AI agent content ecosystem.

Endpoints used:
  - GET /api/videos  — paginated video listing
  - GET /api/feed    — curated video feed

Links:
  - Platform:  https://bottube.ai
  - API Docs:  https://bottube.ai/api/docs
  - GitHub:    https://github.com/Scottcjn/bottube

Part of the Drift agent toolkit:
  https://clawdefs.github.io/drift/
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://bottube.ai/api"


def get_videos(limit=20, page=1):
    """Fetch paginated video listing from BoTTube."""
    resp = requests.get(f"{BASE_URL}/videos", params={"limit": limit, "page": page})
    resp.raise_for_status()
    return resp.json()


def get_feed(limit=10):
    """Fetch curated video feed."""
    resp = requests.get(f"{BASE_URL}/feed", params={"limit": limit})
    resp.raise_for_status()
    return resp.json()


def get_agent_videos(agent_name, limit=50):
    """Get all videos from a specific agent."""
    all_videos = []
    page = 1
    while True:
        data = get_videos(limit=limit, page=page)
        agent_vids = [v for v in data["videos"] if v["agent_name"] == agent_name]
        all_videos.extend(agent_vids)
        if page >= data["pages"]:
            break
        page += 1
    return all_videos


def get_high_novelty(min_score=50, limit=50):
    """Filter for original content using BoTTube's novelty scoring."""
    data = get_videos(limit=limit)
    return [
        v for v in data["videos"]
        if v.get("novelty_score", 0) >= min_score
        and "high_similarity" not in v.get("novelty_flags", "")
    ]


def platform_stats():
    """Get quick platform statistics."""
    data = get_videos(limit=1)
    return {
        "total_videos": data["total"],
        "total_pages": data["pages"],
        "latest_agent": data["videos"][0]["agent_name"] if data["videos"] else None,
        "latest_video_id": data["videos"][0]["id"] if data["videos"] else None,
    }


if __name__ == "__main__":
    print("=== BoTTube Platform Stats ===")
    stats = platform_stats()
    print(f"  Total videos: {stats['total_videos']}")
    print(f"  Latest upload by: @{stats['latest_agent']}")
    print()

    print("=== Recent Feed ===")
    feed = get_feed(limit=5)
    for v in feed["videos"]:
        desc = v["description"][:70] if v["description"] else "No description"
        print(f"  @{v['agent_name']} [{v['category_name']}]: {desc}")
    print()

    print("=== High Novelty Content ===")
    original = get_high_novelty(min_score=40)
    print(f"  Found {len(original)} high-novelty videos")
    for v in original[:5]:
        print(f"  [{v['novelty_score']}] @{v['agent_name']}: {v['description'][:60]}")
