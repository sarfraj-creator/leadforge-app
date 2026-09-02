import re
import datetime
from typing import Dict, Any, List, Optional

class IntentSignal:
    def __init__(
        self,
        signal_type: str,
        evidence: str,
        confidence: float,
        source_url: Optional[str] = None
    ):
        self.signal_type = signal_type
        self.evidence = evidence
        self.confidence = confidence
        self.source_url = source_url
        self.observed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_type": self.signal_type,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "source_url": self.source_url,
            "observed_at": self.observed_at
        }

class BuyingIntentEngine:
    """
    Evaluates observable public buying intent signals.
    Strictly separates technical audit deficiency from verified commercial purchase intent.
    If no observable signal exists, BUYING_INTENT is UNKNOWN.
    """

    @staticmethod
    def detect_intent(
        html_content: Optional[str],
        source_url: Optional[str] = None,
        job_postings: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        signals: List[IntentSignal] = []

        if not html_content:
            return {
                "buying_intent": "UNKNOWN",
                "intent_score": 0,
                "signals": [],
                "explanation": "No public buying intent signals observed on official channels."
            }

        text = html_content.lower()

        # 1. Public Hiring for Web / Frontend / Digital Roles
        hiring_patterns = [
            (r"(hiring|looking for|we are seeking)\s+(web developer|frontend developer|ui/ux designer|seo specialist|wordpress developer)", "Public Hiring for Digital / Engineering Roles", 0.85),
            (r"(new website coming soon|redesign in progress|undergoing redesign)", "Publicly Announced Redesign Initiative", 0.90),
            (r"(rfp|request for proposal|seeking agency partners)", "Active Public RFP / Quote Request", 0.95),
            (r"(expanding our digital team|careers in marketing & tech)", "Digital Team Expansion", 0.70)
        ]

        for pattern, label, conf in hiring_patterns:
            m = re.search(pattern, text)
            if m:
                matched_snippet = html_content[max(0, m.start() - 30): min(len(html_content), m.end() + 50)].strip()
                signals.append(IntentSignal(
                    signal_type=label,
                    evidence=f"Observed on page: '{matched_snippet}'",
                    confidence=conf,
                    source_url=source_url
                ))

        if signals:
            avg_score = int(sum(s.confidence * 100 for s in signals) / len(signals))
            category = "HIGH" if avg_score >= 80 else "MEDIUM"
            return {
                "buying_intent": category,
                "intent_score": avg_score,
                "signals": [s.to_dict() for s in signals],
                "explanation": f"Observed {len(signals)} factual commercial signal(s) indicating digital demand."
            }
        else:
            return {
                "buying_intent": "UNKNOWN",
                "intent_score": 0,
                "signals": [],
                "explanation": "No explicit public intent signals observed. (Default: UNKNOWN)"
            }
