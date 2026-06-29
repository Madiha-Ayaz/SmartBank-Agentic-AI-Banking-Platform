import sys, os, tempfile, json, threading
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from robots.audit_logger.robot import AuditLoggerRobot


class TestAuditLogger:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["AUDIT_LOG_DIR"] = self.tmp
        self.robot = AuditLoggerRobot()

    def test_log_entry_creates_file(self):
        entry = self.robot.log_entry("CREATE", "admin", {"case_id": "Case-001"}, {"status": "created"}, "user1", "SUCCESS")
        assert entry.action == "CREATE"
        import datetime
        ym = datetime.datetime.now(datetime.timezone.utc).strftime("%Y.%m")
        log_file = Path(self.tmp) / f"audit-{ym}.json"
        assert log_file.exists()

    def test_hash_chain_integrity(self):
        self.robot.log_entry("CREATE", "admin", {"case_id": "Case-001"}, None, "user1", "SUCCESS")
        self.robot.log_entry("UPDATE", "agent", {"case_id": "Case-001"}, None, "user2", "SUCCESS")
        self.robot.log_entry("DELETE", "admin", {"case_id": "Case-001"}, None, "user1", "SUCCESS")
        assert self.robot.verify_integrity(3) is True

    def test_tamper_detection(self):
        self.robot.log_entry("CREATE", "admin", {"case_id": "Case-001"}, None, "user1", "SUCCESS")
        self.robot.log_entry("UPDATE", "agent", {"case_id": "Case-001"}, None, "user2", "SUCCESS")
        files = list(Path(self.tmp).glob("audit-*.json"))
        with open(files[0], "r") as f:
            lines = f.readlines()
        data = json.loads(lines[1])
        data["action"] = "TAMPERED"
        with open(files[0], "w") as f:
            f.write(json.dumps(data) + "\n")
        assert self.robot.verify_integrity(2) is False

    def test_empty_log_is_valid(self):
        assert self.robot.verify_integrity(0) is True

    def test_concurrent_logging(self):
        results = []
        def log_thread(n):
            e = self.robot.log_entry("CREATE", f"user{n}", {"case_id": f"Case-{n}"}, None, f"user{n}", "SUCCESS")
            results.append(e)
        threads = [threading.Thread(target=log_thread, args=(i,)) for i in range(10)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert len(results) == 10
        assert self.robot.verify_integrity(10) is True
