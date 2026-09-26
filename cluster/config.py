"""
Cluster Configuration
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

COORDINATOR_HOST = "127.0.0.1"
COORDINATOR_PORT = 8000

INITIAL_NODES = {
    "Node-1": {"host": "127.0.0.1", "port": 8001},
    "Node-2": {"host": "127.0.0.1", "port": 8002},
    "Node-3": {"host": "127.0.0.1", "port": 8003},
    "Node-4": {"host": "127.0.0.1", "port": 8004},
    "Node-5": {"host": "127.0.0.1", "port": 8005},
}

EXPANSION_NODES = {
    "Node-6": {"host": "127.0.0.1", "port": 8006},
}

DEFAULT_REPLICATION_FACTOR = 3
CHUNK_SIZE = 4 * 1024 * 1024  # 4MB streaming buffer
SAMPLE_OBJECT_SIZE = 100 * 1024 * 1024  # 100MB exactly (104,857,600 bytes)
