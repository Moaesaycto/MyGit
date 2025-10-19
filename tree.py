
# ============================================================
#   COMP2041 ASSIGNMENT 2 SUBMISSION | TREE HELPER FILE
#   Stephen Lerantges (z5319858)
#   Term 2, 2024
# ------------------------------------------------------------
# This file contains basic tree functionality that is needed
# to track ancestry and commits for each branch.
# ============================================================


# ============================================================
#  Tree file structure
# ============================================================
#
#   For a tree like this:
#
#               0
#              / \
#             1  2
#               / \
#              3  4
#                  \
#                   5
#
# Would be stored as
# 1 0
# 2 0
# 3 2
# 4 2
# 5 4
#

import os
import networkx as nx

ROOT = ".mygit"
TREE_FILE = os.path.join(ROOT, "tree")
G = nx.DiGraph()


def load_tree():
    G.clear()
    if os.path.exists(TREE_FILE):
        with open(TREE_FILE, 'r') as f:
            for line in f:
                parts = list(map(int, line.strip().split()))
                child = parts[0]
                G.add_node(child)
                for parent in parts[1:]:
                    G.add_edge(parent, child)


def save_tree():
    with open(TREE_FILE, 'w') as f:
        for child in G.nodes:
            preds = list(G.predecessors(child))
            line = f"{child}" + (" " + " ".join(str(p)
                                 for p in preds) if preds else "")
            f.write(line + "\n")


def add_node(node: int, parents: list[int]):
    load_tree()
    if node in G:
        raise ValueError("Node already exists")
    G.add_node(node)
    for parent in parents:
        if parent not in G:
            raise ValueError(f"Parent {parent} does not exist")
        G.add_edge(parent, node)
    save_tree()


def find_lowest_common_ancestor(node1: int, node2: int) -> int | None:
    """
    Finds the lowest common ancestor between two nodes (commit numbers)

    Args:
        node1 (int): First node (commit number)
        node2 (int): Second node (commit number)

    Returns:
        int | None: Returns the commit number of the LCA. None if not found.
    """
    load_tree()
    try:
        return nx.lowest_common_ancestor(G, node1, node2)
    except nx.NetworkXError:
        return None


def add_edge_if_missing(parent: int, child: int) -> None:
    load_tree()
    if not G.has_node(child):
        raise ValueError(f"Child node {child} does not exist")
    if not G.has_node(parent):
        raise ValueError(f"Parent node {parent} does not exist")
    if not G.has_edge(parent, child):
        G.add_edge(parent, child)
        save_tree()


def get_all_reachable_commits(head_commit: int) -> list[int]:
    """
    Returns a topologically sorted list of all commits reachable from HEAD.
    Includes all ancestors (even from merged-in branches).
    """
    load_tree()
    head_commit = int(head_commit)

    if not G.has_node(head_commit):
        return []

    reachable = nx.ancestors(G, head_commit) | {head_commit}
    return sorted(reachable, reverse=True)


def get_parents(commit_no: int) -> list[int]:
    """
    Returns the parent commit numbers of the given commit.
    """
    load_tree()
    if not G.has_node(commit_no):
        return []
    return list(G.predecessors(commit_no))


def is_ancestor(ancestor: int, descendant: int) -> bool:
    """
    Returns True if `ancestor` is in the history of `descendant`.
    """
    load_tree()
    if not G.has_node(ancestor) or not G.has_node(descendant):
        return False
    return ancestor in nx.ancestors(G, descendant)
