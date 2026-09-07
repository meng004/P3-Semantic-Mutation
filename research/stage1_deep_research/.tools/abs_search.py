#!/usr/bin/env python3
"""Fetch abstracts for a list of titles via OpenAlex, falling back to Semantic Scholar."""
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


async def call(tool, **kw):
    fn = resolve(tool)
    res = fn(**kw)
    if inspect.isawaitable(res):
        res = await res
    return res


async def main():
    titles = json.load(open(sys.argv[1]))
    for t in titles:
        got = False
        for tool in ("search_openalex", "search_semantic"):
            try:
                res = await call(tool, query=t, max_results=3)
            except Exception as e:
                print(f"\n### {t}\n  !! {tool} ERROR {e}")
                continue
            for p in res or []:
                abst = (p.get("abstract") or "").strip()
                if abst and len(abst) > 120:
                    print(f"\n### {t}\n  [{tool}] {p.get('title')} | {p.get('doi')}\n  ABS: {abst[:1500]}")
                    got = True
                    break
            if got:
                break
        if not got:
            print(f"\n### {t}\n  (no abstract retrieved)")


if __name__ == "__main__":
    asyncio.run(main())
