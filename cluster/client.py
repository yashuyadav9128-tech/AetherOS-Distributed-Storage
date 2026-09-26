"""
Distributed Storage Client Library
Provides helpers for 100MB sample generation, checksum calculation,
object upload/download, and node fault injection.
"""
import os
import time
import json
import hashlib
import urllib.request
import urllib.error
from pathlib import Path

from cluster.config import CHUNK_SIZE, COORDINATOR_HOST, COORDINATOR_PORT


def generate_sample_data(size_bytes: int = 100 * 1024 * 1024) -> tuple[bytes, str]:
    """Generates verifiable in-memory or on-disk sample data with calculated SHA-256."""
    pattern_base = b"AETHER_DISTRIBUTED_STORAGE_BLOCK_v1_00_"
    # Ensure pattern_chunk is exactly 1,048,576 bytes (1 MB)
    repeats = (1024 * 1024 // len(pattern_base)) + 2
    pattern_chunk = (pattern_base * repeats)[:1024 * 1024]
    mb_count = size_bytes // (1024 * 1024)
    remainder = size_bytes % (1024 * 1024)

    hasher = hashlib.sha256()
    byte_chunks = []

    for i in range(mb_count):
        marker = f"[{i:05d}]".encode("utf-8")
        chunk = marker + pattern_chunk[len(marker):]
        hasher.update(chunk)
        byte_chunks.append(chunk)

    if remainder > 0:
        chunk = pattern_chunk[:remainder]
        hasher.update(chunk)
        byte_chunks.append(chunk)

    full_data = b"".join(byte_chunks)
    return full_data, hasher.hexdigest()


def generate_sample_file(target_path: Path, size_bytes: int = 100 * 1024 * 1024) -> str:
    """Generates a 100MB sample file on disk and returns its SHA-256 checksum."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    pattern_base = b"AETHER_DISTRIBUTED_STORAGE_BLOCK_v1_00_"
    repeats = (1024 * 1024 // len(pattern_base)) + 2
    pattern_chunk = (pattern_base * repeats)[:1024 * 1024]
    mb_count = size_bytes // (1024 * 1024)
    remainder = size_bytes % (1024 * 1024)

    hasher = hashlib.sha256()
    with open(target_path, "wb") as f:
        for i in range(mb_count):
            marker = f"[{i:05d}]".encode("utf-8")
            chunk = marker + pattern_chunk[len(marker):]
            f.write(chunk)
            hasher.update(chunk)

        if remainder > 0:
            chunk = pattern_chunk[:remainder]
            f.write(chunk)
            hasher.update(chunk)

    return hasher.hexdigest()



def corrupt_node_replica(host: str, port: int, key: str) -> dict:
    """Sends a fault injection request to a specific storage node to corrupt its replica."""
    url = f"http://{host}:{port}/api/corrupt?key={key}"
    req = urllib.request.Request(url, data=b"", method="POST")
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        return json.loads(resp.read().decode("utf-8"))


def verify_node_replica(host: str, port: int, key: str) -> dict:
    """Queries a storage node directly to verify on-disk replica checksum."""
    url = f"http://{host}:{port}/api/verify?key={key}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download_object_from_coordinator(key: str, dest_path: Path, coord_host: str = COORDINATOR_HOST, coord_port: int = COORDINATOR_PORT) -> dict:
    """Downloads object via coordinator and validates received checksum."""
    url = f"http://{coord_host}:{coord_port}/api/objects/download?key={key}"
    req = urllib.request.Request(url, method="GET")

    hasher = hashlib.sha256()
    total_bytes = 0
    source_node = "unknown"

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(req, timeout=30.0) as resp:
        source_node = resp.headers.get("X-Source-Node", "unknown")
        expected_checksum = resp.headers.get("X-Checksum-SHA256", "")
        with open(dest_path, "wb") as f:
            while True:
                chunk = resp.read(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                hasher.update(chunk)
                total_bytes += len(chunk)

    calculated_checksum = hasher.hexdigest()
    is_valid = (not expected_checksum) or (expected_checksum.lower() == calculated_checksum.lower())

    return {
        "key": key,
        "size_bytes": total_bytes,
        "source_node": source_node,
        "calculated_checksum": calculated_checksum,
        "expected_checksum": expected_checksum,
        "is_valid": is_valid
    }
