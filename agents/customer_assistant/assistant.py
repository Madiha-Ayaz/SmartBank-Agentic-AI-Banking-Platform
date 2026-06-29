"""
SmartBank Assistant — Zara

An AI-powered banking guide for SmartBank (Pakistan).
Supports English, Roman Urdu, and Urdu script.
5 capability modules: Product Education, Process Guidance, SME Literacy,
Digital Onboarding, and Safety & Fraud Awareness.
"""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from typing import Optional


class Language(str, enum.Enum):
    """Supported languages for Zara."""

    ENGLISH = "en"
    ROMAN_URDU = "ur"
    URDU_SCRIPT = "ur-arab"
    MIXED = "mixed"


@dataclass
class Response:
    """Structured response from Zara."""

    text: str
    language: Language
    module: Optional[str] = None
    ui_components: list[str] = field(default_factory=list)
    escalation: bool = False
    escalation_reason: Optional[str] = None


# ---------------------------------------------------------------------------
# Knowledge Base
# ---------------------------------------------------------------------------

PRODUCT_INFO: dict[str, dict[str, str]] = {
    "account_types": {
        "en": (
            "SmartBank offers: Asaan Account (zero-balance, basic banking), "
            "Bachat Account (profit-earning savings), Current Account (business/transactions), "
            "Senior Citizen Account (higher profit rates), and Youth Account (ages 12-18). "
            "Which one interests you?"
        ),
        "ur": (
            "SmartBank yeh accounts offer karta hai: Asaan Account (zero balance), "
            "Bachat Account (profit wala), Current Account (business ke liye), "
            "Senior Citizen Account (zyada profit), aur Youth Account (12-18 saal ke liye). "
            "Aap ko konsa chahiye?"
        ),
    },
    "profit_rates": {
        "en": (
            "Bachat Account profit rates (p.a.): up to PKR 50K — 5.5%, "
            "PKR 50K-500K — 8%, PKR 500K-5M — 10.5%, above PKR 5M — 12%. "
            "Senior Citizen Account gets an extra 1% bonus. "
            "Rates may change as per SBP guidelines."
        ),
        "ur": (
            "Bachat Account profit rates (p.a.): PKR 50K tak — 5.5%, "
            "PKR 50K se 500K — 8%, PKR 500K se 5M — 10.5%, "
            "PKR 5M se upar — 12%. Senior Citizen Account mein 1% extra hai. "
            "Yeh rates SBP ke mutabiq badal sakte hain."
        ),
    },
    "fees": {
        "en": (
            "Debit card annual fee: PKR 500. "
            "SmartBank ATM withdrawals: free. "
            "Other 1LINK ATM: PKR 15 per transaction. "
            "IBFT: PKR 5-20 per transfer."
        ),
        "ur": (
            "Debit card annual fee: PKR 500. "
            "SmartBank ATM se paise nikalna: free. "
            "Doosre 1LINK ATM: PKR 15 har baar. "
            "IBFT: PKR 5-20 har transfer."
        ),
    },
    "atm_network": {
        "en": "SmartBank has 400+ ATMs across 150 cities. You can also use 15,000+ 1LINK ATMs nationwide.",
        "ur": "SmartBank ke 400+ ATM hain 150 cities mein. Aap 15,000+ 1LINK ATM bhi use kar sakte hain.",
    },
    "digital_limits": {
        "en": (
            "Daily limits: RAAST — PKR 1M, IBFT — PKR 500K, "
            "Card POS — PKR 200K, Card ATM — PKR 50K. "
            "These can be customised at your branch."
        ),
        "ur": (
            "Daily limits: RAAST — PKR 1M, IBFT — PKR 500K, "
            "Card POS — PKR 200K, Card ATM — PKR 50K. "
            "Yeh limits branch se badal sakte hain."
        ),
    },
}

PROCESS_GUIDES: dict[str, dict[str, str]] = {
    "account_opening": {
        "en": (
            "1. Visit branch or use SmartBank App.\n"
            "2. Provide CNIC (original + copy).\n"
            "3. Provide proof of residence (utility bill).\n"
            "4. One passport-size photograph.\n"
            "5. Initial deposit: PKR 0 (Asaan) or PKR 1,000 (Bachat).\n"
            "6. Biometric verification.\n"
            "7. Welcome kit in 3-5 working days."
        ),
        "ur": (
            "1. Branch jayein ya SmartBank App use karein.\n"
            "2. CNIC (asli + copy) dein.\n"
            "3. Pata ka saboot (utility bill) dein.\n"
            "4. Ek passport-size photo.\n"
            "5. Pehli jam'aa: PKR 0 (Asaan) ya PKR 1,000 (Bachat).\n"
            "6. Biometric verification.\n"
            "7. Welcome kit 3-5 din mein aa jayega."
        ),
    },
    "debit_card_ordering": {
        "en": (
            "Via app: Menu > Cards > Order Debit Card.\n"
            "Via branch: request at counter.\n"
            "Delivery in 3-5 working days.\n"
            "Activate via app or ATM PIN change."
        ),
        "ur": (
            "App se: Menu > Cards > Order Debit Card.\n"
            "Branch se: counter par request karein.\n"
            "3-5 din mein aap ke pate par aa jayega.\n"
            "App ya ATM se activate karein."
        ),
    },
    "internet_banking": {
        "en": (
            "1. Visit smartbank.com.pk/ibanking.\n"
            "2. Click 'Register'.\n"
            "3. Enter CNIC + account number.\n"
            "4. OTP aayega mobile par — enter it.\n"
            "5. Set username + password.\n"
            "6. Set security questions."
        ),
        "ur": (
            "1. smartbank.com.pk/ibanking par jayein.\n"
            "2. 'Register' par click karein.\n"
            "3. CNIC aur account number daalein.\n"
            "4. OTP aayega mobile par — woh daalein.\n"
            "5. Username aur password set karein.\n"
            "6. Security questions set karein."
        ),
    },
    "raast_id": {
        "en": (
            "1. Open SmartBank App.\n"
            "2. Go to Payments > RAAST.\n"
            "3. Tap 'Create RAAST ID'.\n"
            "4. Choose alias (yourname@smartbank).\n"
            "5. Verify via OTP.\n"
            "6. Share your RAAST ID to receive payments."
        ),
        "ur": (
            "1. SmartBank App kholen.\n"
            "2. Payments > RAAST par jayein.\n"
            "3. 'Create RAAST ID' dabayein.\n"
            "4. Alias choose karein (aapkanaam@smartbank).\n"
            "5. OTP se verify karein.\n"
            "6. RAAST ID share karein — payment turant aa jayega."
        ),
    },
    "paypak": {
        "en": (
            "PayPak is Pakistan's domestic card scheme. "
            "Zero annual fee. Works at all 1LINK ATMs. "
            "Use for local e-commerce shopping. "
            "Tap & pay at NFC-enabled POS machines."
        ),
        "ur": (
            "PayPak Pakistan ka apna card scheme hai. "
            "Zero annual fee. Tamam 1LINK ATMs par kaam karta hai. "
            "Pakistani websites par shopping kar sakte hain. "
            "NFC POS machines par tap & pay karein."
        ),
    },
}

SME_INFO: dict[str, dict[str, str]] = {
    "business_accounts": {
        "en": (
            "SmartBank offers Asaan Business Account (sole proprietor), "
            "Business Plus Account (partnership/LLC), and Corporate Current Account. "
            "Current accounts are non-remunerative as per SBP regulations."
        ),
        "ur": (
            "SmartBank mein Asaan Business Account (sole proprietor), "
            "Business Plus Account (partnership/LLC), aur Corporate Current Account hai. "
            "Current accounts par profit nahi milta (SBP ke mutabiq)."
        ),
    },
    "trade_finance": {
        "en": (
            "LC (Letter of Credit) for imports/exports. "
            "LG (Letter of Guarantee) for bid/performance bonds. "
            "Import financing: up to 180 days. "
            "Export refinance via SBP at concessional rates."
        ),
        "ur": (
            "LC (Letter of Credit) import/export ke liye. "
            "LG (Letter of Guarantee) bid/performance bonds ke liye. "
            "Import financing: 180 din tak. "
            "Export refinance SBP se kam rate par."
        ),
    },
    "cash_flow": {
        "en": (
            "Keep separate accounts for tax (17% sales tax), payroll, and operations. "
            "Use SmartBank Business Dashboard to track flows. "
            "Enable auto-sweep to profit accounts for surplus > PKR 500K."
        ),
        "ur": (
            "Tax (17% sales tax), payroll, aur operations ke liye alag accounts rakhein. "
            "SmartBank Business Dashboard se tracking karein. "
            "PKR 500K se zyada surplus auto-sweep kar dein profit wale account mein."
        ),
    },
    "sbp_msme": {
        "en": (
            "SBP MSME Refinance Scheme: financing up to PKR 25M at ~9% p.a. "
            "Eligible sectors: manufacturing, services, agriculture, IT. "
            "Collateral-free loans up to PKR 500K under PM Youth Scheme."
        ),
        "ur": (
            "SBP MSME Refinance Scheme: PKR 25M tak financing ~9% p.a. par. "
            "Eligible: manufacturing, services, agriculture, IT. "
            "PM Youth Scheme ke tahat PKR 500K tak bina zamanat ke loan."
        ),
    },
}

SAFETY_TIPS: dict[str, dict[str, str]] = {
    "otp": {
        "en": (
            "SmartBank NEVER asks for your OTP. If anyone calls and asks for OTP, "
            "they are a fraudster. Hang up immediately. "
            "If you shared your OTP, call 0800-12345 to freeze your account."
        ),
        "ur": (
            "SmartBank kabhi OTP nahi maangta. Agar koi call kare aur OTP maange, "
            "woh fraud hai. Foran call cut karein. "
            "Agar OTP share kar diya to 0800-12345 par call karein aur account freeze karwayein."
        ),
    },
    "vishing": {
        "en": (
            "Vishing = voice phishing. Fraudsters call pretending to be bank officers. "
            "They say 'aap ka account block ho jayega'. "
            "SmartBank never threatens to block accounts. "
            "Call 0800-12345 to verify any suspicious call."
        ),
        "ur": (
            "Vishing matlab phone par fraud. Fraudsters bank officer ban ke call karte hain. "
            "Kehte hain 'aap ka account block ho jayega'. "
            "SmartBank kabhi account block karne ki dhamki nahi deta. "
            "Koi shak ho to 0800-12345 par call karein."
        ),
    },
    "phishing": {
        "en": (
            "Phishing links come via SMS or email saying 'aap ka account update karein'. "
            "Never click. SmartBank links always start with smartbank.com.pk."
        ),
        "ur": (
            "Phishing links SMS ya email mein aate hain: 'aap ka account update karein'. "
            "Kabhi click na karein. SmartBank links hamesha smartbank.com.pk se shuru hote hain."
        ),
    },
    "sim_swap": {
        "en": (
            "If your mobile network suddenly goes dead, contact SmartBank immediately "
            "to freeze your account. Fraudsters may have cloned your SIM."
        ),
        "ur": (
            "Agar aap ka mobile network achanak band ho jaye, foran SmartBank ko call karein "
            "aur account freeze karwayein. Fraudsters ne SIM clone kar liya ho ga."
        ),
    },
    "card_skimming": {
        "en": (
            "ATM safety: Cover PIN pad with your hand. "
            "Use ATMs in well-lit, secure locations (branch ATMs preferred)."
        ),
        "ur": (
            "ATM safety: PIN pad ko haath se dhak kar rakhein. "
            "Roshni wali jagah par ATM use karein (branch ke ATM behtar hain)."
        ),
    },
}


# ---------------------------------------------------------------------------
# Intent Classification
# ---------------------------------------------------------------------------

_INTENT_PATTERNS: dict[str, list[str]] = {
    "product_education": [
        r"(?:types?|kinds?) of accounts?",
        r"accounts?\s+types?",
        r"profit\b",
        r"rates?\b",
        r"fees?\b",
        r"limits?\b",
        r"atms?\b",
        r"bachat\b",
        r"asaan\b",
        r"debit card",
        r"balances?\b",
        r"minimum balance",
        r"annual",
        r"product",
        r"maaloomat",
        r"kitna\b",
        r"maloomat",
    ],
    "process_guidance": [
        r"open.*account",
        r"account.*open",
        r"khol",
        r"how (?:do|can|to) .*?(?:open|get|start|register|order)",
        r"order.*card",
        r"raast\b",
        r"paypak\b",
        r"internet banking",
        r"debit card.*order",
        r"account khol",
        r"card.*kaise",
        r"raast id",
        r"process",
        r"step.?by.?step",
        r"kaise\b",
        r"kya .* (?:process|guide|tareeqa)",
    ],
    "sme_literacy": [
        r"sme\b",
        r"business account",
        r"trade.*finance",
        r"lc\b",
        r"letter of credit",
        r"cash.?flow",
        r"cashflow",
        r"manage.*cash",
        r"cash.*manage",
        r"sbp\b",
        r"msme\b",
        r"business.*account",
        r"sole proprietor",
        r"partnership",
        r"ntn\b",
        r"secp\b",
        r"loan\b",
        r"financing",
        r"documents?.*(?:business|account)",
    ],
    "digital_onboarding": [
        r"app\b",
        r"download",
        r"register",
        r"onboard",
        r"55",
        r"rural",
        r"voice",
        r"large.?button",
        r"pata nahi",
        r"nahi aata",
        r"sikh",
        r"guide",
        r"help",
        r"madad",
        r"samajh",
        r"bojh",
    ],
    "safety_fraud": [
        r"fraud\b",
        r"otp\b",
        r"phishing",
        r"vishing",
        r"scam\b",
        r"skimming",
        r"sim swap",
        r"safe\b",
        r"safety",
        r"block\b",
        r"call.*manga",
        r"link\b",
        r"dhoka",
        r"hacker",
        r"mehfooz",
        r"khatarnak",
    ],
}

_ESCALATION_PATTERNS: dict[str, str] = {
    r"main case karna chahta": "complaint",
    r"shikayat": "complaint",
    r"file a complaint": "complaint",
    r"mera account (block|band|freeze)": "blocked_account",
    r"my account is blocked": "blocked_account",
    r"main (baat|talk) karna chahta": "human_request",
    r"talk to (a )?(human|person|agent|representative)": "human_request",
    r"kisi se baat": "human_request",
    r"mujhe (loan|qarz|qardh) chahiye": "loan",
    r"i (want|need) a loan": "loan",
    r"fraud hua": "fraud_event",
    r"main dhoka": "fraud_event",
    r"i have been defrauded": "fraud_event",
    r"(password|pin) bhool": "forgot_password",
    r"i forgot my (password|pin)": "forgot_password",
    r"paise kat": "dispute",
    r"mera paisa": "dispute",
    r"you deducted": "dispute",
    r"aap ne mera": "dispute",
}


# ---------------------------------------------------------------------------
# Assistant
# ---------------------------------------------------------------------------

class SmartBankAssistant:
    """Zara — SmartBank's friendly AI banking guide for Pakistan.

    Supports 5 capability modules:
        1. Product Education
        2. Process Guidance
        3. SME Financial Literacy
        4. Digital Onboarding Helper
        5. Safety & Fraud Awareness

    Provides fallback responses and controlled escalation to human agents.
    """

    # ---- Public API -------------------------------------------------------

    def process_message(
        self, user_message: str, language: str = "en"
    ) -> Response:
        """Main entry point for processing a user message.

        Args:
            user_message: The incoming text from the user.
            language: Expected response language hint ('en' or 'ur').

        Returns:
            A Response dataclass with text, language, optional UI components,
            and escalation flags.
        """
        message = user_message.strip()
        if not message:
            return Response(
                text=self._greeting(language),
                language=Language(language),
            )

        detected_lang = self.detect_language(message)
        response_lang = self._resolve_language(detected_lang, language)

        # Check escalation first
        esc_reason = self._check_escalation(message)
        if esc_reason:
            return self.escalate_to_human(esc_reason, response_lang)

        # Check safety triggers
        safety_tip = self._check_safety_trigger(message)
        if safety_tip:
            tip = SAFETY_TIPS[safety_tip]
            text = tip.get(response_lang.value, tip.get("en", ""))
            return Response(
                text=text,
                language=response_lang,
                module="safety_fraud",
            )

        # Classify intent
        intent = self.detect_intent(message)

        if intent == "product_education":
            topic = self._extract_product_topic(message)
            info = self.get_product_info(topic)
            return Response(
                text=info.get(response_lang.value, info.get("en", "")),
                language=response_lang,
                module=intent,
            )

        if intent == "process_guidance":
            process = self._extract_process_name(message)
            guide = self.get_process_guide(process)
            return Response(
                text=guide.get(response_lang.value, guide.get("en", "")),
                language=response_lang,
                module=intent,
            )

        if intent == "sme_literacy":
            topic = self._extract_sme_topic(message)
            info = SME_INFO.get(topic, SME_INFO["business_accounts"])
            text = info.get(response_lang.value, info.get("en", ""))
            return Response(
                text=text,
                language=response_lang,
                module=intent,
            )

        if intent == "digital_onboarding":
            return Response(
                text=self._onboarding_response(response_lang),
                language=response_lang,
                module=intent,
                ui_components=["large-button"],
            )

        if intent == "safety_fraud":
            tip = self._check_safety_trigger(message) or "otp"
            info = SAFETY_TIPS[tip]
            text = info.get(response_lang.value, info.get("en", ""))
            return Response(
                text=text,
                language=response_lang,
                module=intent,
            )

        # Fallback
        return Response(
            text=self._fallback_response(response_lang),
            language=response_lang,
        )

    def detect_intent(self, message: str) -> str:
        """Classify a message into one of the 5 modules or 'unknown'.

        Args:
            message: User message text.

        Returns:
            Intent key string: 'product_education', 'process_guidance',
            'sme_literacy', 'digital_onboarding', 'safety_fraud', or 'unknown'.
        """
        msg_lower = message.lower()
        scores: dict[str, int] = {}
        for intent, patterns in _INTENT_PATTERNS.items():
            score = sum(1 for p in patterns if re.search(p, msg_lower))
            if score > 0:
                scores[intent] = score

        if not scores:
            return "unknown"

        return max(scores, key=scores.get)  # type: ignore[arg-type]

    def detect_language(self, message: str) -> Language:
        """Detect the language of the user message.

        Heuristic: counts Urdu-script characters, Roman Urdu keywords,
        and English words. Returns the best match.

        Args:
            message: The user message.

        Returns:
            Detected Language enum value.
        """
        # Urdu script check
        urdu_chars = sum(1 for c in message if "\u0600" <= c <= "\u06FF")
        if urdu_chars > len(message) * 0.3:
            return Language.URDU_SCRIPT

        # Roman Urdu keywords
        urdu_keywords = {
            "hai", "hoon", "hain", "ka", "ki", "ke", "se", "mein", "par",
            "ko", "aap", "main", "yeh", "woh", "kya", "kaise", "kahan",
            "kitna", "kab", "kis", "kisi", "mujhe", "tum", "acha", "theek", "nahi",
            "haan", "bilkul", "shukriya", "madad", "baat", "karo", "karein",
            "sakta", "sakti", "chahiye", "ho", "ga", "gi", "raha", "rahay",
            "apna", "apni", "us", "kuch", "sab", "bahut", "thora",
            "saath", "liye", "bina", "baad", "pehle", "darmiyan", "agar",
            "lekin", "magar", "ya", "aur", "bhi", "toh", "phir",
            "kholen", "kholna", "banayein", "rakhein", "karwayein",
            "dabayein", "aayega", "jayein", "karte", "karta", "sakte",
            "sakta", "hota", "hoti", "jaan", "dein",
            "karke", "manga", "diya", "hua", "hue",
            "bachat", "milta", "milti", "karna", "karni", "karo",
        }
        words = set(re.findall(r"[a-zA-Z]+", message.lower()))
        overlap = words & urdu_keywords

        # Two or more Urdu keywords signals Roman Urdu or mixed
        if len(overlap) >= 2:
            non_urdu = words - overlap
            # Only classify as mixed if there are 4+ non-Urdu words
            # (fewer English words in a Roman Urdu sentence is normal code-switching)
            if len(non_urdu) >= 4:
                return Language.MIXED
            return Language.ROMAN_URDU

        # Single Urdu keyword with English words = mixed
        en_words = words - urdu_keywords
        if len(overlap) >= 1 and len(en_words) >= 2:
            return Language.MIXED

        return Language.ENGLISH

    def get_product_info(self, topic: str = "account_types") -> dict[str, str]:
        """Retrieve product information for a given topic.

        Args:
            topic: Product topic key (e.g. 'account_types', 'profit_rates').

        Returns:
            Dict mapping language codes to response text.
        """
        return PRODUCT_INFO.get(topic, PRODUCT_INFO["account_types"])

    def get_process_guide(self, process_name: str = "account_opening") -> dict[str, str]:
        """Retrieve a step-by-step process guide.

        Args:
            process_name: Process key (e.g. 'account_opening', 'raast_id').

        Returns:
            Dict mapping language codes to guide text.
        """
        return PROCESS_GUIDES.get(process_name, PROCESS_GUIDES["account_opening"])

    def escalate_to_human(
        self, reason: str, language: Language = Language.ENGLISH
    ) -> Response:
        """Generate escalation response for human handoff.

        Args:
            reason: Escalation reason string.
            language: Response language.

        Returns:
            Response with escalation flag set to True.
        """
        messages = {
            "en": {
                "complaint": "Main aap ko SmartBank ke complaint officer se mila rahi hoon. Shukriya aap ke sabr ka.",
                "blocked_account": "Yeh masla branch manager hi hal kar sakte hain. Main unhein aap se connect karti hoon.",
                "human_request": "Bilkul. Main aap ko SmartBank ke customer care se connect kar rahi hoon.",
                "loan": "Loan ke liye SmartBank ki loan officer se baat karni hogi. Main unhein aap se connect kar deti hoon.",
                "fraud_event": "Yeh bohat ahem masla hai. Main foran SmartBank Fraud Department se connect kar rahi hoon. Mehrbani se 0800-12345 par bhi call karein.",
                "forgot_password": "Password reset ke liye app ya internet banking ka 'Forgot Password' option use karein. Agar nahi ho raha to main branch se connect karti hoon.",
                "dispute": "Transaction dispute ke liye main SmartBank ki dispute resolution team se connect kar rahi hoon.",
            },
            "ur": {
                "complaint": "Main aap ko SmartBank ke complaint officer se mila rahi hoon. Shukriya aap ke sabr ka.",
                "blocked_account": "Yeh masla branch manager hi hal kar sakte hain. Main unhein aap se connect karti hoon.",
                "human_request": "Bilkul. Main aap ko SmartBank ke customer care se connect kar rahi hoon.",
                "loan": "Loan ke liye SmartBank ki loan officer se baat karni hogi. Main unhein aap se connect kar deti hoon.",
                "fraud_event": "Yeh bohat ahem masla hai. Main foran SmartBank Fraud Department se connect kar rahi hoon. Mehrbani se 0800-12345 par bhi call karein.",
                "forgot_password": "Password reset ke liye app ya internet banking ka 'Forgot Password' option use karein. Agar nahi ho raha to main branch se connect karti hoon.",
                "dispute": "Transaction dispute ke liye main SmartBank ki dispute resolution team se connect kar rahi hoon.",
            },
        }

        lang = "ur" if language in (Language.ROMAN_URDU, Language.URDU_SCRIPT) else "en"
        text = messages[lang].get(reason, messages[lang]["human_request"])

        return Response(
            text=text,
            language=language,
            escalation=True,
            escalation_reason=reason,
        )

    def handle_safety_check(self, trigger_word: str) -> str:
        """Return a fraud awareness tip based on a trigger word.

        Args:
            trigger_word: Safety trigger (e.g. 'otp', 'phishing').

        Returns:
            Fraud awareness tip text in English.
        """
        trigger = trigger_word.strip().lower()
        mapping = {
            "otp": "otp",
            "phishing": "phishing",
            "vishing": "vishing",
            "sim": "sim_swap",
            "skimming": "card_skimming",
            "fraud": "otp",
            "scam": "vishing",
            "safe": "otp",
        }
        key = mapping.get(trigger, "otp")
        return SAFETY_TIPS[key].get("en", "")

    # ---- Internal helpers -------------------------------------------------

    @staticmethod
    def _resolve_language(detected: Language, hint: str) -> Language:
        """Resolve response language from detected and user hint.

        When detection is mixed/uncertain, the user's language hint wins.
        When detection is English but the hint is Urdu, trust the hint
        (the user may have typed English but prefers Urdu responses).
        """
        if detected == Language.MIXED:
            if hint:
                return Language(hint)
            return detected
        if detected == Language.ENGLISH and hint and hint.startswith("ur"):
            return Language(hint)
        return detected

    def _check_escalation(self, message: str) -> Optional[str]:
        """Check if message matches an escalation trigger.

        Returns escalation reason key or None.
        """
        msg_lower = message.lower().strip()
        for pattern, reason in _ESCALATION_PATTERNS.items():
            if re.search(pattern, msg_lower):
                return reason
        return None

    def _check_safety_trigger(self, message: str) -> Optional[str]:
        """Check if message relates to a specific safety topic.

        Returns the safety tip key or None.
        """
        msg_lower = message.lower()
        if re.search(r"otp\b", msg_lower):
            return "otp"
        if re.search(r"vish|call.*(fake|fraud)|officer.*(ban|call)", msg_lower):
            return "vishing"
        if re.search(r"phish|link|click|sms.*link|link.*sms", msg_lower):
            return "phishing"
        if re.search(r"sim|mobile.*(band|clone|dead|died|gone)", msg_lower):
            return "sim_swap"
        if re.search(r"atm.*(safe|pin|skimm)|card.*(skimm|clone)", msg_lower):
            return "card_skimming"
        return None

    def _extract_product_topic(self, message: str) -> str:
        """Map user message to a product info topic key."""
        msg_lower = message.lower()
        if re.search(r"(profit|rate|%|p\.?a\.?)", msg_lower):
            return "profit_rates"
        if re.search(r"(fee|annual|cost)", msg_lower):
            return "fees"
        if re.search(r"atms?\b", msg_lower):
            return "atm_network"
        if re.search(r"(limit|raast|ibft|pos)", msg_lower):
            return "digital_limits"
        return "account_types"

    def _extract_process_name(self, message: str) -> str:
        """Map user message to a process guide key."""
        msg_lower = message.lower()
        if re.search(r"raast\b", msg_lower):
            return "raast_id"
        if re.search(r"(paypak|domestic)", msg_lower):
            return "paypak"
        if re.search(r"(debit.*card|card.*order)", msg_lower):
            return "debit_card_ordering"
        if re.search(r"(internet|ibanking|online.*bank)", msg_lower):
            return "internet_banking"
        return "account_opening"

    def _extract_sme_topic(self, message: str) -> str:
        """Map user message to an SME info key."""
        msg_lower = message.lower()
        if re.search(r"(trade|lc|letter of|import|export)", msg_lower):
            return "trade_finance"
        if re.search(r"(cash.?flow|auto.?sweep|surplus)", msg_lower):
            return "cash_flow"
        if re.search(r"(sbp|msme|scheme|refinance)", msg_lower):
            return "sbp_msme"
        return "business_accounts"

    def _greeting(self, language: str) -> str:
        """Return a greeting message."""
        if language.startswith("ur"):
            return "Salam! Main Zara hoon — SmartBank ka aap ka apna banking guide. Main aap ki kya madad kar sakti hoon?"
        return "Hello! I'm Zara, your SmartBank banking guide. How can I help you today?"

    def _onboarding_response(self, language: Language) -> str:
        """Return the initial digital onboarding prompt."""
        if language in (Language.ROMAN_URDU, Language.URDU_SCRIPT):
            return (
                "Salam! Zara hoon. Kya aap SmartBank mein account khulwana chahte hain? "
                "Yeh bohat aasan hai. Pehle SmartBank App Play Store se download karein. "
                "Phir 'Register' dabayein. CNIC aur mobile number daalein. "
                "OTP aayega — woh daalein. PIN set karein. Bas! "
                "Kya aap ne samajh liya?"
            )
        return (
            "Hello! I'm Zara. Would you like to open a SmartBank account? "
            "It's very simple. First download the SmartBank App from Play Store. "
            "Tap 'Register'. Enter your CNIC and mobile number. "
            "Enter the OTP you receive. Set your PIN. Done! "
            "Did you understand?"
        )

    def _fallback_response(self, language: Language) -> str:
        """Return a fallback message when intent cannot be determined."""
        if language in (Language.ROMAN_URDU, Language.URDU_SCRIPT):
            return (
                "Mujhe maaf karein, main aap ki baat theek se samajh nahi paayi. "
                "Kya aap yeh bata sakte hain: aap ko kis cheez mein madad chahiye? "
                "Account kholna, debit card, RAAST ID, ya koi aur masla?"
            )
        return (
            "I'm sorry, I didn't quite understand that. "
            "Could you tell me what you need help with? "
            "Account opening, debit card, RAAST ID, or something else?"
        )


# ---------------------------------------------------------------------------
# Demo Mode
# ---------------------------------------------------------------------------

_SAMPLE_CONVERSATIONS: list[dict] = [
    {"role": "user", "text": "What types of accounts do you have?", "lang": "en", "exp_module": "product_education"},
    {"role": "user", "text": "Bachat Account par kitna profit milta hai?", "lang": "ur", "exp_module": "product_education"},
    {"role": "user", "text": "How do I open a Bachat Account?", "lang": "en", "exp_module": "process_guidance"},
    {"role": "user", "text": "RAAST ID kaise banayein?", "lang": "ur", "exp_module": "process_guidance"},
    {"role": "user", "text": "What SME financing does SBP offer?", "lang": "en", "exp_module": "sme_literacy"},
    {"role": "user", "text": "Business account ke liye kya documents chahiye?", "lang": "ur", "exp_module": "sme_literacy"},
    {"role": "user", "text": "Main ne kabhi app use nahi kiya, guide karein", "lang": "ur", "exp_module": "digital_onboarding"},
    {"role": "user", "text": "I'm not comfortable with English, can I use Urdu?", "lang": "en", "exp_module": "digital_onboarding"},
    {"role": "user", "text": "Kisi ne mujhe call karke OTP manga", "lang": "ur", "exp_module": "safety_fraud"},
    {"role": "user", "text": "I think I shared my OTP with someone", "lang": "en", "exp_module": "safety_fraud"},
    {"role": "user", "text": "Mera account block hai", "lang": "ur", "exp_module": "escalation"},
    {"role": "user", "text": "Main case karna chahta hoon", "lang": "ur", "exp_module": "escalation"},
    {"role": "user", "text": "I want to talk to a human", "lang": "en", "exp_module": "escalation"},
    {"role": "user", "text": "xyz unknown gibberish", "lang": "en", "exp_module": "unknown"},
]


def demo_mode() -> None:
    """Run a demo of the SmartBankAssistant with sample conversations."""
    assistant = SmartBankAssistant()

    print("=" * 60)
    print("  ZARA — SmartBank AI Banking Guide (Demo)")
    print("=" * 60)

    for turn in _SAMPLE_CONVERSATIONS:
        print(f"\n  User ({turn['lang']}): {turn['text']}")
        print(f"  Expected Module: {turn['exp_module']}")
        response = assistant.process_message(turn["text"], turn["lang"])
        print(f"  Zara: {response.text}")
        if response.escalation:
            print(f"  [ESCALATED: {response.escalation_reason}]")
        print("  ---")


if __name__ == "__main__":
    demo_mode()
