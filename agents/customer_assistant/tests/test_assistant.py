"""Tests for SmartBankAssistant (Zara) — Phase 06.

Covers all 5 capability modules, language detection, escalation,
fallback, and multi-turn conversation.
"""

from __future__ import annotations

import pytest

from agents.customer_assistant.assistant import (

    Language,
    Response,
    SmartBankAssistant,
    PRODUCT_INFO,
    PROCESS_GUIDES,
    SME_INFO,
    SAFETY_TIPS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def zara() -> SmartBankAssistant:
    """Return a fresh SmartBankAssistant instance."""
    return SmartBankAssistant()


# ---------------------------------------------------------------------------
# Module 1: Product Education
# ---------------------------------------------------------------------------

class TestProductEducation:
    """Tests for the Product Education module."""

    @pytest.mark.parametrize(
        ("message", "language", "expected_topic"),
        [
            ("What types of accounts do you have?", "en", "account_types"),
            ("What are the profit rates?", "en", "profit_rates"),
            ("How much is the debit card fee?", "en", "fees"),
            ("How many ATMs does SmartBank have?", "en", "atm_network"),
            ("What are the digital limits?", "en", "digital_limits"),
        ],
    )
    def test_en_product_queries(
        self,
        zara: SmartBankAssistant,
        message: str,
        language: str,
        expected_topic: str,
    ) -> None:
        """English product queries return correct module info."""
        response = zara.process_message(message, language)
        assert response.module == "product_education"
        assert response.language == Language.ENGLISH
        expected_info = PRODUCT_INFO[expected_topic]["en"]
        assert response.text == expected_info

    @pytest.mark.parametrize(
        ("message", "language", "expected_topic"),
        [
            ("Bachat Account par kitna profit milta hai?", "ur", "profit_rates"),
            ("Asaan Account mein minimum balance kitna hai?", "ur", "account_types"),
            ("Debit card ki annual fee kitni hai?", "ur", "fees"),
            ("SmartBank ke ATM kahan hain?", "ur", "atm_network"),
            ("RAAST limit kya hai?", "ur", "digital_limits"),
        ],
    )
    def test_ur_product_queries(
        self,
        zara: SmartBankAssistant,
        message: str,
        language: str,
        expected_topic: str,
    ) -> None:
        """Roman Urdu product queries return correct module info."""
        response = zara.process_message(message, language)
        assert response.module == "product_education"
        assert response.language == Language.ROMAN_URDU
        expected_info = PRODUCT_INFO[expected_topic]["ur"]
        assert response.text == expected_info

    def test_get_product_info_direct(self, zara: SmartBankAssistant) -> None:
        """Direct call to get_product_info returns expected data."""
        info = zara.get_product_info("profit_rates")
        assert "Bachat Account profit rates" in info["en"]
        assert "Bachat Account profit rates" in info["ur"]


# ---------------------------------------------------------------------------
# Module 2: Process Guidance
# ---------------------------------------------------------------------------

class TestProcessGuidance:
    """Tests for the Process Guidance module."""

    @pytest.mark.parametrize(
        ("message", "language", "expected_process"),
        [
            ("How do I open a Bachat Account?", "en", "account_opening"),
            ("How do I order a debit card?", "en", "debit_card_ordering"),
            ("How do I register for internet banking?", "en", "internet_banking"),
            ("How do I create a RAAST ID?", "en", "raast_id"),
            ("What is PayPak?", "en", "paypak"),
        ],
    )
    def test_en_process_queries(
        self,
        zara: SmartBankAssistant,
        message: str,
        language: str,
        expected_process: str,
    ) -> None:
        """English process queries return correct step-by-step guide."""
        response = zara.process_message(message, language)
        assert response.module == "process_guidance"
        assert response.language == Language.ENGLISH
        expected_guide = PROCESS_GUIDES[expected_process]["en"]
        assert response.text == expected_guide

    @pytest.mark.parametrize(
        ("message", "language", "expected_process"),
        [
            ("Account kaise kholen?", "ur", "account_opening"),
            ("Debit card kaise order karein?", "ur", "debit_card_ordering"),
            ("Internet banking kaise register karein?", "ur", "internet_banking"),
            ("RAAST ID kaise banayein?", "ur", "raast_id"),
            ("PayPak kya hai?", "ur", "paypak"),
        ],
    )
    def test_ur_process_queries(
        self,
        zara: SmartBankAssistant,
        message: str,
        language: str,
        expected_process: str,
    ) -> None:
        """Roman Urdu process queries return correct step-by-step guide."""
        response = zara.process_message(message, language)
        assert response.module == "process_guidance"
        assert response.language == Language.ROMAN_URDU
        expected_guide = PROCESS_GUIDES[expected_process]["ur"]
        assert response.text == expected_guide

    def test_get_process_guide_direct(self, zara: SmartBankAssistant) -> None:
        """Direct call to get_process_guide returns expected data."""
        guide = zara.get_process_guide("raast_id")
        assert "Open SmartBank App" in guide["en"]
        assert "SmartBank App kholen" in guide["ur"]


# ---------------------------------------------------------------------------
# Module 3: SME Financial Literacy
# ---------------------------------------------------------------------------

class TestSMELiteracy:
    """Tests for the SME Financial Literacy module."""

    @pytest.mark.parametrize(
        ("message", "language", "expected_topic"),
        [
            ("What types of business accounts do you offer?", "en", "business_accounts"),
            ("How does trade finance work?", "en", "trade_finance"),
            ("How do I manage cash flow?", "en", "cash_flow"),
            ("What SBP MSME schemes are available?", "en", "sbp_msme"),
        ],
    )
    def test_en_sme_queries(
        self,
        zara: SmartBankAssistant,
        message: str,
        language: str,
        expected_topic: str,
    ) -> None:
        """English SME queries return correct module info."""
        response = zara.process_message(message, language)
        assert response.module == "sme_literacy"
        assert response.language == Language.ENGLISH
        expected_info = SME_INFO[expected_topic]["en"]
        assert response.text == expected_info

    @pytest.mark.parametrize(
        ("message", "language", "expected_topic"),
        [
            ("Business account ke liye kya documents chahiye?", "ur", "business_accounts"),
            ("Trade finance kya hota hai?", "ur", "trade_finance"),
            ("Cash flow kaise manage karein?", "ur", "cash_flow"),
            ("SBP MSME scheme kya hai?", "ur", "sbp_msme"),
        ],
    )
    def test_ur_sme_queries(
        self,
        zara: SmartBankAssistant,
        message: str,
        language: str,
        expected_topic: str,
    ) -> None:
        """Roman Urdu SME queries return correct module info."""
        response = zara.process_message(message, language)
        assert response.module == "sme_literacy"
        assert response.language == Language.ROMAN_URDU
        expected_info = SME_INFO[expected_topic]["ur"]
        assert response.text == expected_info


# ---------------------------------------------------------------------------
# Module 4: Digital Onboarding Helper
# ---------------------------------------------------------------------------

class TestDigitalOnboarding:
    """Tests for the Digital Onboarding Helper module."""

    @pytest.mark.parametrize(
        ("message", "language"),
        [
            ("Main ne kabhi app use nahi kiya", "ur"),
            ("I need help with the app", "en"),
            ("Mujhe app sikhna hai", "ur"),
            ("Can you guide me, I'm new to banking", "en"),
        ],
    )
    def test_onboarding_response(
        self, zara: SmartBankAssistant, message: str, language: str
    ) -> None:
        """Onboarding queries return the onboarding prompt with large-button UI."""
        response = zara.process_message(message, language)
        assert response.module == "digital_onboarding"
        assert "large-button" in response.ui_components
        # Response should be helpful onboarding text
        assert len(response.text) > 20

    def test_onboarding_urdu_contains_salam(self, zara: SmartBankAssistant) -> None:
        """Roman Urdu onboarding response includes Salam greeting."""
        response = zara.process_message("Mujhe guide karein", "ur")
        assert "Salam" in response.text


# ---------------------------------------------------------------------------
# Module 5: Safety & Fraud Awareness
# ---------------------------------------------------------------------------

class TestSafetyFraud:
    """Tests for the Safety & Fraud Awareness module."""

    @pytest.mark.parametrize(
        ("message", "language", "expected_tip_key"),
        [
            ("Someone called and asked for my OTP", "en", "otp"),
            ("Kisi ne mujhe call karke OTP manga", "ur", "otp"),
            ("I got a vishing call", "en", "vishing"),
            ("Mujhe ek phishing link aaya hai", "ur", "phishing"),
            ("My mobile network suddenly died", "en", "sim_swap"),
            ("ATM par PIN kaise safe rakhein?", "ur", "card_skimming"),
        ],
    )
    def test_safety_triggers(
        self,
        zara: SmartBankAssistant,
        message: str,
        language: str,
        expected_tip_key: str,
    ) -> None:
        """Safety-related queries return the correct fraud awareness tip."""
        response = zara.process_message(message, language)
        assert response.module == "safety_fraud"
        expected_tip = SAFETY_TIPS[expected_tip_key]
        expected_text = expected_tip.get(
            "ur" if language == "ur" else "en",
            expected_tip["en"],
        )
        assert response.text == expected_text

    def test_handle_safety_check_otp(self, zara: SmartBankAssistant) -> None:
        """handle_safety_check returns correct OTP tip."""
        tip = zara.handle_safety_check("otp")
        assert "OTP" in tip
        assert "never" in tip.lower() or "NEVER" in tip

    def test_handle_safety_check_phishing(self, zara: SmartBankAssistant) -> None:
        """handle_safety_check returns correct phishing tip."""
        tip = zara.handle_safety_check("phishing")
        assert "phishing" in tip.lower() or "link" in tip.lower()

    def test_handle_safety_check_unknown_trigger(self, zara: SmartBankAssistant) -> None:
        """handle_safety_check with unknown trigger defaults to OTP tip."""
        tip = zara.handle_safety_check("xyz")
        assert "OTP" in tip


# ---------------------------------------------------------------------------
# Escalation
# ---------------------------------------------------------------------------

class TestEscalation:
    """Tests for human agent escalation."""

    @pytest.mark.parametrize(
        ("message", "language", "expected_reason"),
        [
            ("Main case karna chahta hoon", "ur", "complaint"),
            ("I want to file a complaint", "en", "complaint"),
            ("Mera account block hai", "ur", "blocked_account"),
            ("My account is blocked", "en", "blocked_account"),
            ("Main baat karna chahta hoon kisi se", "ur", "human_request"),
            ("I need a loan", "en", "loan"),
            ("Mujhe loan chahiye", "ur", "loan"),
            ("Mujhe fraud hua hai", "ur", "fraud_event"),
            ("I have been defrauded", "en", "fraud_event"),
            ("Main apna password bhool gaya", "ur", "forgot_password"),
            ("I forgot my password", "en", "forgot_password"),
            ("Aap ne mera paisa kat liya", "ur", "dispute"),
            ("You deducted my money", "en", "dispute"),
            ("I want to talk to a human", "en", "human_request"),
        ],
    )
    def test_escalation_triggers(
        self,
        zara: SmartBankAssistant,
        message: str,
        language: str,
        expected_reason: str,
    ) -> None:
        """Escalation trigger phrases result in escalated response."""
        response = zara.process_message(message, language)
        assert response.escalation is True
        assert response.escalation_reason == expected_reason

    def test_escalate_to_human_direct(self, zara: SmartBankAssistant) -> None:
        """Direct call to escalate_to_human returns proper Response."""
        response = zara.escalate_to_human("complaint", Language.ROMAN_URDU)
        assert response.escalation is True
        assert response.escalation_reason == "complaint"
        assert "complaint officer" in response.text or "complaint" in response.text.lower()


# ---------------------------------------------------------------------------
# Language Detection
# ---------------------------------------------------------------------------

class TestLanguageDetection:
    """Tests for language detection."""

    @pytest.mark.parametrize(
        ("message", "expected_language"),
        [
            ("What types of accounts do you offer?", Language.ENGLISH),
            ("How do I open an account?", Language.ENGLISH),
            ("Bachat Account par kitna profit milta hai?", Language.ROMAN_URDU),
            ("Mujhe debit card order karna hai", Language.ROMAN_URDU),
            ("کیا آپ مدد کر سکتے ہیں؟", Language.URDU_SCRIPT),
            ("SmartBank mein account kholne ka tareeqa kya hai?", Language.MIXED),
        ],
    )
    def test_detect_language(
        self,
        zara: SmartBankAssistant,
        message: str,
        expected_language: Language,
    ) -> None:
        """Language detection classifies messages correctly."""
        detected = zara.detect_language(message)
        assert detected == expected_language


# ---------------------------------------------------------------------------
# Unknown Query Fallback
# ---------------------------------------------------------------------------

class TestFallback:
    """Tests for unknown query fallback."""

    @pytest.mark.parametrize(
        ("message", "language", "expected_language"),
        [
            ("xyz random gibberish 123", "en", Language.ENGLISH),
            ("asdf qwerty zxcv", "ur", Language.ROMAN_URDU),
        ],
    )
    def test_fallback_response(
        self,
        zara: SmartBankAssistant,
        message: str,
        language: str,
        expected_language: Language,
    ) -> None:
        """Unknown queries return a fallback response without crashing."""
        response = zara.process_message(message, language)
        assert response.module is None
        assert response.language == expected_language
        assert len(response.text) > 10
        assert "sorry" in response.text.lower() or "maaf" in response.text.lower()

    def test_empty_message(self, zara: SmartBankAssistant) -> None:
        """Empty message returns a greeting."""
        response = zara.process_message("", "en")
        assert "Hello" in response.text or "Salam" in response.text

    def test_whitespace_message(self, zara: SmartBankAssistant) -> None:
        """Whitespace-only message returns a greeting."""
        response = zara.process_message("   ", "ur")
        assert "Salam" in response.text


# ---------------------------------------------------------------------------
# Multi-turn Conversation
# ---------------------------------------------------------------------------

class TestMultiTurnConversation:
    """Tests for multi-turn conversation handling."""

    def test_product_followed_by_process(self, zara: SmartBankAssistant) -> None:
        """Conversation: product question followed by process question."""
        r1 = zara.process_message("What are Bachat Account profit rates?", "en")
        assert r1.module == "product_education"

        r2 = zara.process_message("How do I open a Bachat Account?", "en")
        assert r2.module == "process_guidance"

    def test_safety_then_escalation(self, zara: SmartBankAssistant) -> None:
        """Conversation: safety query then escalation."""
        r1 = zara.process_message("Someone asked for my OTP", "en")
        assert r1.module == "safety_fraud"

        r2 = zara.process_message("Main case karna chahta hoon", "ur")
        assert r2.escalation is True
        assert r2.escalation_reason == "complaint"

    def test_language_switch_mid_conversation(self, zara: SmartBankAssistant) -> None:
        """Conversation switching between English and Urdu."""
        r1 = zara.process_message("What types of accounts?", "en")
        assert r1.language == Language.ENGLISH

        r2 = zara.process_message("Bachat Account par kitna profit hai?", "ur")
        assert r2.language == Language.ROMAN_URDU

    def test_onboarding_then_sme(self, zara: SmartBankAssistant) -> None:
        """Conversation: onboarding help then SME question."""
        r1 = zara.process_message("Mujhe app use karna nahi aata", "ur")
        assert r1.module == "digital_onboarding"

        r2 = zara.process_message("SBP MSME scheme kya hai?", "ur")
        assert r2.module == "sme_literacy"


# ---------------------------------------------------------------------------
# Intent Detection
# ---------------------------------------------------------------------------

class TestIntentDetection:
    """Tests for the detect_intent method."""

    @pytest.mark.parametrize(
        ("message", "expected_intent"),
        [
            ("What are the account types?", "product_education"),
            ("How do I open an account?", "process_guidance"),
            ("Tell me about SME financing", "sme_literacy"),
            ("I need help using the app", "digital_onboarding"),
            ("Someone asked for my OTP", "safety_fraud"),
            ("xyz unknown gibberish", "unknown"),
        ],
    )
    def test_detect_intent(
        self,
        zara: SmartBankAssistant,
        message: str,
        expected_intent: str,
    ) -> None:
        """detect_intent classifies messages to the correct module."""
        intent = zara.detect_intent(message)
        assert intent == expected_intent


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Tests for edge cases and robustness."""

    def test_very_long_message(self, zara: SmartBankAssistant) -> None:
        """Very long messages are handled without error."""
        long_msg = "account " * 200
        response = zara.process_message(long_msg, "en")
        assert response.text is not None

    def test_message_with_special_characters(self, zara: SmartBankAssistant) -> None:
        """Messages with special characters are handled."""
        response = zara.process_message("OTP!? @#$%^&*()", "en")
        assert response.text is not None

    def test_message_with_numbers_only(self, zara: SmartBankAssistant) -> None:
        """Numeric messages fall back gracefully."""
        response = zara.process_message("12345 67890", "en")
        assert response.text is not None

    def test_get_product_info_unknown_topic(self, zara: SmartBankAssistant) -> None:
        """Unknown product topic defaults to account_types."""
        info = zara.get_product_info("nonexistent_topic")
        assert "Asaan Account" in info["en"]

    def test_get_process_guide_unknown_process(self, zara: SmartBankAssistant) -> None:
        """Unknown process name defaults to account_opening."""
        guide = zara.get_process_guide("nonexistent_process")
        assert "branch" in guide["en"].lower() or "jayein" in guide["ur"]
