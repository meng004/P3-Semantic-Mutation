#!/usr/bin/env python3
"""Batch-run paper_search_mcp queries and print compact one-line records.

Reads a JSON list of {"tag":..., "tool":..., "args":{...}} from the file given
as argv[1]; prints TAG / title / authors / year / doi / venue / vol / pages.
"""
import asyncio
import inspect
import json
import sys

sys.path.insert(0, "/Users/limeng/paper-search-mcp")
from paper_search_mcp import server  # noqa: E402


def resolve(name):
    obj = getattr(server, name)
    for attr in ("fn", "func", "__wrapped__"):
        if hasattr(obj, attr):
            return getattr(obj, attr)
    return obj


def brief(p):
    extra = p.get("extra") or "{}"
    try:
        extra = eval(extra) if isinstance(extra, str) else extra
    except Exception:
        extra = {}
    if not isinstance(extra, dict):
        extra = {}
    date = str(p.get("published_date") or "")[:10]
    return " | ".join([
        (p.get("title") or "").strip()[:130],
        (p.get("authors") or "")[:110],
        date,
        p.get("doi") or "",
        str(extra.get("container_title") or p.get("source") or "")[:80],
        "v" + str(extra.get("volume") or ""),
        "i" + str(extra.get("issue") or ""),
        "p" + str(extra.get("page") or ""),
        str(extra.get("crossref_type") or p.get("categories") or "")[:22],
    ])


async def main():
    jobs = json.load(open(sys.argv[1]))
    for job in jobs:
        print(f"\n##### {job['tag']}  [{job['tool']}] {json.dumps(job['args'], ensure_ascii=False)}")
        try:
            fn = resolve(job["tool"])
            res = fn(**job["args"])
            if inspect.isawaitable(res):
                res = await res
        except Exception as e:
            print(f"  !! TOOL-ERROR: {type(e).__name__}: {e}")
            continue
        if isinstance(res, dict):
            res = [res]
        if not res:
            print("  (0 results)")
            continue
        for p in res:
            print("  - " + brief(p))


if __name__ == "__main__":
    asyncio.run(main())
