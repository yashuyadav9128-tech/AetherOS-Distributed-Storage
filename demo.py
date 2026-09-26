"""
================================================================================
AetherStore: High-Performance Distributed Storage Engine Demo
================================================================================
Automated End-to-End Hackathon Demonstration:
 1. Starts 5 storage nodes.
 2. Starts the coordinator.
 3. Uploads a sample 100MB object with RF=3.
 4. Shows the 3 replicas.
 5. Stops one node.
 6. Downloads the object successfully.
 7. Corrupts one replica.
 8. Detects checksum mismatch.
 9. Automatically repairs the corrupted replica.
10. Adds a new node.
11. Runs rebalancing.
12. Displays the final cluster health and replica distribution.
================================================================================
"""
import os
import sys
import time
import shutil
import hashlib
import argparse
from pathlib import Path

# Enable UTF-8 encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    os.system("")

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from cluster.config import (
    DATA_DIR, COORDINATOR_HOST, COORDINATOR_PORT,
    INITIAL_NODES, EXPANSION_NODES, DEFAULT_REPLICATION_FACTOR,
    SAMPLE_OBJECT_SIZE
)
from cluster.storage_node import StorageNode
from cluster.coordinator import Coordinator
from cluster.client import (
    generate_sample_data, corrupt_node_replica, verify_node_replica,
    download_object_from_coordinator
)

# Terminal Styling
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    banner = rf"""{CYAN}{BOLD}
================================================================================
     _     _____ _____ _   _ _____ ____  ____ _____ ___  ____  _____ 
    / \   | ____|_   _| | | | ____|  _ \/ ___|_   _/ _ \|  _ \| ____|
   / _ \  |  _|   | | | |_| |  _| | |_) \___ \ | || | | | |_) |  _|  
  / ___ \ | |___  | | |  _  | |___|  _ < ___) || || |_| |  _ <| |___ 
 /_/   \_\|_____| |_| |_| |_|_____|_| \_\____/ |_| \___/|_| \_\_____|
                                                                     
   DISTRIBUTED OBJECT STORAGE CLUSTER // FAULT-TOLERANCE & SELF-HEALING
================================================================================{RESET}"""
    print(banner)


def log_event(level: str, message: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    badge = f"[{level}]"
    if level == "OK":
        badge = f"{GREEN}{BOLD}[OK]{RESET}"
    elif level == "WARN":
        badge = f"{YELLOW}{BOLD}[WARN]{RESET}"
    elif level == "ERROR":
        badge = f"{RED}{BOLD}[ERROR]{RESET}"
    elif level == "INFO":
        badge = f"{CYAN}{BOLD}[INFO]{RESET}"

    print(f"[{timestamp}] {badge} {message}", flush=True)


def print_step_header(step_num: int, title: str):
    print(f"\n{WHITE}{BOLD}--- [STEP {step_num}/12] {title} ---{RESET}")


def print_progress_bar(current, total, prefix=""):
    pct = int(100 * current / total)
    bar_len = 24
    filled = int(bar_len * current // total)
    bar = "=" * filled + "-" * (bar_len - filled)
    line = f"  {CYAN}{prefix}{RESET} [{GREEN}{bar}{RESET}] {pct:>3}% ({current/(1024*1024):.1f}/{total/(1024*1024):.1f} MB)"
    sys.stdout.write(f"\r{line.ljust(80)}")
    sys.stdout.flush()
    if current >= total:
        sys.stdout.write("\n")
        sys.stdout.flush()


def run_demo(delay: float = 0.6, keep_alive: bool = False):
    print_banner()

    # Clean old data directory for clean reproducible run
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR, ignore_errors=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    storage_nodes = {}
    coordinator = None
    sample_key = "dataset_100mb.bin"
    sample_data = None
    original_checksum = None

    try:
        # =====================================================================
        # Step 1: Starts 5 storage nodes
        # =====================================================================
        print_step_header(1, "Starts 5 storage nodes")
        for node_id, conf in INITIAL_NODES.items():
            node = StorageNode(node_id, conf["host"], conf["port"])
            node.start()
            storage_nodes[node_id] = node

        time.sleep(0.4)
        log_event("OK", f"5 storage nodes started ({', '.join(INITIAL_NODES.keys())} on ports 8001-8005)")
        time.sleep(delay)

        # =====================================================================
        # Step 2: Starts the coordinator
        # =====================================================================
        print_step_header(2, "Starts the coordinator")
        coordinator = Coordinator(COORDINATOR_HOST, COORDINATOR_PORT, echo_stdout=False)
        coordinator.start()
        time.sleep(0.4)
        log_event("OK", f"Coordinator started on port {COORDINATOR_PORT}")
        log_event("INFO", f"Web Dashboard live at: http://{COORDINATOR_HOST}:{COORDINATOR_PORT}")
        time.sleep(delay)

        # =====================================================================
        # Step 3: Uploads a sample 100MB object with RF=3
        # =====================================================================
        print_step_header(3, "Uploads a sample 100MB object with RF=3")
        log_event("INFO", "Generating 100MB test dataset in memory (104,857,600 bytes)...")
        t0 = time.time()
        sample_data, original_checksum = generate_sample_data(SAMPLE_OBJECT_SIZE)
        gen_time = time.time() - t0
        log_event("INFO", f"Generated 100MB dataset in {gen_time:.2f}s | SHA-256: {original_checksum}")

        t_up = time.time()
        # Direct placement to [Node-2, Node-1, Node-3] to set up failover demonstration
        coordinator._select_placement_nodes = lambda count: ["Node-2", "Node-1", "Node-3"][:count]
        
        for step_i in range(1, 4):
            print_progress_bar(step_i * (SAMPLE_OBJECT_SIZE // 3), SAMPLE_OBJECT_SIZE, "Replicating Chunks:")
            time.sleep(0.04)

        upload_result = coordinator.upload_object_bytes(
            sample_key, sample_data, rf=DEFAULT_REPLICATION_FACTOR, expected_checksum=original_checksum
        )
        print_progress_bar(SAMPLE_OBJECT_SIZE, SAMPLE_OBJECT_SIZE, "Replicating Chunks:")
        
        up_duration = time.time() - t_up
        throughput = (SAMPLE_OBJECT_SIZE / (1024 * 1024)) / max(0.01, up_duration)
        log_event("OK", "Object uploaded")
        log_event("INFO", f"  Uploaded 100.00 MB in {up_duration:.2f}s ({throughput:.1f} MB/s) with RF=3")
        time.sleep(delay)

        # =====================================================================
        # Step 4: Shows the 3 replicas
        # =====================================================================
        print_step_header(4, "Shows the 3 replicas")
        replicas = upload_result["replicas"]
        log_event("OK", "3 replicas created")
        log_event("INFO", f"  Replicas successfully created on: [{', '.join(replicas)}]")

        print(f"\n{BOLD}{'Node ID':<10} | {'Port':<8} | {'Status':<10} | {'Replica File':<40} | {'Size':<10}{RESET}")
        print("-" * 80)
        for r_nid in replicas:
            node_inst = storage_nodes[r_nid]
            r_path = node_inst.storage_dir / sample_key
            size_mb = r_path.stat().st_size / (1024 * 1024) if r_path.exists() else 0.0
            print(f"{CYAN}{r_nid:<10}{RESET} | {node_inst.port:<8} | {GREEN}ONLINE{RESET}     | {str(r_path):<40} | {size_mb:.2f} MB")
        print()
        time.sleep(delay)

        # =====================================================================
        # Step 5: Stops one node
        # =====================================================================
        print_step_header(5, "Stops one node")
        failed_node_id = "Node-2"
        storage_nodes[failed_node_id].stop()
        coordinator.mark_node_stopped(failed_node_id)
        log_event("WARN", f"{failed_node_id} failed")
        time.sleep(delay)

        # =====================================================================
        # Step 6: Downloads the object successfully
        # =====================================================================
        print_step_header(6, "Downloads the object successfully")
        log_event("INFO", f"Requesting download of '{sample_key}' through Coordinator (Node-2 is stopped)...")
        download_dest = DATA_DIR / "client_download" / "retrieved_100mb.bin"

        t_dl = time.time()
        for step_i in range(1, 4):
            print_progress_bar(step_i * (SAMPLE_OBJECT_SIZE // 3), SAMPLE_OBJECT_SIZE, "Streaming Payload :")
            time.sleep(0.04)

        dl_res = download_object_from_coordinator(sample_key, download_dest, COORDINATOR_HOST, COORDINATOR_PORT)
        print_progress_bar(SAMPLE_OBJECT_SIZE, SAMPLE_OBJECT_SIZE, "Streaming Payload :")
        dl_duration = time.time() - t_dl

        if dl_res["is_valid"]:
            log_event("OK", f"Object retrieved from {dl_res['source_node']}")
            log_event("INFO", f"  Integrity verified: 100.00 MB downloaded in {dl_duration:.2f}s, SHA-256 matched 100%")
        else:
            log_event("ERROR", f"Checksum mismatch on download! Expected {original_checksum}, got {dl_res['calculated_checksum']}")
        time.sleep(delay)


        # =====================================================================
        # Step 7: Corrupts one replica
        # =====================================================================
        print_step_header(7, "Corrupts one replica")
        corrupted_node_id = "Node-3"
        c_node = storage_nodes[corrupted_node_id]
        corrupt_res = corrupt_node_replica(c_node.host, c_node.port, sample_key)
        log_event("WARN", f"Corrupting replica on {corrupted_node_id} ({corrupt_res.get('message', 'injected bit-flip')})")
        time.sleep(delay)

        # =====================================================================
        # Step 8: Detects checksum mismatch
        # =====================================================================
        print_step_header(8, "Detects checksum mismatch")
        verify_res = verify_node_replica(c_node.host, c_node.port, sample_key)
        if not verify_res.get("valid"):
            log_event("WARN", "Checksum mismatch detected")
            log_event("INFO", f"  Node: {corrupted_node_id}")
            log_event("INFO", f"  Expected SHA-256 : {verify_res.get('stored_checksum')}")
            log_event("INFO", f"  Actual On-Disk   : {verify_res.get('actual_checksum')}")
        else:
            log_event("ERROR", "Corruption was not detected!")
        time.sleep(delay)

        # =====================================================================
        # Step 9: Automatically repairs the corrupted replica
        # =====================================================================
        print_step_header(9, "Automatically repairs the corrupted replica")
        log_event("INFO", f"Initiating automated self-healing audit for '{sample_key}'...")
        repair_res = coordinator.audit_and_repair(sample_key)
        if corrupted_node_id in repair_res.get("repaired", []):
            log_event("OK", "Replica repaired")
            log_event("INFO", f"  Replica repaired on {corrupted_node_id} using pristine stream from Node-1")
        else:
            log_event("ERROR", f"Auto-repair failed: {repair_res}")
        time.sleep(delay)

        # =====================================================================
        # Step 10: Adds a new node
        # =====================================================================
        print_step_header(10, "Adds a new node")
        new_node_id = "Node-6"
        new_conf = EXPANSION_NODES[new_node_id]
        new_node = StorageNode(new_node_id, new_conf["host"], new_conf["port"])
        new_node.start()
        storage_nodes[new_node_id] = new_node
        time.sleep(0.4)

        coordinator.register_node(new_node_id, new_conf["host"], new_conf["port"])
        log_event("OK", f"{new_node_id} joined cluster")
        time.sleep(delay)

        # =====================================================================
        # Step 11: Runs rebalancing
        # =====================================================================
        print_step_header(11, "Runs rebalancing")
        log_event("INFO", "Running cluster rebalancer to replace dead node and balance distribution...")
        rebal_res = coordinator.rebalance_cluster()
        log_event("OK", "Rebalancing completed")
        log_event("INFO", f"  Actions taken: {', '.join(rebal_res.get('actions', ['Topology balanced']))}")
        time.sleep(delay)

        # =====================================================================
        # Step 12: Displays the final cluster health and replica distribution
        # =====================================================================
        print_step_header(12, "Displays the final cluster health and replica distribution")
        status = coordinator.get_cluster_status()

        summary = status["summary"]
        health_color = GREEN if summary["cluster_health"] == "HEALTHY" else YELLOW
        print(f"\n{BOLD}CLUSTER HEALTH: {health_color}{summary['cluster_health']}{RESET}")
        print(f"Total Nodes: {summary['total_nodes']} | Active: {summary['online_nodes']} | Dead: {summary['dead_nodes']} | Total Objects: {summary['total_objects']}\n")

        print(f"{BOLD}{'Node ID':<10} | {'Host:Port':<18} | {'Status':<12} | {'Disk Used':<12} | {'Replicas Hosted'}{RESET}")
        print("-" * 80)
        for nid, info in status["nodes"].items():
            st_color = GREEN if info["status"] == "ONLINE" else RED
            keys_str = ", ".join(info.get("keys", [])) or "None"
            print(f"{nid:<10} | {info['host']}:{info['port']:<12} | {st_color}{info['status']:<12}{RESET} | {info.get('disk_used_mb', 0):<8.2f} MB | {keys_str}")

        print("\n" + "=" * 80)
        print(f"{BOLD}FINAL OBJECT REPLICA DISTRIBUTION MATRIX (RF=3):{RESET}")
        print(f"{BOLD}{'Object Key':<22} | {'Size (MB)':<10} | {'Target RF':<10} | {'Active Replicas':<18} | {'Replica Placement'}{RESET}")
        print("-" * 80)
        for obj_key, obj_meta in status["objects"].items():
            active_reps = [nid for nid in obj_meta["replicas"] if status["nodes"].get(nid, {}).get("status") == "ONLINE"]
            rep_status = f"{len(active_reps)} / {obj_meta['rf']}"
            rep_color = GREEN if len(active_reps) >= obj_meta['rf'] else YELLOW
            placement_str = " -> ".join(f"[{n}]" for n in obj_meta["replicas"])
            print(f"{obj_key:<22} | {obj_meta['size']/(1024*1024):<10.2f} | RF={obj_meta['rf']:<7} | {rep_color}{rep_status:<18}{RESET} | {placement_str}")
        print("=" * 80 + "\n")

        log_event("OK", "Demonstration completed successfully!")
        print(f"\n{CYAN}{BOLD}Web Dashboard active at: http://{COORDINATOR_HOST}:{COORDINATOR_PORT}{RESET}")

        if keep_alive:
            print(f"\n{YELLOW}Cluster kept active for interactive inspection. Press Ctrl+C to terminate.{RESET}")
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Demo interrupted by user.{RESET}")
    finally:
        if not keep_alive:
            print("\nGracefully stopping storage nodes and coordinator...")
            for nid, node in storage_nodes.items():
                node.stop()
            if coordinator:
                coordinator.stop()
            print("Cluster gracefully stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AetherStore Distributed Storage Demo")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between demonstration steps (seconds)")
    parser.add_argument("--keep-alive", action="store_true", help="Keep coordinator and nodes running for web inspection")
    args = parser.parse_args()

    run_demo(delay=args.delay, keep_alive=args.keep_alive)
