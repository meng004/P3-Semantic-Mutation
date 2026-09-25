"""Independent certifier for one NetworkX install. Does not read MR verdicts."""
from __future__ import annotations

import sys
import traceback

import networkx as nx
from networkx.algorithms.shortest_paths.dense import (
    floyd_warshall_predecessor_and_distance,
)


def edge_weights(G):
    weights = []
    for u, v, data in G.edges(data=True):
        weights.append(data["weight"])
    return weights


def main() -> int:
    print("commit_expected", sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN")
    print("python", sys.version.replace("\n", " "))
    print("networkx_file", nx.__file__)
    print("networkx_version", getattr(nx, "__version__", "UNKNOWN"))

    control = nx.Graph()
    control.add_edge(0, 1, weight=1)
    try:
        _pred_c, dist_c = floyd_warshall_predecessor_and_distance(control)
        control_self = dist_c[0][0]
        print("control_dist00", control_self)
        if control_self != 0:
            print("verdict", "EXEC_FAIL")
            print("reason", "control graph dist[0][0] is not 0")
            return 2
    except Exception:
        traceback.print_exc()
        print("verdict", "EXEC_FAIL")
        return 2

    target = nx.Graph()
    target.add_edge(0, 0, weight=5)
    weights = edge_weights(target)
    print("target_weights", weights)
    if any(w < 0 for w in weights):
        print("verdict", "CERT_INCONCLUSIVE")
        print("reason", "negative weight is outside this requirement")
        return 2
    expected = 0
    try:
        _pred, dist = floyd_warshall_predecessor_and_distance(target)
        observed = dist[0][0]
    except Exception:
        traceback.print_exc()
        print("verdict", "EXEC_FAIL")
        return 2
    print("expected_dist00", expected)
    print("observed_dist00", observed)
    print("abs_diff", abs(observed - expected))
    if observed == expected:
        print("verdict", "CERT_HOLD")
        return 0
    print("verdict", "CERT_BREAK")
    return 1


if __name__ == "__main__":
    sys.exit(main())
