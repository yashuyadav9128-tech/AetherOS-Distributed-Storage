# AetherStore: High-Performance Distributed Storage Engine

A production-grade, zero-dependency distributed object storage cluster implementing **Replication Factor (RF=3)**, **failover retrieval**, **SHA-256 end-to-end checksum verification**, **self-healing corruption repair**, and **dynamic scale-out rebalancing**.

---

## 🚀 One-Command Automated Demo

You can run the entire 12-step demonstration with a single command:

```powershell
python demo.py
```

Or on Windows:
```cmd
run_demo.bat
```
or
```powershell
.\run_demo.ps1
```

### Options:
- **Interactive Inspection Mode (Keeps Web Dashboard & Cluster Running)**:
  ```powershell
  python demo.py --keep-alive
  ```
  Open **[http://localhost:8000](http://localhost:8000)** in your browser to view the real-time glassmorphic dashboard!
- **Adjust step pacing delay**:
  ```powershell
  python demo.py --delay 1.0
  ```

## Vercel Dashboard Preview

Vercel detects the FastAPI entrypoint in `app.py` and serves the dashboard at `/`. This is a visual preview only: Vercel does not run the coordinator and six storage-node processes, so live telemetry and cluster controls are unavailable. Run the cluster locally with `python demo.py --keep-alive` for the fully interactive dashboard.

---

## 📋 The 12 Demonstrated Requirements

| Step | Action | Status / Output Event | Verification Mechanism |
|---|---|---|---|
| **1** | Starts 5 storage nodes | `[OK] 5 storage nodes started` | Initialized Node-1 through Node-5 on ports 8001–8005. |
| **2** | Starts the coordinator | `[OK] Coordinator started on port 8000` | Topology registry & metadata catalog initialized. |
| **3** | Uploads sample 100MB object with RF=3 | `[OK] Object uploaded` | 100.00 MB binary dataset streamed to 3 selected nodes. |
| **4** | Shows the 3 replicas | `[OK] 3 replicas created` | Confirms replicas on disk: `[Node-2, Node-1, Node-3]`. |
| **5** | Stops one node | `[WARN] Node-2 failed` | Node-2 socket killed, marked DEAD in cluster topology. |
| **6** | Downloads the object successfully | `[OK] Object retrieved from Node-1` | Coordinator detects Node-2 is offline, fails over to Node-1 seamlessly, 100% SHA-256 verified. |
| **7** | Corrupts one replica | `[WARN] Corrupting replica on Node-3` | Injected bit-rot XOR flip directly into Node-3's on-disk replica. |
| **8** | Detects checksum mismatch | `[WARN] Checksum mismatch detected` | Scrubber computes on-disk SHA-256, flags mismatch against metadata. |
| **9** | Automatically repairs corrupted replica | `[OK] Replica repaired` | Self-healer retrieves clean stream from Node-1, restores Node-3. |
| **10** | Adds a new node | `[OK] Node-6 joined cluster` | Node-6 spins up on port 8006 and registers with coordinator. |
| **11** | Runs rebalancing | `[OK] Rebalancing completed` | Rebalancer identifies dead Node-2 replica, migrates replica to Node-6. |
| **12** | Displays final cluster health & distribution | `CLUSTER HEALTH: HEALTHY` | 3/3 RF satisfied on `[Node-3] -> [Node-1] -> [Node-6]`. |

---

## 🏛️ Architecture Overview

```
                      +-----------------------------+
                      |   Client / Web Dashboard    |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |     Master Coordinator      |
                      |   (Port 8000 // HTTP API)   |
                      +--------------+--------------+
                                     |
         +---------------------------+---------------------------+
         |                           |                           |
         v                           v                           v
+-----------------+         +-----------------+         +-----------------+
|  Storage Node 1 |         |  Storage Node 2 |         |  Storage Node 3 |
|   (Port 8001)   |         |   (Port 8002)   |         |   (Port 8003)   |
|   [DATA / META] |         |   [DATA / META] |         |   [DATA / META] |
+-----------------+         +-----------------+         +-----------------+
         |                           |                           |
         v                           v                           v
+-----------------+         +-----------------+         +-----------------+
|  Storage Node 4 |         |  Storage Node 5 |         |  Storage Node 6 |
|   (Port 8004)   |         |   (Port 8005)   |         |   (Port 8006)   |
|   [DATA / META] |         |   [DATA / META] |         |   [DATA / META] |
+-----------------+         +-----------------+         +-----------------+
```

### Key Engineering Features:
1. **Zero External Dependencies**: Built 100% using Python's standard library (`http.server`, `socketserver`, `hashlib`, `urllib`).
2. **Chunked Streaming I/O**: 4MB buffered streaming prevents loading full 100MB files into memory during transfers.
3. **End-to-End Cryptographic Checksumming**: SHA-256 hashes generated on write, stored in metadata `.meta`, verified on read.
4. **Resilient Failover**: If any replica node crashes, download requests fail over instantly to alternative healthy nodes with zero downtime.
5. **Self-Healing Engine**: Automatically detects on-disk bit corruption and repairs replicas by sourcing from clean nodes.
6. **Topology Rebalancer**: Automatically incorporates new nodes (e.g. Node-6) to replace dead nodes and balance cluster capacity.
7. **Real-Time Web Dashboard**: Built-in dark-mode glassmorphic interface at `http://localhost:8000` with live heartbeats, node rack view, replica matrix, and event logs.

---

## 🌐 Coordinator REST API Reference

- `GET /api/cluster/status`: Cluster topology, health summary, and replica matrix.
- `POST /api/objects/upload?key=<name>&rf=3`: Streams object to RF storage nodes.
- `GET /api/objects/download?key=<name>`: Downloads object with automatic failover.
- `GET /api/objects/replicas?key=<name>`: Retrieves replica placement locations.
- `POST /api/objects/audit_and_repair?key=<name>`: Audits and repairs corrupted replicas.
- `POST /api/cluster/rebalance`: Rebalances replica distribution across active nodes.
- `POST /api/nodes/register?node_id=<id>&port=<port>`: Dynamically registers a new storage node.
- `POST /api/nodes/stop?node_id=<id>`: Marks a node as stopped / dead.
- `GET /`: Embedded interactive web management console.
