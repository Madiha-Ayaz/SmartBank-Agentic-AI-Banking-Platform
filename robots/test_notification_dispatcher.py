import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from robots.notification_dispatcher.robot import NotificationDispatcherRobot


class TestNotificationDispatcher:
    def setup_method(self):
        os.environ["SMTP_HOST"] = ""
        os.environ["TWILIO_ACCOUNT_SID"] = ""
        self.robot = NotificationDispatcherRobot()

    def test_send_email_returns_receipt(self):
        receipt = self.robot.send_email("test@example.com", "Card Activated", "card_activation",
                                        {"customer_name": "Ali", "card_type": "Visa", "card_last4": "1234"})
        assert receipt is not None

    def test_send_sms_returns_receipt(self):
        receipt = self.robot.send_sms("+923001234567", "card_activation", {"card_last4": "1234"})
        assert receipt is not None

    def test_send_whatsapp_returns_receipt(self):
        receipt = self.robot.send_whatsapp("+923001234567", "card_activation", {"card_type": "Visa", "card_last4": "1234"})
        assert receipt is not None

    def test_send_email_with_all_params(self):
        receipt = self.robot.send_email("test@example.com", "Account Opened", "account_opening",
                                        {"customer_name": "Ali", "account_number": "PK12ABCD0000001234"})
        assert receipt is not None

    def test_missing_template_raises_error(self):
        try:
            self.robot.send_email("test@example.com", "Test", "nonexistent_template", {})
            assert False, "Should have raised"
        except KeyError:
            pass
