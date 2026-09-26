"""
Distributed Storage Coordinator
Orchestrates cluster topology, metadata catalog, replica placement (RF=3),
failover retrieval, self-healing corruption repair, dynamic rebalancing, and web dashboard.
"""
import os
import sys
import json
import time
import hashlib
import logging
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    os.system("")


from cluster.config import (
    COORDINATOR_HOST, COORDINATOR_PORT,
    INITIAL_NODES, DEFAULT_REPLICATION_FACTOR, CHUNK_SIZE
)
from cluster.web_dashboard import get_dashboard_html

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


class ThreadedCoordinatorServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class CoordinatorHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress standard logging to keep output clean
        pass

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
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/" or parsed.path == "/index.html":
            html = get_dashboard_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        elif parsed.path == "/api/cluster/status":
            status_data = self.server.coordinator.get_cluster_status()
            self._send_json(200, status_data)
        elif parsed.path == "/api/objects/download":
            key = params.get("key", [None])[0]
            if not key:
                self._send_json(400, {"error": "Missing key parameter"})
                return
            self._handle_download(key)
        elif parsed.path == "/api/objects/replicas":
            key = params.get("key", [None])[0]
            obj = self.server.coordinator.objects.get(key)
            if not obj:
                self._send_json(404, {"error": f"Object '{key}' not found"})
                return
            self._send_json(200, {
                "key": key,
                "rf": obj["rf"],
                "replicas": obj["replicas"],
                "size": obj["size"],
                "sha256": obj["sha256"]
            })
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/api/objects/upload":
            key = params.get("key", [None])[0]
            rf = int(params.get("rf", [DEFAULT_REPLICATION_FACTOR])[0])
            expected_checksum = params.get("checksum", [None])[0]
            content_length = int(self.headers.get("Content-Length", 0))

            if not key:
                self._send_json(400, {"error": "Missing key parameter"})
                return

            res = self.server.coordinator.upload_object_stream(key, self.rfile, content_length, rf, expected_checksum)
            self._send_json(200 if "error" not in res else 500, res)

        elif parsed.path == "/api/objects/audit_and_repair":
            key = params.get("key", [None])[0]
            res = self.server.coordinator.audit_and_repair(key)
            self._send_json(200, res)

        elif parsed.path == "/api/cluster/repair_all":
            results = []
            for k in list(self.server.coordinator.objects.keys()):
                results.append(self.server.coordinator.audit_and_repair(k))
            self._send_json(200, {"status": "completed", "results": results})

        elif parsed.path == "/api/cluster/rebalance":
            res = self.server.coordinator.rebalance_cluster()
            self._send_json(200, res)

        elif parsed.path == "/api/nodes/register":
            node_id = params.get("node_id", [None])[0]
            host = params.get("host", ["127.0.0.1"])[0]
            port = int(params.get("port", [8000])[0])
            if not node_id:
                self._send_json(400, {"error": "Missing node_id"})
                return
            res = self.server.coordinator.register_node(node_id, host, port)
            self._send_json(200, res)

        elif parsed.path == "/api/nodes/stop":
            node_id = params.get("node_id", [None])[0]
            res = self.server.coordinator.mark_node_stopped(node_id)
            self._send_json(200, res)

        elif parsed.path == "/api/demo/corrupt":
            node_id = params.get("node_id", ["Node-3"])[0]
            key = params.get("key", ["dataset_100mb.bin"])[0]
            node = self.server.coordinator.nodes.get(node_id)
            if not node:
                self._send_json(404, {"error": "Node not found"})
                return
            try:
                url = f"http://{node['host']}:{node['port']}/api/corrupt?key={key}"
                req = urllib.request.Request(url, data=b"", method="POST")
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    self.server.coordinator.record_event("WARN", f"Corrupting replica on {node_id} (injected bit-rot)")
                    self._send_json(200, data)
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        elif parsed.path == "/api/demo/restart_node":
            node_id = params.get("node_id", ["Node-2"])[0]
            node = self.server.coordinator.nodes.get(node_id)
            if node:
                node["status"] = "ONLINE"
                self.server.coordinator.record_event("OK", f"{node_id} restarted and marked ONLINE")
                self._send_json(200, {"status": "restarted", "node_id": node_id})
            else:
                self._send_json(404, {"error": "Node not found"})

        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def _handle_download(self, key):
        coord = self.server.coordinator
        res = coord.download_object_data(key)
        if "error" in res:
            self._send_json(404, res)
            return

        data = res["data"]
        source_node = res["source_node"]
        sha256 = res["sha256"]

        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Source-Node", source_node)
        self.send_header("X-Checksum-SHA256", sha256)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)


class Coordinator:
    """Manages cluster topology, metadata, placement, failover, self-healing, and rebalancing."""
    def __init__(self, host=COORDINATOR_HOST, port=COORDINATOR_PORT, echo_stdout: bool = True):
        self.host = host
        self.port = port
        self.echo_stdout = echo_stdout
        self.server = None
        self.thread = None
        self.running = False
        
        # Topology: node_id -> {"host": str, "port": int, "status": "ONLINE" | "DEAD", "disk_used_mb": float, "keys": list}
        self.nodes = {}
        # Objects: key -> {"size": int, "sha256": str, "rf": int, "replicas": [node_ids], "uploaded_at": float}
        self.objects = {}
        # Live event log buffer (for web dashboard & CLI)
        self.events = []
        self._lock = threading.Lock()

        # Pre-populate default initial nodes
        for nid, info in INITIAL_NODES.items():
            self.nodes[nid] = {
                "host": info["host"],
                "port": info["port"],
                "status": "ONLINE",
                "disk_used_mb": 0.0,
                "keys": []
            }

    def record_event(self, level: str, message: str, echo_stdout: bool = None):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        time_short = time.strftime("%H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "time": time_short,
            "level": level,
            "message": message
        }
        with self._lock:
            self.events.append(entry)
            if len(self.events) > 100:
                self.events.pop(0)

        should_echo = self.echo_stdout if echo_stdout is None else echo_stdout
        if should_echo:
            # Color coding for terminal output
            cyan = "\033[96m"
            green = "\033[92m"
            yellow = "\033[93m"
            red = "\033[91m"
            bold = "\033[1m"
            reset = "\033[0m"

            badge = f"[{level}]"
            if level == "OK":
                badge = f"{green}{bold}[OK]{reset}"
            elif level == "WARN":
                badge = f"{yellow}{bold}[WARN]{reset}"
            elif level == "ERROR":
                badge = f"{red}{bold}[ERROR]{reset}"
            elif level == "INFO":
                badge = f"{cyan}[INFO]{reset}"

            print(f"[{timestamp}] {badge} {message}", flush=True)

    def ping_node(self, node_id: str) -> bool:
        """Pings a node's /api/health endpoint to verify liveness."""
        node = self.nodes.get(node_id)
        if not node or node.get("status") == "DEAD":
            return False

        url = f"http://{node['host']}:{node['port']}/api/health"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    node["status"] = "ONLINE"
                    node["disk_used_mb"] = data.get("disk_used_mb", 0.0)
                    node["keys"] = data.get("keys", [])
                    return True
        except Exception:
            node["status"] = "DEAD"
            return False
        node["status"] = "DEAD"
        return False

    def refresh_all_nodes(self):
        """Refreshes status and stats for all registered nodes."""
        for nid in list(self.nodes.keys()):
            self.ping_node(nid)

    def register_node(self, node_id: str, host: str, port: int):
        self.nodes[node_id] = {
            "host": host,
            "port": port,
            "status": "ONLINE",
            "disk_used_mb": 0.0,
            "keys": []
        }
        self.record_event("OK", f"{node_id} joined cluster (127.0.0.1:{port})")
        return {"status": "registered", "node_id": node_id}

    def mark_node_stopped(self, node_id: str):
        if node_id in self.nodes:
            self.nodes[node_id]["status"] = "DEAD"
            self.record_event("WARN", f"{node_id} failed (simulated crash / stopped)")
            return {"status": "marked dead", "node_id": node_id}
        return {"error": "Node not found"}

    def _select_placement_nodes(self, count: int) -> list:
        """Selects healthiest online nodes with lowest replica count for optimal distribution."""
        active = [nid for nid, info in self.nodes.items() if info["status"] == "ONLINE"]
        # Sort by number of keys hosted
        active.sort(key=lambda nid: len(self.nodes[nid].get("keys", [])))
        return active[:count]

    def upload_object_bytes(self, key: str, data: bytes, rf: int = DEFAULT_REPLICATION_FACTOR, expected_checksum: str = None) -> dict:
        """Uploads an in-memory object with RF replicas to storage nodes."""
        hasher = hashlib.sha256(data)
        sha256 = hasher.hexdigest()
        if expected_checksum and expected_checksum.lower() != sha256.lower():
            raise ValueError(f"Checksum mismatch: expected {expected_checksum}, calculated {sha256}")

        size_mb = len(data) / (1024 * 1024)
        target_nodes = self._select_placement_nodes(rf)
        if len(target_nodes) < rf:
            raise RuntimeError(f"Not enough active nodes to satisfy RF={rf} (available: {len(target_nodes)})")

        replicated_nodes = []
        for nid in target_nodes:
            node = self.nodes[nid]
            url = f"http://{node['host']}:{node['port']}/api/put?key={key}&checksum={sha256}"
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("Content-Type", "application/octet-stream")
            req.add_header("Content-Length", str(len(data)))
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                if resp.status == 200:
                    replicated_nodes.append(nid)
                    if key not in node["keys"]:
                        node["keys"].append(key)
                    node["disk_used_mb"] = round(node.get("disk_used_mb", 0) + size_mb, 2)

        self.objects[key] = {
            "size": len(data),
            "sha256": sha256,
            "rf": rf,
            "replicas": replicated_nodes,
            "uploaded_at": time.time(),
            "status": "HEALTHY"
        }

        self.record_event("OK", f"Object uploaded ({size_mb:.2f} MB, RF={rf}, SHA-256: {sha256[:16]}...)")
        self.record_event("OK", f"{len(replicated_nodes)} replicas created: [{', '.join(replicated_nodes)}]")

        return {
            "key": key,
            "size": len(data),
            "sha256": sha256,
            "rf": rf,
            "replicas": replicated_nodes
        }

    def upload_object_stream(self, key: str, rfile, content_length: int, rf: int, expected_checksum: str) -> dict:
        """Reads stream into memory and replicates."""
        data = bytearray()
        remaining = content_length
        while remaining > 0:
            read_len = min(remaining, CHUNK_SIZE)
            chunk = rfile.read(read_len)
            if not chunk:
                break
            data.extend(chunk)
            remaining -= len(chunk)
        return self.upload_object_bytes(key, bytes(data), rf, expected_checksum)

    def download_object_data(self, key: str) -> dict:
        """
        Attempts download from replicas in order.
        If a replica node is unreachable or corrupted, fails over seamlessly to the next replica.
        """
        obj = self.objects.get(key)
        if not obj:
            return {"error": f"Object '{key}' not found in metadata catalog"}

        expected_checksum = obj["sha256"]
        replicas = list(obj["replicas"])

        for nid in replicas:
            node = self.nodes.get(nid)
            if not node or node.get("status") == "DEAD":
                continue

            url = f"http://{node['host']}:{node['port']}/api/get?key={key}"
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    if resp.status == 200:
                        data = resp.read()
                        # Verify integrity on download
                        hasher = hashlib.sha256(data)
                        dl_checksum = hasher.hexdigest()
                        if dl_checksum.lower() == expected_checksum.lower():
                            self.record_event("OK", f"Object retrieved from {nid} (failover verified, {len(data)/(1024*1024):.2f} MB)")
                            return {
                                "key": key,
                                "data": data,
                                "source_node": nid,
                                "sha256": dl_checksum,
                                "size": len(data)
                            }
                        else:
                            self.record_event("WARN", f"Replica on {nid} returned corrupt data during download! Failing over...")
            except (urllib.error.URLError, ConnectionRefusedError, TimeoutError, OSError) as e:
                # Node is unreachable / stopped
                node["status"] = "DEAD"
                # Continue failover to other replica nodes
                continue

        return {"error": f"Unable to retrieve healthy replica for '{key}' from any active node"}

    def audit_and_repair(self, key: str) -> dict:
        """
        Audits replica integrity using checksums.
        If corruption is detected, repairs replica from a verified healthy copy.
        """
        obj = self.objects.get(key)
        if not obj:
            return {"error": f"Object '{key}' not found"}

        expected_checksum = obj["sha256"]
        replicas = list(obj["replicas"])
        corrupted_nodes = []
        healthy_nodes = []

        # Step 1: Audit all replica nodes
        for nid in replicas:
            node = self.nodes.get(nid)
            if not node or node.get("status") == "DEAD":
                continue

            url = f"http://{node['host']}:{node['port']}/api/verify?key={key}"
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    if resp.status == 200:
                        res = json.loads(resp.read().decode("utf-8"))
                        if not res.get("valid"):
                            actual_cs = res.get("actual_checksum", "unknown")
                            corrupted_nodes.append((nid, actual_cs))
                            self.record_event("WARN", f"Checksum mismatch detected on {nid} (expected: {expected_checksum[:12]}..., actual: {actual_cs[:12]}...)")
                        else:
                            healthy_nodes.append(nid)
            except Exception:
                node["status"] = "DEAD"

        # Step 2: Auto-repair corrupted replicas
        repaired_nodes = []
        if corrupted_nodes:
            if not healthy_nodes:
                self.record_event("ERROR", f"Cannot repair {key}: No healthy replica found in cluster!")
                return {"status": "unrecoverable", "corrupted": [c[0] for c in corrupted_nodes]}

            donor_node_id = healthy_nodes[0]
            donor_node = self.nodes[donor_node_id]

            # Fetch clean stream from healthy donor
            fetch_url = f"http://{donor_node['host']}:{donor_node['port']}/api/get?key={key}"
            clean_data = None
            try:
                with urllib.request.urlopen(urllib.request.Request(fetch_url), timeout=20.0) as resp:
                    clean_data = resp.read()
            except Exception as e:
                self.record_event("ERROR", f"Failed to read clean replica from donor {donor_node_id}: {e}")
                return {"status": "donor_failed"}

            # Re-upload clean replica to each corrupted node
            for target_nid, _ in corrupted_nodes:
                target_node = self.nodes.get(target_nid)
                if not target_node or target_node.get("status") == "DEAD":
                    continue

                put_url = f"http://{target_node['host']}:{target_node['port']}/api/put?key={key}&checksum={expected_checksum}"
                put_req = urllib.request.Request(put_url, data=clean_data, method="POST")
                put_req.add_header("Content-Type", "application/octet-stream")
                put_req.add_header("Content-Length", str(len(clean_data)))
                try:
                    with urllib.request.urlopen(put_req, timeout=20.0) as put_resp:
                        if put_resp.status == 200:
                            repaired_nodes.append(target_nid)
                            self.record_event("OK", f"Replica repaired on {target_nid} (restored clean copy from {donor_node_id})")
                except Exception as e:
                    self.record_event("ERROR", f"Failed to restore replica on {target_nid}: {e}")

        return {
            "status": "audited",
            "key": key,
            "corrupted_detected": [c[0] for c in corrupted_nodes],
            "repaired": repaired_nodes,
            "healthy_replicas": healthy_nodes + repaired_nodes
        }

    def rebalance_cluster(self) -> dict:
        """
        Rebalances replica placement across all active online nodes (including newly joined nodes like Node-6).
        Ensures dead node replicas are replaced and load is distributed evenly while preserving RF=3.
        """
        self.refresh_all_nodes()
        online_nodes = [nid for nid, info in self.nodes.items() if info["status"] == "ONLINE"]

        rebalanced_actions = []

        for key, obj in self.objects.items():
            current_replicas = set(obj["replicas"])
            # Remove dead nodes from replica placement
            active_replicas = [nid for nid in current_replicas if self.nodes.get(nid, {}).get("status") == "ONLINE"]
            target_rf = obj.get("rf", DEFAULT_REPLICATION_FACTOR)

            # If we lost replicas due to failed nodes (e.g. Node-2), or new nodes (Node-6) need placement:
            needed = target_rf - len(active_replicas)
            candidates = [nid for nid in online_nodes if nid not in active_replicas]

            # Prioritize candidate nodes with least keys, favoring new nodes (e.g. Node-6)
            def node_priority(nid):
                k_count = len(self.nodes[nid].get("keys", []))
                n_num = int(nid.split("-")[-1]) if nid.startswith("Node-") and nid.split("-")[-1].isdigit() else 0
                return (k_count, -n_num)

            candidates.sort(key=node_priority)

            if needed > 0 and candidates and active_replicas:
                # Donor node
                donor_nid = active_replicas[0]
                donor_node = self.nodes[donor_nid]

                # Fetch clean data
                donor_url = f"http://{donor_node['host']}:{donor_node['port']}/api/get?key={key}"
                try:
                    with urllib.request.urlopen(donor_url, timeout=20.0) as resp:
                        data = resp.read()

                    # Distribute to candidate nodes to restore RF
                    for i in range(min(needed, len(candidates))):
                        target_nid = candidates[i]
                        target_node = self.nodes[target_nid]

                        put_url = f"http://{target_node['host']}:{target_node['port']}/api/put?key={key}&checksum={obj['sha256']}"
                        req = urllib.request.Request(put_url, data=data, method="POST")
                        req.add_header("Content-Type", "application/octet-stream")
                        req.add_header("Content-Length", str(len(data)))
                        with urllib.request.urlopen(req, timeout=20.0) as put_resp:
                            if put_resp.status == 200:
                                active_replicas.append(target_nid)
                                if key not in target_node["keys"]:
                                    target_node["keys"].append(key)
                                target_node["disk_used_mb"] = round(target_node.get("disk_used_mb", 0) + (len(data)/(1024*1024)), 2)
                                rebalanced_actions.append(f"Replicated '{key}' to {target_nid}")
                except Exception as e:
                    self.record_event("ERROR", f"Rebalancing error for '{key}': {e}")

            # Update object's replicas list
            obj["replicas"] = active_replicas

        self.record_event("OK", f"Rebalancing completed: Replicas rebalanced across {len(online_nodes)} active nodes")
        return {
            "status": "rebalanced",
            "online_nodes_count": len(online_nodes),
            "actions": rebalanced_actions,
            "objects": {k: v["replicas"] for k, v in self.objects.items()}
        }

    def get_cluster_status(self) -> dict:
        total_nodes = len(self.nodes)
        online_nodes = sum(1 for n in self.nodes.values() if n["status"] == "ONLINE")
        total_objects = len(self.objects)

        # Health assessment
        all_rf_satisfied = True
        for obj in self.objects.values():
            active_reps = sum(1 for nid in obj["replicas"] if self.nodes.get(nid, {}).get("status") == "ONLINE")
            if active_reps < obj.get("rf", DEFAULT_REPLICATION_FACTOR):
                all_rf_satisfied = False

        cluster_health = "HEALTHY" if all_rf_satisfied and online_nodes >= 3 else "DEGRADED"

        return {
            "summary": {
                "total_nodes": total_nodes,
                "online_nodes": online_nodes,
                "dead_nodes": total_nodes - online_nodes,
                "total_objects": total_objects,
                "cluster_health": cluster_health
            },
            "nodes": self.nodes,
            "objects": self.objects,
            "recent_events": self.events[-15:]
        }

    def start(self, retries=5, delay=0.3):
        if self.running:
            return
        last_err = None
        for attempt in range(retries):
            try:
                self.server = ThreadedCoordinatorServer((self.host, self.port), CoordinatorHandler)
                self.server.coordinator = self
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


if __name__ == "__main__":
    coord = Coordinator()
    coord.start()
    coord.record_event("OK", f"Coordinator started on http://{coord.host}:{coord.port}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        coord.stop()
