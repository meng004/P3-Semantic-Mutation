#!/usr/bin/env python3
"""Direct driver for the paper_search_mcp tool functions.

The Cursor MCP transport for the `paper-search` server is unavailable in this
session (~/.cursor/mcp.json has a JSON syntax error), so we invoke the exact
same tool functions in-process. Same code path, same upstream APIs.

Usage:
    psearch.py <tool_name> <json_args>
    psearch.py search_dblp '{"query":"semantic mutation testing","max_results":30}'
"""
import asyncio
import inspect
import json
import sys

sys.path.insert(0, "/Users/limeng/paper-search-mcp")

from paper_search_mcp import server  # noqa: E402


def resolve(tool_name):
    obj = getattr(server, tool_name)
    # FastMCP may wrap the coroutine in a FunctionTool
    for attr in ("fn", "func", "__wrapped__"):
        if hasattr(obj, attr):
            return getattr(obj, attr)
    return obj


def main():
    tool_name = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    fn = resolve(tool_name)
    res = fn(**args)
    if inspect.isawaitable(res):
        res = asyncio.run(res)
    print(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
