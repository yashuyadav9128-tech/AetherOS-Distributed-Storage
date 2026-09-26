"""
Automated Test Suite for AetherStore Distributed Storage Cluster
Tests:
 - Node health & streaming storage
 - End-to-end SHA-256 verification
 - Failover retrieval when a replica node crashes
 - Bit-rot corruption detection & self-healing repair
 - Dynamic node expansion & rebalancing
"""
import unittest
import time
import shutil
from pathlib import Path

from cluster.config import DATA_DIR, INITIAL_NODES, EXPANSION_NODES
from cluster.storage_node import StorageNode
from cluster.coordinator import Coordinator
from cluster.client import generate_sample_data, corrupt_node_replica, verify_node_replica, download_object_from_coordinator


class TestClusterOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Clean data dir
        if DATA_DIR.exists():
            shutil.rmtree(DATA_DIR, ignore_errors=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Start 5 initial nodes
        cls.nodes = {}
        for nid, conf in INITIAL_NODES.items():
            node = StorageNode(nid, conf["host"], conf["port"])
            node.start()
            cls.nodes[nid] = node

        # Start coordinator
        cls.coordinator = Coordinator(echo_stdout=False)
        cls.coordinator.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        for node in cls.nodes.values():
            node.stop()
        cls.coordinator.stop()

    def test_01_upload_and_replication(self):
        """Test uploading a 10MB object with RF=3 and verifying on disk."""
        data, checksum = generate_sample_data(10 * 1024 * 1024)
        key = "test_10mb.bin"
        res = self.coordinator.upload_object_bytes(key, data, rf=3, expected_checksum=checksum)

        self.assertEqual(len(res["replicas"]), 3)
        self.assertEqual(res["sha256"], checksum)

        # Check each replica exists on disk
        for nid in res["replicas"]:
            path = self.nodes[nid].storage_dir / key
            self.assertTrue(path.exists())
            self.assertEqual(path.stat().st_size, len(data))

    def test_02_failover_download(self):
        """Test download failover when one replica node is stopped."""
        data, checksum = generate_sample_data(5 * 1024 * 1024)
        key = "failover_test.bin"
        res = self.coordinator.upload_object_bytes(key, data, rf=3, expected_checksum=checksum)
        replicas = res["replicas"]

        # Stop first replica node
        first_nid = replicas[0]
        self.nodes[first_nid].stop()
        self.coordinator.mark_node_stopped(first_nid)

        # Attempt download
        dest = DATA_DIR / "client_download" / "failover_verified.bin"
        dl_res = download_object_from_coordinator(key, dest)
        self.assertTrue(dl_res["is_valid"])
        self.assertNotEqual(dl_res["source_node"], first_nid)
        self.assertIn(dl_res["source_node"], replicas[1:])

        # Restart node
        conf = INITIAL_NODES[first_nid]
        restarted_node = StorageNode(first_nid, conf["host"], conf["port"])
        restarted_node.start()
        self.nodes[first_nid] = restarted_node
        self.coordinator.nodes[first_nid]["status"] = "ONLINE"

    def test_03_corruption_detection_and_repair(self):
        """Test that bit-rot corruption is detected and repaired from healthy replicas."""
        data, checksum = generate_sample_data(5 * 1024 * 1024)
        key = "repair_test.bin"
        res = self.coordinator.upload_object_bytes(key, data, rf=3, expected_checksum=checksum)
        target_nid = res["replicas"][-1]
        node = self.nodes[target_nid]

        # Corrupt target replica
        corrupt_res = corrupt_node_replica(node.host, node.port, key)
        self.assertEqual(corrupt_res["status"], "corrupted")

        # Verify corruption detected
        verify_res = verify_node_replica(node.host, node.port, key)
        self.assertFalse(verify_res["valid"])

        # Auto-repair
        repair_res = self.coordinator.audit_and_repair(key)
        self.assertIn(target_nid, repair_res.get("repaired", []))

        # Re-verify replica is valid again
        verify_after = verify_node_replica(node.host, node.port, key)
        self.assertTrue(verify_after["valid"])
        self.assertEqual(verify_after["actual_checksum"], checksum)

    def test_04_expansion_and_rebalancing(self):
        """Test adding Node-6 and running rebalancing."""
        new_nid = "Node-6"
        new_conf = EXPANSION_NODES[new_nid]
        new_node = StorageNode(new_nid, new_conf["host"], new_conf["port"])
        new_node.start()
        self.nodes[new_nid] = new_node

        self.coordinator.register_node(new_nid, new_conf["host"], new_conf["port"])
        self.assertIn(new_nid, self.coordinator.nodes)

        # Mark Node-2 dead to test rebalancing into Node-6
        self.coordinator.mark_node_stopped("Node-2")
        rebal_res = self.coordinator.rebalance_cluster()
        self.assertEqual(rebal_res["status"], "rebalanced")


if __name__ == "__main__":
    unittest.main()
