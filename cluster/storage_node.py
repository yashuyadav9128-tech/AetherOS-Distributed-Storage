"""
Distributed Storage Node Implementation
Handles chunked streaming storage, checksum verification, fault injection, and health reporting.
"""
import os
import sys
import json
import time
import hashlib
import logging
import argparse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
import threading

from cluster.config import CHUNK_SIZE, DATA_DIR

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class StorageNodeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default noisy access logs unless error
        if args and str(args[1]).startswith(('4', '5')):
            logging.warning("[%s] %s", self.server.node_id, format % args)

    def _send_json(self, status_code, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/api/health":
            self._handle_health()
        elif parsed.path == "/api/get":
            self._handle_get(params)
        elif parsed.path == "/api/verify":
            self._handle_verify(params)
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/api/put":
            self._handle_put(params)
        elif parsed.path == "/api/corrupt":
            self._handle_corrupt(params)
        elif parsed.path == "/api/delete":
            self._handle_delete(params)
        elif parsed.path == "/api/shutdown":
            self._handle_shutdown()
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if parsed.path == "/api/delete":
            self._handle_delete(params)
        else:
            self._send_json(404, {"error": "Not Found"})

    def _handle_health(self):
        storage_dir = Path(self.server.storage_dir)
        keys = []
        total_size = 0
        if storage_dir.exists():
            for p in storage_dir.iterdir():
                if p.is_file() and not p.name.endswith(".meta"):
                    keys.append(p.name)
                    total_size += p.stat().st_size

        self._send_json(200, {
            "node_id": self.server.node_id,
            "status": "ONLINE",
            "host": self.server.host,
            "port": self.server.port,
            "disk_used_bytes": total_size,
            "disk_used_mb": round(total_size / (1024 * 1024), 2),
            "keys": keys,
            "replica_count": len(keys)
        })

    def _handle_put(self, params):
        key = params.get("key", [None])[0] or self.headers.get("X-Object-Key")
        expected_checksum = params.get("checksum", [None])[0] or self.headers.get("X-Object-Checksum")
        content_length = int(self.headers.get("Content-Length", 0))

        if not key:
            self._send_json(400, {"error": "Missing key parameter"})
            return

        storage_dir = Path(self.server.storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)
        file_path = storage_dir / key
        meta_path = storage_dir / f"{key}.meta"

        hasher = hashlib.sha256()
        bytes_received = 0

        try:
            with open(file_path, "wb") as f:
                remaining = content_length
                while remaining > 0:
                    read_len = min(remaining, CHUNK_SIZE)
                    chunk = self.rfile.read(read_len)
                    if not chunk:
                        break
                    f.write(chunk)
                    hasher.update(chunk)
                    bytes_received += len(chunk)
                    remaining -= len(chunk)

            calculated_checksum = hasher.hexdigest()

            if expected_checksum and calculated_checksum.lower() != expected_checksum.lower():
                if file_path.exists():
                    file_path.unlink()
                self._send_json(400, {
                    "error": "Checksum mismatch during PUT",
                    "expected": expected_checksum,
                    "calculated": calculated_checksum
                })
                return

            # Save metadata
            meta = {
                "key": key,
                "size": bytes_received,
                "sha256": calculated_checksum,
                "uploaded_at": time.time(),
                "node_id": self.server.node_id
            }
            with open(meta_path, "w", encoding="utf-8") as mf:
                json.dump(meta, mf)

            self._send_json(200, {
                "status": "stored",
                "node_id": self.server.node_id,
                "key": key,
                "size": bytes_received,
                "sha256": calculated_checksum
            })
        except Exception as e:
            if file_path.exists():
                file_path.unlink()
            self._send_json(500, {"error": f"Failed to write file: {str(e)}"})

    def _handle_get(self, params):
        key = params.get("key", [None])[0]
        if not key:
            self._send_json(400, {"error": "Missing key parameter"})
            return

        file_path = Path(self.server.storage_dir) / key
        meta_path = Path(self.server.storage_dir) / f"{key}.meta"

        if not file_path.exists():
            self._send_json(404, {"error": f"Object '{key}' not found on {self.server.node_id}"})
            return

        sha256 = ""
        if meta_path.exists():
            try:
                with open(meta_path, "r", encoding="utf-8") as mf:
                    meta = json.load(mf)
                    sha256 = meta.get("sha256", "")
            except Exception:
                pass

        file_size = file_path.stat().st_size
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(file_size))
        if sha256:
            self.send_header("X-Checksum-SHA256", sha256)
        self.send_header("X-Node-ID", self.server.node_id)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                self.wfile.write(chunk)

    def _handle_verify(self, params):
        key = params.get("key", [None])[0]
        if not key:
            self._send_json(400, {"error": "Missing key parameter"})
            return

        file_path = Path(self.server.storage_dir) / key
        meta_path = Path(self.server.storage_dir) / f"{key}.meta"

        if not file_path.exists():
            self._send_json(404, {
                "node_id": self.server.node_id,
                "key": key,
                "exists": False,
                "valid": False,
                "error": "File does not exist"
            })
            return

        stored_checksum = None
        if meta_path.exists():
            try:
                with open(meta_path, "r", encoding="utf-8") as mf:
                    stored_checksum = json.load(mf).get("sha256")
            except Exception:
                pass

        hasher = hashlib.sha256()
        file_size = 0
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                hasher.update(chunk)
                file_size += len(chunk)

        actual_checksum = hasher.hexdigest()
        is_valid = (stored_checksum is not None) and (stored_checksum.lower() == actual_checksum.lower())

        self._send_json(200, {
            "node_id": self.server.node_id,
            "key": key,
            "exists": True,
            "valid": is_valid,
            "stored_checksum": stored_checksum,
            "actual_checksum": actual_checksum,
            "size": file_size
        })

    def _handle_corrupt(self, params):
        key = params.get("key", [None])[0]
        if not key:
            self._send_json(400, {"error": "Missing key parameter"})
            return

        file_path = Path(self.server.storage_dir) / key
        if not file_path.exists():
            self._send_json(404, {"error": f"Key {key} not found to corrupt"})
            return

        file_size = file_path.stat().st_size
        # Inject bit corruption: alter 128 bytes around the midpoint or offset 4096
        offset = min(4096, max(0, file_size // 2))
        corrupt_len = min(128, max(1, file_size - offset))

        with open(file_path, "r+b") as f:
            f.seek(offset)
            original = f.read(corrupt_len)
            corrupted = bytes(b ^ 0xFF for b in original)
            f.seek(offset)
            f.write(corrupted)

        self._send_json(200, {
            "node_id": self.server.node_id,
            "status": "corrupted",
            "key": key,
            "offset": offset,
            "corrupted_bytes": corrupt_len,
            "message": f"Injected bit-flip corruption into {key} at offset {offset}"
        })

    def _handle_delete(self, params):
        key = params.get("key", [None])[0]
        if not key:
            self._send_json(400, {"error": "Missing key parameter"})
            return

        file_path = Path(self.server.storage_dir) / key
        meta_path = Path(self.server.storage_dir) / f"{key}.meta"

        deleted = False
        if file_path.exists():
            file_path.unlink()
            deleted = True
        if meta_path.exists():
            meta_path.unlink()

        self._send_json(200, {
            "node_id": self.server.node_id,
            "key": key,
            "deleted": deleted
        })

    def _handle_shutdown(self):
        self._send_json(200, {"status": "shutting down", "node_id": self.server.node_id})
        threading.Thread(target=self.server.shutdown, daemon=True).start()


class StorageNode:
    """Manages the lifecycle of an individual storage node server."""
    def __init__(self, node_id: str, host: str, port: int, storage_dir: Path = None):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.storage_dir = storage_dir or (DATA_DIR / self.node_id.lower().replace("-", "_"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.server = None
        self.thread = None
        self.running = False

    def start(self, retries=5, delay=0.3):
        if self.running:
            return
        last_err = None
        for attempt in range(retries):
            try:
                self.server = ThreadedHTTPServer((self.host, self.port), StorageNodeHandler)
                self.server.node_id = self.node_id
                self.server.host = self.host
                self.server.port = self.port
                self.server.storage_dir = self.storage_dir
                self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
                self.thread.start()
                self.running = True
                return
            except OSError as e:
                last_err = e
                time.sleep(delay)
        if last_err:
            raise last_err

    def stop(self):
        if self.server and self.running:
            self.running = False
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2.0)

    def is_alive(self):
        return self.running and self.thread and self.thread.is_alive()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a distributed storage node.")
    parser.add_argument("--id", default="Node-1", help="Node Identifier")
    parser.add_argument("--host", default="127.0.0.1", help="Host binding")
    parser.add_argument("--port", type=int, default=8001, help="Port to listen on")
    args = parser.parse_args()

    node = StorageNode(args.id, args.host, args.port)
    logging.info(f"Starting {args.id} on {args.host}:{args.port} (storage: {node.storage_dir})")
    node.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info(f"Stopping {args.id}...")
        node.stop()
