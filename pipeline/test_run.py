# -*- coding: utf-8 -*-
"""Quick test script"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.api import get_stats

r = get_stats(
    region="广东省",
    major="婴幼儿托育服务与管理",
    use_cache=False,
    details_limit=3,
)
from pipeline.config import CACHE_DIR
CACHE_DIR.mkdir(parents=True, exist_ok=True)
out = CACHE_DIR / "test_output.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(r, f, ensure_ascii=False, indent=2)
print("Done. Output:", str(out))
print("Stats region:", r.get("stats", {}).get("region"))
print("Stats national:", r.get("stats", {}).get("national"))
print("school_count (expected 189):", r["stats"]["region"]["school_count"])
