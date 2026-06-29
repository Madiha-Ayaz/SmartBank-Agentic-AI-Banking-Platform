import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from robots.cbs_connector.robot import CBSConnectorRobot


class TestCBSConnector:
    def setup_method(self):
        os.environ["CBS_SIMULATION_MODE"] = "true"
        os.environ["CBS_MOCK_DATA_PATH"] = ""
        os.environ["CBS_USERNAME"] = "admin"
        os.environ["CBS_PASSWORD"] = "password"
        self.robot = CBSConnectorRobot()

    def test_login_returns_token(self):
        token = self.robot.login("admin", "password")
        assert token is not None
        assert hasattr(token, 'access_token')

    def test_get_account_status_returns_data(self):
        self.robot.login("admin", "password")
        status = self.robot.get_account_status("ACC-001")
        assert status is not None

    def test_update_account_record(self):
        self.robot.login("admin", "password")
        result = self.robot.update_account_record("ACC-001", {"status": "frozen"})
        assert result is not None

    def test_logout_clears_session(self):
        self.robot.login("admin", "password")
        assert self.robot._session_active is True
        self.robot.logout()
        assert self.robot._session_active is False

    def test_multiple_operations_in_session(self):
        self.robot.login("admin", "password")
        s1 = self.robot.get_account_status("ACC-001")
        self.robot.update_account_record("ACC-001", {"balance": 5000})
        s2 = self.robot.get_account_status("ACC-001")
        self.robot.logout()
        assert s1 is not None and s2 is not None
