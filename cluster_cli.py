"""
AetherStore Cluster CLI Management Tool
Provides interactive commands for cluster monitoring, object uploads, downloads,
checksum verification, fault injection, and rebalancing.
"""
import sys
import os
import argparse
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# Enable UTF-8 encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    os.system("")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from cluster.config import COORDINATOR_HOST, COORDINATOR_PORT, INITIAL_NODES, EXPANSION_NODES
from cluster.client import (
    generate_sample_data, corrupt_node_replica, verify_node_replica,
    download_object_from_coordinator
)

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def req_json(url: str, method: str = "GET", data: bytes = None) -> dict:
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"{RED}[ERROR] Could not connect to {url}: {e}{RESET}")
        sys.exit(1)


def cmd_status(args):
    url = f"http://{COORDINATOR_HOST}:{COORDINATOR_PORT}/api/cluster/status"
    data = req_json(url)

    summary = data["summary"]
    h_col = GREEN if summary["cluster_health"] == "HEALTHY" else YELLOW
    print(f"\n{BOLD}AETHERSTORE CLUSTER STATUS:{RESET} {h_col}{summary['cluster_health']}{RESET}")
    print(f"Total Nodes: {summary['total_nodes']} | Active: {summary['online_nodes']} | Dead: {summary['dead_nodes']} | Objects: {summary['total_objects']}\n")

    print(f"{BOLD}{'Node ID':<10} | {'Host:Port':<18} | {'Status':<12} | {'Disk Used':<12} | {'Replicas Hosted'}{RESET}")
    print("-" * 80)
    for nid, info in data["nodes"].items():
        st_color = GREEN if info["status"] == "ONLINE" else RED
        keys = ", ".join(info.get("keys", [])) or "None"
        print(f"{nid:<10} | {info['host']}:{info['port']:<12} | {st_color}{info['status']:<12}{RESET} | {info.get('disk_used_mb', 0):<8.2f} MB | {keys}")

    print("\n" + "=" * 80)
    print(f"{BOLD}OBJECT REPLICA MATRIX:{RESET}")
    print(f"{BOLD}{'Key':<22} | {'Size':<10} | {'RF':<6} | {'Status':<12} | {'Placement'}{RESET}")
    print("-" * 80)
    for k, obj in data["objects"].items():
        active_reps = [n for n in obj["replicas"] if data["nodes"].get(n, {}).get("status") == "ONLINE"]
        rf_ok = len(active_reps) >= obj["rf"]
        rf_col = GREEN if rf_ok else YELLOW
        placement = " -> ".join(f"[{n}]" for n in obj["replicas"])
        print(f"{k:<22} | {obj['size']/(1024*1024):<7.2f} MB | RF={obj['rf']:<3} | {rf_col}{len(active_reps)}/{obj['rf']}{RESET}        | {placement}")
    print()


def cmd_upload(args):
    key = args.key
    rf = args.rf
    file_path = Path(args.file)

    if file_path.exists():
        with open(file_path, "rb") as f:
            data = f.read()
    else:
        print(f"{YELLOW}[INFO] File '{args.file}' not found on disk. Generating {args.file} in memory...{RESET}")
        size_mb = 100 if "100" in args.file else 10
        data, _ = generate_sample_data(size_mb * 1024 * 1024)

    url = f"http://{COORDINATOR_HOST}:{COORDINATOR_PORT}/api/objects/upload?key={key}&rf={rf}"
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/octet-stream")
    req.add_header("Content-Length", str(len(data)))

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30.0) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            dur = time.time() - t0
            mb = len(data) / (1024 * 1024)
            print(f"{GREEN}[OK] Object uploaded successfully!{RESET}")
            print(f"  Key       : {res['key']}")
            print(f"  Size      : {mb:.2f} MB in {dur:.2f}s ({(mb/max(0.01, dur)):.1f} MB/s)")
            print(f"  SHA-256   : {res['sha256']}")
            print(f"  Replicas  : {', '.join(res['replicas'])}")
    except Exception as e:
        print(f"{RED}[ERROR] Upload failed: {e}{RESET}")


def cmd_download(args):
    dest = Path(args.dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    res = download_object_from_coordinator(args.key, dest, COORDINATOR_HOST, COORDINATOR_PORT)
    dur = time.time() - t0

    if res["is_valid"]:
        mb = res["size_bytes"] / (1024 * 1024)
        print(f"{GREEN}[OK] Object retrieved successfully from {res['source_node']}!{RESET}")
        print(f"  Saved to : {dest} ({mb:.2f} MB in {dur:.2f}s)")
        print(f"  SHA-256  : {res['calculated_checksum']} (verified)")
    else:
        print(f"{RED}[ERROR] Download failed or checksum mismatch: {res}{RESET}")


def cmd_repair(args):
    url = f"http://{COORDINATOR_HOST}:{COORDINATOR_PORT}/api/objects/audit_and_repair?key={args.key}"
    res = req_json(url, method="POST")
    print(f"{CYAN}[INFO] Audit & Repair Result:{RESET}")
    print(json.dumps(res, indent=2))


def cmd_rebalance(args):
    url = f"http://{COORDINATOR_HOST}:{COORDINATOR_PORT}/api/cluster/rebalance"
    res = req_json(url, method="POST")
    print(f"{GREEN}[OK] Cluster rebalance completed!{RESET}")
    print(json.dumps(res, indent=2))


def cmd_corrupt(args):
    node_id = args.node_id
    all_nodes = {**INITIAL_NODES, **EXPANSION_NODES}
    if node_id not in all_nodes:
        print(f"{RED}[ERROR] Unknown node ID: {node_id}{RESET}")
        return
    conf = all_nodes[node_id]
    res = corrupt_node_replica(conf["host"], conf["port"], args.key)
    print(f"{YELLOW}[WARN] Corruption injected:{RESET}")
    print(json.dumps(res, indent=2))


def main():
    parser = argparse.ArgumentParser(description="AetherStore Cluster CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status
    subparsers.add_parser("status", help="Show cluster health and node topology")

    # upload
    up_p = subparsers.add_parser("upload", help="Upload an object to the cluster")
    up_p.add_argument("file", help="File path or identifier to upload")
    up_p.add_argument("--key", default="sample.bin", help="Object key name")
    up_p.add_argument("--rf", type=int, default=3, help="Replication Factor")

    # download
    dl_p = subparsers.add_parser("download", help="Download an object from the cluster")
    dl_p.add_argument("key", help="Object key name")
    dl_p.add_argument("--dest", default="downloaded_file.bin", help="Destination file path")

    # repair
    rep_p = subparsers.add_parser("repair", help="Audit and self-heal corrupted replicas")
    rep_p.add_argument("key", help="Object key name")

    # rebalance
    subparsers.add_parser("rebalance", help="Rebalance cluster replica placement")

    # corrupt
    corr_p = subparsers.add_parser("corrupt", help="Inject fault into a replica")
    corr_p.add_argument("node_id", help="Node ID (e.g. Node-3)")
    corr_p.add_argument("key", help="Object key name")

    args = parser.parse_args()

    cmds = {
        "status": cmd_status,
        "upload": cmd_upload,
        "download": cmd_download,
        "repair": cmd_repair,
        "rebalance": cmd_rebalance,
        "corrupt": cmd_corrupt
    }

    cmds[args.command](args)


if __name__ == "__main__":
    main()
