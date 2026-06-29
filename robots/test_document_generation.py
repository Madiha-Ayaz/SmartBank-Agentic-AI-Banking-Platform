import sys, os
from pathlib import Path
from datetime import date
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from robots.document_generation.robot import DocumentGenerationRobot


class TestDocumentGeneration:
    def setup_method(self):
        self.tmp = Path(__file__).resolve().parent / "__tmp_docs"
        os.environ["OUTPUT_DIR"] = str(self.tmp)
        self.tmp.mkdir(exist_ok=True)
        self.robot = DocumentGenerationRobot()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_generate_statement_creates_doc(self):
        doc = self.robot.generate_statement("ACC-001", (date(2026, 1, 1), date(2026, 6, 1)))
        assert doc is not None

    def test_generate_letter_creates_doc(self):
        doc = self.robot.generate_letter("CUST-001", "account_opening")
        assert doc is not None

    def test_generate_confirmation_creates_doc(self):
        doc = self.robot.generate_confirmation("card_activation", {"name": "Ali Ahmed", "card_last_four": "1234"})
        assert doc is not None

    def test_invalid_letter_type(self):
        try:
            self.robot.generate_letter("CUST-001", "invalid_type")
            assert False, "Should have raised"
        except (ValueError, KeyError):
            pass

    def test_empty_account_id(self):
        try:
            self.robot.generate_statement("", (date(2026, 1, 1), date(2026, 6, 1)))
            assert False, "Should have raised"
        except (ValueError, KeyError):
            pass
