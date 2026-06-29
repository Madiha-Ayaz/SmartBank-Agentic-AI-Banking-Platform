import re
import uuid
import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, Any


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class IntentResult:
    code: str
    label: str
    confidence: float


@dataclass
class Entities:
    account_number: Optional[str] = None
    cnic: Optional[str] = None
    registered_mobile: Optional[str] = None
    email: Optional[str] = None
    card_last_four: Optional[str] = None
    date_of_birth: Optional[str] = None
    statement_period: Optional[str] = None
    branch_code: Optional[str] = None


@dataclass
class AlternativeIntent:
    code: str
    label: str
    confidence: float


@dataclass
class MaestroPayload:
    alternative_intents: list[AlternativeIntent] = field(default_factory=list)
    request_summary: str = ""
    priority: str = "LOW"
    target_service: str = "human_agent"


@dataclass
class ClassificationResult:
    request_id: str
    timestamp: str
    channel: str
    raw_input: str
    detected_language: str
    intent: IntentResult
    entities: Entities
    missing_fields: list[str]
    follow_up_question: Optional[str]
    escalate_to_human: bool
    escalation_reason: Optional[str]
    maestro_payload: MaestroPayload

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Intent library — keyword / phrase patterns for local classification
# ---------------------------------------------------------------------------

INTENT_LIBRARY: list[dict[str, Any]] = [
    {
        "code": "ATM01",
        "label": "ATM Card Activation",
        "priority": "HIGH",
        "target_service": "card_management",
        "mandatory_entities": ["account_number", "cnic"],
        "patterns": [
            r"(?i)\b(atm\s*card\s*activ(at|e)|activ.*atm|enable.*atm|new.*card.*activ|card.*(ko|kardo|kar)\s*activ)"
        ],
    },
    {
        "code": "PIN02",
        "label": "PIN Generation / Reset",
        "priority": "HIGH",
        "target_service": "pin_management",
        "mandatory_entities": ["account_number", "registered_mobile"],
        "patterns": [
            r"(?i)\b(pin\s*(generat|reset|set|forgot|change|new)|forgot.*pin|reset.*pin|pin\s*(bhool|reset|change)|naya.*pin)"
        ],
    },
    {
        "code": "DEB03",
        "label": "Debit Card Block / Unblock",
        "priority": "CRITICAL",
        "target_service": "card_management",
        "mandatory_entities": ["account_number", "card_last_four"],
        "patterns": [
            r"(?i)\b((block|freeze|stop|lock|unblock|unfreeze)(\s+\w+)?\s*(card|debit)|card\s+(is\s+|has\s+been\s+|gaya\s+)?(stol|chor|block|freeze)|temporari.*freeze)"
        ],
    },
    {
        "code": "STM04",
        "label": "Bank Statement Generation",
        "priority": "MEDIUM",
        "target_service": "statement_generation",
        "mandatory_entities": ["account_number", "statement_period"],
        "patterns": [
            r"(?i)\b(statement|account.*summary|transaction.*(history|report|list)|bank.*statement|download.*statement|statement.*chahiye)"
        ],
    },
    {
        "code": "LTR05",
        "label": "Account Opening Letter",
        "priority": "MEDIUM",
        "target_service": "document_issuance",
        "mandatory_entities": ["account_number", "branch_code"],
        "patterns": [
            r"(?i)\b((account\s*)?open(ing)?\s*letter|welcome\s*letter|introduction\s*letter|bank.*letter|letter.*chahiye)"
        ],
    },
    {
        "code": "NIC06",
        "label": "Identity Card / CNIC Update",
        "priority": "HIGH",
        "target_service": "identity_update",
        "mandatory_entities": ["cnic"],
        "patterns": [
            r"(?i)\b(cnic\s*(updat|chang|renew|new|edit)|(updat|chang|renew).*(cnic|identity|id\s*card|nic)|id\s*card\s*(expir|updat)|nic(06)?\s*(updat|change|karna))"
        ],
    },
    {
        "code": "IB07",
        "label": "Internet Banking Access Recovery",
        "priority": "HIGH",
        "target_service": "internet_banking",
        "mandatory_entities": ["account_number", "registered_mobile"],
        "patterns": [
            r"(?i)\b(inter(net)?\s*bank(ing)?\s*(login|password|access|reset|lock|recover|problem)|online\s*bank(ing)?\s*(login|password|lock)|login\s*.*nahi.*ho\s*raha|password\s*(reset|change|bhool)|internet\s*banking\s*.*password)"
        ],
    },
    {
        "code": "MB08",
        "label": "Mobile Banking Activation",
        "priority": "MEDIUM",
        "target_service": "mobile_banking",
        "mandatory_entities": ["registered_mobile"],
        "patterns": [
            r"(?i)\b(mobile\s*bank(ing)?\s*(activ|register|enabl|setup)|app\s*(activ|register|login|pe\s*.*nahi\s*ho|download)|mobile.*banking.*kardo)"
        ],
    },
]


# ---------------------------------------------------------------------------
# Helpers — regex compilation
# ---------------------------------------------------------------------------

CNIC_PATTERN = re.compile(r"\b(\d{5})-(\d{7})-(\d)\b")
CNIC_MASK = re.compile(r"\b\d{5}-\d{7}-\d\b")
ACCOUNT_PATTERN = re.compile(r"\b(\d{10,16})\b")
MOBILE_PATTERN = re.compile(r"\b(03\d{2})-?(\d{7})\b")
EMAIL_PATTERN = re.compile(r"\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b")
CARD_LAST_FOUR = re.compile(r"\b(\d{4})\b")
DATE_PATTERN = re.compile(
    r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b"
)
PROFANITY_LIST: list[str] = [
    "fuck", "shit", "damn", "asshole", "bitch", "bastard", "chutiya", "bhenchod",
    "madarchod", "lauda", "land", "gaand", "saala", "kutte", "harami",
]

# Language detection — simple heuristic
URDU_MARKERS: list[str] = [
    "hai", "ho", "karo", "kardo", "chahiye", "mera", "meri", "mujhe", "apna",
    "apni", "nahi", "raha", "rahi", "gaya", "gayi", "kar", "do", "nikaal",
    "bhool", "tha", "thi", "hain", "ka", "ki", "ke", "se", "ko", "pe",
]


def _detect_language(text: str) -> str:
    tokens = re.findall(r"[a-zA-Z]+", text)
    if not tokens:
        return "en"
    lower_tokens = [t.lower() for t in tokens]
    urdu_count = sum(1 for t in lower_tokens if t in URDU_MARKERS)
    ratio = urdu_count / len(tokens)
    if ratio >= 0.35:
        return "ur"
    if ratio >= 0.15:
        return "mixed"
    return "en"


def _is_profane(text: str) -> bool:
    lower = text.lower()
    return any(p in lower for p in PROFANITY_LIST)


def _parse_entities(text: str) -> Entities:
    entities = Entities()

    cnic_match = CNIC_PATTERN.search(text)
    if cnic_match:
        entities.cnic = f"{cnic_match.group(1)}-{cnic_match.group(2)}-{cnic_match.group(3)}"

    acct_matches = ACCOUNT_PATTERN.findall(text)
    if acct_matches:
        entities.account_number = acct_matches[0]

    mobile_match = MOBILE_PATTERN.search(text)
    if mobile_match:
        entities.registered_mobile = f"{mobile_match.group(1)}-{mobile_match.group(2)}"

    email_match = EMAIL_PATTERN.search(text)
    if email_match:
        entities.email = f"{email_match.group(1)}@{email_match.group(2)}"

    card_match = CARD_LAST_FOUR.findall(text)
    if card_match:
        entities.card_last_four = card_match[0]

    date_match = DATE_PATTERN.search(text)
    if date_match:
        y, m, d = date_match.group(1), date_match.group(2).zfill(2), date_match.group(3).zfill(2)
        entities.date_of_birth = f"{y}-{m}-{d}"

    period_match = re.search(
        r"(?i)(last\s+\d+\s+(month|year)s?|\b(?:from\s+)?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\s*(?:to|till|-)\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}|(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})",
        text,
    )
    if period_match:
        entities.statement_period = period_match.group(0).strip()

    branch_match = re.search(r"\b(\d{4})\b", text)
    if branch_match:
        entities.branch_code = branch_match.group(1)

    return entities


def _mask_pii_value(value: Optional[str], field: str) -> Optional[str]:
    if value is None:
        return None
    if field == "cnic":
        m = CNIC_PATTERN.match(value)
        if m:
            return "*****-***" + m.group(2)[-4:] + "-*"
        return "*****" + value[-4:] if len(value) > 4 else "*****"
    if field == "account_number":
        return "*" * (len(value) - 4) + value[-4:] if len(value) > 4 else "****"
    if field == "registered_mobile":
        cleaned = value.replace("-", "")
        if len(cleaned) > 3:
            return "*" * (len(cleaned) - 3) + cleaned[-3:]
        return "*******"
    if field == "email":
        parts = value.split("@")
        if len(parts) == 2:
            return parts[0][0] + "***@" + parts[1]
        return value
    if field in ("card_last_four",):
        return value[-4:] if len(value) >= 4 else value
    return value


def mask_pii(entities: Entities) -> Entities:
    masked = Entities()
    for f in Entities.__dataclass_fields__:
        val = getattr(entities, f)
        setattr(masked, f, _mask_pii_value(val, f))
    return masked


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

FORMAT_RULES: dict[str, re.Pattern] = {
    "account_number": re.compile(r"^\d{10,16}$"),
    "cnic": re.compile(r"^\d{5}-\d{7}-\d$"),
    "registered_mobile": re.compile(r"^03\d{2}-?\d{7}$"),
    "card_last_four": re.compile(r"^\d{4}$"),
    "branch_code": re.compile(r"^\d{4}$"),
    "date_of_birth": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
}


def _get_missing_fields(code: str, entities: Entities) -> list[str]:
    for intent_def in INTENT_LIBRARY:
        if intent_def["code"] == code:
            missing: list[str] = []
            raw_entities = {f: getattr(entities, f) for f in Entities.__dataclass_fields__}
            for field in intent_def["mandatory_entities"]:
                val = raw_entities.get(field)
                if not val:
                    missing.append(field)
                else:
                    fmt = FORMAT_RULES.get(field)
                    if fmt and not fmt.match(val):
                        missing.append(field)
            return missing
    return []


def _follow_up_for(code: str, missing: list[str]) -> Optional[str]:
    if not missing:
        return None
    field_labels = {
        "account_number": "account number",
        "cnic": "CNIC number (format: XXXXX-XXXXXXX-X)",
        "registered_mobile": "registered mobile number (format: 03XX-XXXXXXX)",
        "email": "email address",
        "card_last_four": "last 4 digits of your card",
        "date_of_birth": "date of birth (YYYY-MM-DD)",
        "statement_period": "statement period (e.g. 'last 3 months' or 'Jan 2025')",
        "branch_code": "branch code",
    }
    labels = [field_labels.get(f, f.replace("_", " ")) for f in missing]
    if len(labels) == 1:
        return f"Please provide your {labels[0]}."
    return "Please provide the following: " + ", ".join(labels) + "."


def _score_confidence(
    code: str, pattern_matched: bool, entities: Entities, raw_input: str,
) -> float:
    if not pattern_matched:
        return 0.0
    raw = {f: getattr(entities, f) for f in Entities.__dataclass_fields__}
    # Find mandatory fields for this intent
    mandatory = []
    for intent_def in INTENT_LIBRARY:
        if intent_def["code"] == code:
            mandatory = intent_def["mandatory_entities"]
            break
    if not mandatory:
        return 0.70
    present = sum(1 for f in mandatory if raw.get(f))
    valid = sum(
        1
        for f in mandatory
        if raw.get(f)
        and (f not in FORMAT_RULES or FORMAT_RULES[f].match(str(raw[f])))
    )
    total = len(mandatory)
    if total == 0:
        return 0.70
    presence_ratio = present / total
    validity_ratio = valid / total
    base = 0.70 + (presence_ratio * 0.15) + (validity_ratio * 0.15)
    return round(min(base, 1.0), 2)


# ---------------------------------------------------------------------------
# Main classifier
# ---------------------------------------------------------------------------

class SmartBankIntentClassifier:
    """Classifies multi-lingual banking requests into one of 8 SmartBank
    intent categories using keyword/phrase matching (local / no LLM call).

    This is designed for demo / hackathon environments where an external LLM
    API may not be available.  For production, swap the local matching with a
    call to an LLM using the system prompt in ``system_prompt.md`` and the
    schema in ``schema.json``.
    """

    INTENT_LIBRARY = INTENT_LIBRARY

    def __init__(
        self,
        config: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialise the classifier.

        Args:
            config: Optional dictionary that may contain:
                - api_key (str): Not used for local classification.
                - model (str): Not used for local classification.
                - confidence_threshold (float): Escalation threshold (default 0.65).
        """
        self.config = config or {}
        self.confidence_threshold = float(self.config.get("confidence_threshold", 0.65))

    def classify(
        self,
        text: str,
        channel: str = "web",
        language_hint: Optional[str] = None,
    ) -> ClassificationResult:
        """Classify a banking request text.

        Args:
            text: Raw input from the customer (English or Roman Urdu).
            channel: Communication channel (web, mobile, ivr, whatsapp).
            language_hint: Optional language override. If None, auto-detect.

        Returns:
            A fully populated ClassificationResult dataclass.

        Raises:
            ValueError: If text is empty or None after stripping.
        """
        cleaned = text.strip() if text else ""
        if not cleaned:
            raise ValueError("Input text cannot be empty.")

        raw_input = cleaned
        request_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if channel not in ("web", "mobile", "ivr", "whatsapp"):
            channel = "web"

        # Language detection
        detected_language = language_hint or _detect_language(cleaned)

        # Profanity check
        if _is_profane(cleaned):
            return ClassificationResult(
                request_id=request_id,
                timestamp=timestamp,
                channel=channel,
                raw_input=raw_input,
                detected_language=detected_language,
                intent=IntentResult(
                    code="UNKNOWN",
                    label="Unknown Request",
                    confidence=0.0,
                ),
                entities=Entities(),
                missing_fields=[],
                follow_up_question=None,
                escalate_to_human=True,
                escalation_reason="Profanity or abusive language detected.",
                maestro_payload=MaestroPayload(
                    request_summary="Request contained profanity — escalated to human agent.",
                    priority="LOW",
                    target_service="human_agent",
                ),
            )

        # Entity extraction (raw, before masking)
        raw_entities = _parse_entities(cleaned)

        # Intent matching
        best_intent: Optional[IntentResult] = None
        alternatives: list[AlternativeIntent] = []
        matched_any = False

        for intent_def in self.INTENT_LIBRARY:
            score = 0.0
            matched = False
            for pattern in intent_def["patterns"]:
                if re.search(pattern, cleaned):
                    matched = True
                    matched_any = True
                    break
            if matched:
                score = _score_confidence(
                    intent_def["code"],
                    pattern_matched=True,
                    entities=raw_entities,
                    raw_input=cleaned,
                )
            if score > 0.0:
                alt = AlternativeIntent(
                    code=intent_def["code"],
                    label=intent_def["label"],
                    confidence=score,
                )
                if best_intent is None or score > best_intent.confidence:
                    if best_intent is not None:
                        alternatives.append(
                            AlternativeIntent(best_intent.code, best_intent.label, best_intent.confidence)
                        )
                    best_intent = IntentResult(
                        code=intent_def["code"],
                        label=intent_def["label"],
                        confidence=score,
                    )
                else:
                    alternatives.append(alt)

        # No intent matched
        if best_intent is None:
            return ClassificationResult(
                request_id=request_id,
                timestamp=timestamp,
                channel=channel,
                raw_input=raw_input,
                detected_language=detected_language,
                intent=IntentResult(
                    code="UNKNOWN",
                    label="Unknown Request",
                    confidence=0.0,
                ),
                entities=mask_pii(raw_entities),
                missing_fields=[],
                follow_up_question=None,
                escalate_to_human=True,
                escalation_reason="Could not determine intent from input.",
                maestro_payload=MaestroPayload(
                    request_summary="Unrecognized request — escalated to human agent.",
                    priority="LOW",
                    target_service="human_agent",
                ),
            )

        # Sort alternatives descending
        alternatives.sort(key=lambda a: a.confidence, reverse=True)

        # Tie-breaker check: best vs second-best difference < 0.05
        tie_break = False
        if len(alternatives) > 0:
            diff = best_intent.confidence - alternatives[0].confidence
            if 0.0 <= diff < 0.05:
                tie_break = True

        # Missing fields
        missing = _get_missing_fields(best_intent.code, raw_entities)

        # DEB03 escalation check
        deb_escalation = False
        if best_intent.code == "DEB03" and not raw_entities.card_last_four:
            deb_escalation = True

        # Missing fields for DEB03
        deb_missing_card = best_intent.code == "DEB03" and "card_last_four" not in missing

        # Escalation logic
        escalate = False
        escalation_reason: Optional[str] = None
        if best_intent.confidence < self.confidence_threshold:
            escalate = True
            escalation_reason = (
                f"Low confidence ({best_intent.confidence:.2f}) below threshold "
                f"({self.confidence_threshold:.2f})."
            )
        elif tie_break:
            escalate = True
            escalation_reason = (
                "Ambiguous — multiple intents with similar confidence "
                f"(best: {best_intent.code} [{best_intent.confidence:.2f}], "
                f"next: {alternatives[0].code} [{alternatives[0].confidence:.2f}])."
            )
        elif deb_escalation:
            escalate = True
            escalation_reason = (
                "CRITICAL intent DEB03 requires card_last_four for verification, "
                "but it was not provided."
            )

        # Get priority and target service
        priority = "LOW"
        target_service = "human_agent"
        for intent_def in self.INTENT_LIBRARY:
            if intent_def["code"] == best_intent.code:
                priority = intent_def["priority"]
                target_service = intent_def["target_service"]
                break

        # Summary
        summary = (
            f"Customer requested {best_intent.label.lower()}"
            if not escalate
            else f"[ESCALATED] {escalation_reason} Original intent: {best_intent.label}"
        )

        # PII masking
        masked_entities = mask_pii(raw_entities)

        # Follow-up question
        follow_up = _follow_up_for(best_intent.code, missing)

        # Filter alternatives to those > 0.3 confidence (exclude primary)
        filtered_alternatives = [a for a in alternatives if a.code != best_intent.code and a.confidence > 0.30]

        return ClassificationResult(
            request_id=request_id,
            timestamp=timestamp,
            channel=channel,
            raw_input=raw_input,
            detected_language=detected_language,
            intent=best_intent,
            entities=masked_entities,
            missing_fields=missing,
            follow_up_question=follow_up,
            escalate_to_human=escalate,
            escalation_reason=escalation_reason,
            maestro_payload=MaestroPayload(
                alternative_intents=filtered_alternatives,
                request_summary=summary,
                priority=priority,
                target_service=target_service,
            ),
        )

    def validate_entities(
        self,
        intent_code: str,
        entities: Entities,
    ) -> list[str]:
        """Validate that all mandatory entities for the given intent are
        present and correctly formatted.

        Args:
            intent_code: One of ATM01, PIN02, DEB03, STM04, LTR05,
                         NIC06, IB07, MB08.
            entities: Extracted entities (raw, before masking).

        Returns:
            List of missing or invalid field names.
        """
        return _get_missing_fields(intent_code, entities)

    def mask_pii(self, entities: Entities) -> Entities:
        """Mask sensitive PII fields in an Entities object.

        Args:
            entities: The extracted entities object.

        Returns:
            A new Entities object with masked values.
        """
        return mask_pii(entities)

    def get_intent_definitions(self) -> list[dict[str, Any]]:
        """Return the full intent library for introspection / debugging."""
        return self.INTENT_LIBRARY
