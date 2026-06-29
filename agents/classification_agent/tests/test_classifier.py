"""Tests for SmartBankIntentClassifier — Phase 02."""

from __future__ import annotations

import uuid

import pytest

from agents.classification_agent.classifier import (
    ClassificationResult,
    Entities,
    SmartBankIntentClassifier,
)


@pytest.fixture
def classifier() -> SmartBankIntentClassifier:
    return SmartBankIntentClassifier(config={
        "api_key": "test-key",
        "model": "test-model",
        "confidence_threshold": 0.65,
    })


class TestClassification:
    def test_atm_card_activation_en(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("please activate my atm card", "web")
        assert result.intent.code == "ATM01"
        assert result.intent.confidence >= 0.65

    def test_pin_reset_urdu(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("Mera PIN reset kar do", "mobile")
        assert result.intent.code == "PIN02"

    def test_card_block_critical(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("Mera debit card block karo, koi transaction nahi tha meri", "web")
        assert result.intent.code == "DEB03"
        assert result.intent.confidence >= 0.65

    def test_statement_request(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("Please send my bank statement for last month", "web")
        assert result.intent.code == "STM04"

    def test_account_letter(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("Mujhe account opening letter chahiye", "web")
        assert result.intent.code == "LTR05"

    def test_cnic_update(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("I need to update my CNIC number in the system", "web")
        assert result.intent.code == "NIC06"

    def test_internet_banking_recovery(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("Mera internet banking recover karo", "mobile")
        assert result.intent.code == "IB07"

    def test_mobile_banking_activation(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("I want mobile banking activation", "web")
        assert result.intent.code == "MB08"

    def test_empty_input(self, classifier: SmartBankIntentClassifier):
        with pytest.raises(ValueError, match="empty"):
            classifier.classify("", "web")

    def test_low_confidence_escalation(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("Some random gibberish that means nothing xyz123", "web")
        assert result.escalate_to_human is True

    def test_pii_masking(self, classifier: SmartBankIntentClassifier):
        entities = Entities(
            cnic="12345-1234567-1",
            account_number="1234567890123456",
        )
        masked = classifier.mask_pii(entities)
        assert "*****" in str(masked.account_number)
        assert "*****-***" in str(masked.cnic)

    def test_entity_extraction_account(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("My account number is 1234567890", "web")
        assert result.entities.account_number is not None

    def test_output_schema(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("I lost my card, block it immediately", "ivr")
        assert isinstance(result.request_id, str)
        assert uuid.UUID(result.request_id)
        assert result.timestamp
        assert result.channel == "ivr"

    def test_multi_lingual_mixed(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("Mera card block kar do please, urgent hai", "web")
        assert result.detected_language in ("ur", "mixed")
        assert result.intent.code == "DEB03"

    def test_profanity_filtering(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("Arey shit mera paisa, card block karo", "web")
        assert result.intent.code == "UNKNOWN"
        assert result.escalate_to_human is True

    def test_missing_fields(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("I need a new PIN", "web")
        assert isinstance(result.missing_fields, list)

    def test_follow_up_generation(self, classifier: SmartBankIntentClassifier):
        result = classifier.classify("Activate my card", "web")
        if result.missing_fields:
            assert result.follow_up_question

    def test_validate_entities(self, classifier: SmartBankIntentClassifier):
        entities = Entities(account_number="1234567890")
        missing = classifier.validate_entities("ATM01", entities)
        assert "cnic" in missing

    def test_get_intent_definitions(self, classifier: SmartBankIntentClassifier):
        defs = classifier.get_intent_definitions()
        assert len(defs) == 8
        codes = [d["code"] for d in defs]
        assert "ATM01" in codes
        assert "DEB03" in codes
