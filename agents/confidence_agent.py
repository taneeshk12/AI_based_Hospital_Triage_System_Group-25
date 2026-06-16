"""
Confidence Agent
================
Analyzes the model's prediction certainty and determines the appropriate
level of human oversight required.

This is a core Human-Centered AI component: instead of blindly trusting
the model, the system uses confidence thresholds to flag uncertain predictions
for mandatory clinician review. This prevents over-reliance on AI.

Design Principle:
    - HIGH confidence (≥85%)  → ADVISORY review (informational, clinician decides)
    - MEDIUM confidence (70-85%) → ADVISORY with a caution note
    - LOW confidence (<70%)   → MANDATORY review (must be seen by a clinician)
    - HIGH_RISK prediction    → Always at minimum ADVISORY/IMMEDIATE
"""

from typing import Any


class ConfidenceAgent:
    """
    Analyzes a model prediction's confidence score and emits a
    human-oversight recommendation.

    Works with the output dict from any of the four sub-agents:
    RespiratoryAgent, CardiacAgent, SepsisAgent, GeneralHealthAgent.

    Attributes:
        HIGH_CONFIDENCE_THRESHOLD   (float): ≥ this → HIGH_CONFIDENCE
        MEDIUM_CONFIDENCE_THRESHOLD (float): ≥ this → MEDIUM_CONFIDENCE
    """

    HIGH_CONFIDENCE_THRESHOLD: float = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.70

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def analyze(self, prediction: dict[str, Any]) -> dict[str, Any]:
        """
        Analyse confidence from a sub-agent prediction dict and return an
        enriched dict with human-oversight fields.

        Args:
            prediction: Output dict from any of the four model sub-agents.
                        Must contain at least a ``confidence`` (float 0-1)
                        and ``risk_level`` (str) key.

        Returns:
            Dict with the following added/overwritten keys:
                confidence_category   : "HIGH_CONFIDENCE" | "MEDIUM_CONFIDENCE" | "LOW_CONFIDENCE"
                human_review_status   : "ADVISORY" | "MANDATORY"
                review_urgency        : "IMMEDIATE" | "WITHIN_4H" | "ROUTINE"
                review_message        : human-readable string for clinicians
                action_required       : bool — True when MANDATORY or HIGH risk
        """
        confidence: float = float(prediction.get("confidence", 0.5))
        risk_level: str = prediction.get("risk_level", "UNKNOWN") or "UNKNOWN"

        confidence_category = self._categorize_confidence(confidence)
        human_review_status = self._determine_review_status(confidence_category, risk_level)
        review_urgency = self._determine_urgency(human_review_status, risk_level)
        review_message = self._build_review_message(
            confidence, confidence_category, human_review_status, risk_level
        )
        action_required = human_review_status == "MANDATORY" or "HIGH" in risk_level.upper()

        return {
            **prediction,
            "confidence_category": confidence_category,
            "human_review_status": human_review_status,
            "review_urgency": review_urgency,
            "review_message": review_message,
            "action_required": action_required,
        }

    def summarize(self, all_predictions: dict[str, dict]) -> dict[str, Any]:
        """
        Produce an aggregate confidence summary across all four sub-agents.

        Args:
            all_predictions: Dict of agent_name → prediction dict (already
                             processed by .analyze()).

        Returns:
            Dict with overall confidence stats and the most urgent review status.
        """
        scores = [
            float(p.get("confidence", 0.5))
            for p in all_predictions.values()
            if p.get("status") == "success"
        ]
        categories = [
            p.get("confidence_category", "LOW_CONFIDENCE")
            for p in all_predictions.values()
            if p.get("status") == "success"
        ]
        statuses = [
            p.get("human_review_status", "ADVISORY")
            for p in all_predictions.values()
            if p.get("status") == "success"
        ]

        avg_confidence = sum(scores) / len(scores) if scores else 0.5
        overall_category = self._categorize_confidence(avg_confidence)
        overall_status = "MANDATORY" if "MANDATORY" in statuses else "ADVISORY"

        return {
            "avg_confidence": round(avg_confidence, 4),
            "avg_confidence_pct": f"{avg_confidence * 100:.1f}%",
            "overall_confidence_category": overall_category,
            "overall_human_review_status": overall_status,
            "per_agent_categories": categories,
        }

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _categorize_confidence(self, confidence: float) -> str:
        if confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            return "HIGH_CONFIDENCE"
        if confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            return "MEDIUM_CONFIDENCE"
        return "LOW_CONFIDENCE"

    def _determine_review_status(self, category: str, risk_level: str) -> str:
        """LOW confidence always triggers MANDATORY human review."""
        if category == "LOW_CONFIDENCE":
            return "MANDATORY"
        if "HIGH" in risk_level.upper() and category != "HIGH_CONFIDENCE":
            return "MANDATORY"
        return "ADVISORY"

    def _determine_urgency(self, review_status: str, risk_level: str) -> str:
        risk_up = risk_level.upper()
        if "HIGH" in risk_up:
            return "IMMEDIATE"
        if review_status == "MANDATORY":
            return "WITHIN_4H"
        return "ROUTINE"

    def _build_review_message(
        self,
        confidence: float,
        category: str,
        status: str,
        risk_level: str,
    ) -> str:
        pct = f"{confidence * 100:.1f}%"
        risk_clean = risk_level.replace("_", " ").title()

        if status == "MANDATORY" and category == "LOW_CONFIDENCE":
            return (
                f"⚠️  LOW CONFIDENCE ({pct}) — Model certainty is insufficient. "
                f"Mandatory clinician review required before acting on this prediction."
            )
        if "HIGH" in risk_level.upper():
            return (
                f"⚠️  {risk_clean} — Model confidence is {category.replace('_', ' ').lower()} ({pct}). "
                f"Immediate physician review recommended."
            )
        if category == "MEDIUM_CONFIDENCE":
            return (
                f"ℹ️  {risk_clean} — Moderate model confidence ({pct}). "
                f"Review the SHAP feature drivers before finalising clinical action."
            )
        return (
            f"✅  {risk_clean} — High model confidence ({pct}). "
            f"Prediction is reliable; clinician review is advisory."
        )
