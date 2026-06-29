from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    AUTO_APPROVE = "auto-approve"
    HUMAN_REVIEW = "human-review"
    AUTO_REJECT = "auto-reject"


DECISION_THRESHOLDS: dict[str, int] = {
    "human_review_lower": 30,
    "human_review_upper": 60,
}


def get_decision(risk_score: float) -> RiskLevel:
    if risk_score > 60:
        return RiskLevel.AUTO_REJECT
    if risk_score >= 30:
        return RiskLevel.HUMAN_REVIEW
    return RiskLevel.AUTO_APPROVE


FRAUD_WEIGHTS: dict[str, int] = {
    "exif_date_mismatch": 25,
    "font_inconsistency": 20,
    "mrz_checksum_failure": 30,
    "known_fraud_template_match": 35,
    "face_match_failure": 25,
    "document_number_suspicious": 15,
}


@dataclass
class FraudScoringResult:
    raw_score: float = 0.0
    capped_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.AUTO_APPROVE
    triggered_indicators: list[str] = field(default_factory=list)
    indicator_scores: dict[str, int] = field(default_factory=dict)


class FraudScorer:
    def __init__(self, weights: Optional[dict[str, int]] = None):
        self.weights = weights or dict(FRAUD_WEIGHTS)

    def assess_risk(self, detection_results: dict[str, bool]) -> float:
        if not detection_results:
            return 0.0

        total_weight = sum(self.weights.get(k, 0) for k in detection_results)
        triggered_weight = sum(
            self.weights.get(k, 0)
            for k, v in detection_results.items()
            if v
        )

        raw_score = triggered_weight
        capped_score = min(raw_score, 100.0)
        return capped_score

    def assess_risk_detailed(
        self, detection_results: dict[str, bool]
    ) -> FraudScoringResult:
        if not detection_results:
            return FraudScoringResult()

        triggered: list[str] = []
        indicator_scores: dict[str, int] = {}

        for indicator, triggered_flag in detection_results.items():
            weight = self.weights.get(indicator, 0)
            indicator_scores[indicator] = weight if triggered_flag else 0
            if triggered_flag:
                triggered.append(indicator)

        raw_score = sum(indicator_scores.values())
        capped_score = min(raw_score, 100.0)
        risk_level = get_decision(capped_score)

        return FraudScoringResult(
            raw_score=raw_score,
            capped_score=capped_score,
            risk_level=risk_level,
            triggered_indicators=triggered,
            indicator_scores=indicator_scores,
        )


__all__ = [
    "RiskLevel",
    "FraudScorer",
    "FraudScoringResult",
    "get_decision",
    "DECISION_THRESHOLDS",
    "FRAUD_WEIGHTS",
]
