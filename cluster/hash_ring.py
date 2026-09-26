"""
Consistent Hash Ring Implementation
Provides consistent hashing with virtual nodes for distributed object placement,
deterministic failover, and minimal key migration during cluster resizing.
"""
import hashlib
import bisect
from typing import List, Dict, Set


class ConsistentHashRing:
    def __init__(self, vnodes: int = 64):
        self.vnodes = vnodes
        self.ring: List[int] = []  # Sorted list of token hashes
        self.token_to_node: Dict[int, str] = {}  # token -> node_id
        self.nodes: Set[str] = set()

    def _hash(self, key: str) -> int:
        """Computes integer MD5 hash for consistent placement on a 2^128 ring."""
        return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)

    def add_node(self, node_id: str):
        """Adds a physical node to the ring with multiple virtual nodes."""
        if node_id in self.nodes:
            return
        self.nodes.add(node_id)
        for i in range(self.vnodes):
            token = self._hash(f"{node_id}#vnode-{i}")
            self.ring.append(token)
            self.token_to_node[token] = node_id
        self.ring.sort()

    def remove_node(self, node_id: str):
        """Removes a physical node and its virtual nodes from the ring."""
        if node_id not in self.nodes:
            return
        self.nodes.remove(node_id)
        tokens_to_remove = set()
        for i in range(self.vnodes):
            token = self._hash(f"{node_id}#vnode-{i}")
            tokens_to_remove.add(token)

        self.ring = [t for t in self.ring if t not in tokens_to_remove]
        for t in tokens_to_remove:
            self.token_to_node.pop(t, None)

    def get_nodes(self, key: str, count: int = 3, active_nodes: Set[str] = None) -> List[str]:
        """
        Returns `count` distinct physical nodes for a given key.
        Traverses clockwise on the ring from the key's token position.
        """
        if not self.ring:
            return []

        allowed = active_nodes if active_nodes is not None else self.nodes
        if not allowed:
            return []

        key_token = self._hash(key)
        idx = bisect.bisect_right(self.ring, key_token)
        total_tokens = len(self.ring)

        selected_nodes: List[str] = []
        seen = set()

        for step in range(total_tokens):
            curr_idx = (idx + step) % total_tokens
            token = self.ring[curr_idx]
            nid = self.token_to_node.get(token)

            if nid and nid in allowed and nid not in seen:
                seen.add(nid)
                selected_nodes.append(nid)
                if len(selected_nodes) >= count:
                    break

        return selected_nodes
