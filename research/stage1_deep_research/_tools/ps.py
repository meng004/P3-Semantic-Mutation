#!/usr/bin/env python3
"""Direct driver for the locally-installed paper-search-mcp searchers.

The `user-paper-search` MCP namespace failed to load in this session because
~/.cursor/mcp.json contains a JSON syntax error (missing comma before the
"undermind" entry). This driver calls the exact same searcher classes that the
MCP tools wrap (paper_search_mcp.academic_platforms.*), so project rule §7
(paper-search-first) is satisfied without degrading to WebSearch.

Usage:
    python ps.py <tool> "<query>" [max_results]
    python ps.py doi <doi>
    python ps.py batch <jsonfile>
"""
import json
import sys
import time
import traceback

sys.path.insert(0, "/Users/limeng/paper-search-mcp")

TOOLS = {}


def _load():
    from paper_search_mcp.academic_platforms.arxiv import ArxivSearcher
    from paper_search_mcp.academic_platforms.crossref import CrossRefSearcher
    from paper_search_mcp.academic_platforms.dblp import DBLPSearcher
    from paper_search_mcp.academic_platforms.openalex import OpenAlexSearcher
    from paper_search_mcp.academic_platforms.semantic import SemanticSearcher
    from paper_search_mcp.academic_platforms.google_scholar import GoogleScholarSearcher

    TOOLS.update({
        "search_dblp": DBLPSearcher(),
        "search_arxiv": ArxivSearcher(),
        "search_crossref": CrossRefSearcher(),
        "search_openalex": OpenAlexSearcher(),
        "search_semantic": SemanticSearcher(),
        "search_google_scholar": GoogleScholarSearcher(),
    })


def fmt(p):
    d = p.to_dict() if hasattr(p, "to_dict") else dict(p)
    ex = getattr(p, "extra", None) or d.get("extra") or {}
    if not isinstance(ex, dict):
        ex = {}
    pd = getattr(p, "published_date", None)
    year = getattr(pd, "year", None)
    if year in (None, 1970):
        year = (str(d.get("published") or d.get("year") or ""))[:4]
    return {
        "title": (d.get("title") or "").strip(),
        "authors": d.get("authors") or [],
        "year": str(year or ""),
        "venue": ex.get("container_title") or ex.get("venue") or d.get("journal")
                 or d.get("venue") or d.get("source") or "",
        "vol": ex.get("volume", ""),
        "issue": ex.get("issue", ""),
        "page": ex.get("page", ""),
        "type": (d.get("categories") or [""])[0] if d.get("categories") else "",
        "doi": d.get("doi") or "",
        "url": d.get("url") or "",
        "citations": d.get("citations") or d.get("citation_count") or "",
        "abstract": (d.get("abstract") or ""),
    }


def run(tool, query, n=10, **kw):
    t0 = time.time()
    try:
        res = TOOLS[tool].search(query, max_results=n, **kw)
        return {"tool": tool, "query": query, "elapsed": round(time.time() - t0, 2),
                "status": "ok", "n": len(res), "results": [fmt(p) for p in res]}
    except Exception as e:
        return {"tool": tool, "query": query, "elapsed": round(time.time() - t0, 2),
                "status": "error", "error": f"{type(e).__name__}: {e}",
                "trace": traceback.format_exc()[-500:], "results": []}


def doi(d):
    t0 = time.time()
    try:
        p = TOOLS["search_crossref"].get_paper_by_doi(d)
        return {"tool": "get_crossref_paper_by_doi", "query": d,
                "elapsed": round(time.time() - t0, 2),
                "status": "ok" if p else "notfound",
                "results": [fmt(p)] if p else []}
    except Exception as e:
        return {"tool": "get_crossref_paper_by_doi", "query": d,
                "status": "error", "error": f"{type(e).__name__}: {e}", "results": []}


if __name__ == "__main__":
    _load()
    mode = sys.argv[1]
    out = []
    if mode == "doi":
        out.append(doi(sys.argv[2]))
    elif mode == "batch":
        jobs = json.load(open(sys.argv[2]))
        for j in jobs:
            if j.get("mode") == "doi":
                out.append(doi(j["q"]))
            else:
                out.append(run(j["tool"], j["q"], j.get("n", 10)))
            time.sleep(j.get("sleep", 1.0))
    else:
        out.append(run(mode, sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10))
    print(json.dumps(out, indent=1, ensure_ascii=False))
