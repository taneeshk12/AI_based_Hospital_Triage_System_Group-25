"""
Symptom Agent (Clinical Context Agent)
=======================================
Extracts clinically meaningful context from structured vital signs and
lab values — without using clinical notes for prediction.

Design Rationale:
    Clinical notes in this dataset contain heavy template-based label leakage
    and are therefore NOT used for risk scoring. However, they can be accepted
    as an optional parameter and returned as display context only.

    All symptom detection is rule-based, derived from established clinical
    thresholds (e.g., SIRS criteria, qSOFA, NEWS2 equivalents).

Outputs:
    - detected_symptoms       : Named clinical findings (e.g., "Fever", "Hypoxia")
    - clinical_presentations  : Possible clinical syndromes (e.g., "Possible septic shock")
    - clinical_summary        : One-paragraph plain-English summary for clinicians
    - clinical_notes_display  : Raw notes (if provided) — for display only, never scored
"""

from typing import Any


class SymptomAgent:
    """
    Extracts clinical context from structured patient data.

    All logic is rule-based and derived from standard clinical thresholds.
    Clinical notes, if provided, are stored for display but never used
    to compute risk scores or influence model predictions.
    """

    # ------------------------------------------------------------------ #
    # Clinical Thresholds                                                  #
    # ------------------------------------------------------------------ #
    THRESHOLDS = {
        # Vitals
        "fever":          lambda d: d.get("temperature", 37) > 38.3,
        "hypothermia":    lambda d: d.get("temperature", 37) < 36.0,
        "tachycardia":    lambda d: d.get("heart_rate", 80) > 100,
        "bradycardia":    lambda d: d.get("heart_rate", 80) < 50,
        "hypoxia":        lambda d: d.get("spo2", 97) < 92,
        "severe_hypoxia": lambda d: d.get("spo2", 97) < 88,
        "tachypnea":      lambda d: d.get("respiratory_rate", 16) > 20,
        "bradypnea":      lambda d: d.get("respiratory_rate", 16) < 10,
        "hypotension":    lambda d: d.get("systolic_bp", 120) < 90,
        "hypertension":   lambda d: d.get("systolic_bp", 120) > 160,
        "altered_mentation": lambda d: d.get("altered_mentation", 0) == 1,
        "chest_pain":     lambda d: d.get("chest_pain", 0) == 1,
        "diabetes":       lambda d: d.get("diabetes", 0) == 1,
        # Labs
        "leukocytosis":   lambda d: d.get("wbc", 8) > 12,
        "leukopenia":     lambda d: d.get("wbc", 8) < 4,
        "anemia":         lambda d: d.get("hemoglobin", 14) < 10,
        "thrombocytopenia": lambda d: d.get("platelet_count", 250) < 100,
        "hyperglycemia":  lambda d: d.get("glucose", 100) > 200,
        "elevated_lactate": lambda d: d.get("lactate", 1.2) > 2.0,
        "severe_lactate": lambda d: d.get("lactate", 1.2) > 4.0,
        "elevated_troponin": lambda d: d.get("troponin", 0.01) > 0.04,
        "elevated_creatinine": lambda d: d.get("creatinine", 0.9) > 1.5,
        "elevated_bnp":   lambda d: d.get("bnp", 50) > 100,
        "coagulopathy":   lambda d: d.get("inr", 1.0) > 1.5,
        "hyponatremia":   lambda d: d.get("sodium", 140) < 135,
        "hyperkalemia":   lambda d: d.get("potassium", 4.0) > 5.5,
        # High pain
        "severe_pain":    lambda d: d.get("pain_score", 0) >= 7,
        "moderate_pain":  lambda d: 4 <= d.get("pain_score", 0) <= 6,
    }

    # Human-readable labels for detected findings
    SYMPTOM_LABELS = {
        "fever":             "Fever",
        "hypothermia":       "Hypothermia",
        "tachycardia":       "Tachycardia",
        "bradycardia":       "Bradycardia",
        "hypoxia":           "Hypoxia",
        "severe_hypoxia":    "Severe Hypoxia",
        "tachypnea":         "Tachypnea",
        "bradypnea":         "Bradypnea",
        "hypotension":       "Hypotension",
        "hypertension":      "Hypertension",
        "altered_mentation": "Altered Mental Status",
        "chest_pain":        "Chest Pain",
        "diabetes":          "Diabetes (History)",
        "leukocytosis":      "Leukocytosis (Elevated WBC)",
        "leukopenia":        "Leukopenia (Low WBC)",
        "anemia":            "Anaemia",
        "thrombocytopenia":  "Thrombocytopenia",
        "hyperglycemia":     "Hyperglycaemia",
        "elevated_lactate":  "Elevated Lactate",
        "severe_lactate":    "Severe Hyperlactataemia",
        "elevated_troponin": "Elevated Troponin",
        "elevated_creatinine": "Elevated Creatinine",
        "elevated_bnp":      "Elevated BNP (Heart Failure Marker)",
        "coagulopathy":      "Coagulopathy (Elevated INR)",
        "hyponatremia":      "Hyponatraemia",
        "hyperkalemia":      "Hyperkalaemia",
        "severe_pain":       "Severe Pain",
        "moderate_pain":     "Moderate Pain",
    }

    # Clinical presentation rules: (condition_set, presentation_text)
    # If ANY condition in the set is True → add presentation
    PRESENTATION_RULES: list[tuple[set[str], str]] = [
        (
            {"fever", "leukocytosis", "tachycardia"},
            "Possible systemic inflammatory response (SIRS criteria met).",
        ),
        (
            {"fever", "altered_mentation"},
            "Possible neurological or infectious presentation (e.g., meningitis, encephalitis, or septic encephalopathy).",
        ),
        (
            {"hypoxia", "tachypnea"},
            "Possible cardiopulmonary presentation (e.g., PE, pneumothorax, heart failure).",
        ),
        (
            {"hypotension", "tachycardia", "elevated_lactate"},
            "Possible septic shock presentation.",
        ),
        (
            {"severe_lactate", "hypotension"},
            "Possible sepsis with hemodynamic compromise.",
        ),
        (
            {"elevated_troponin", "chest_pain"},
            "Possible acute coronary syndrome (ACS).",
        ),
        (
            {"elevated_bnp", "tachypnea"},
            "Possible acute decompensated heart failure.",
        ),
        (
            {"elevated_creatinine", "hyperkalemia"},
            "Possible acute kidney injury (AKI).",
        ),
        (
            {"coagulopathy", "elevated_lactate"},
            "Possible disseminated intravascular coagulation (DIC) risk.",
        ),
        (
            {"severe_hypoxia"},
            "Severe hypoxaemia — immediate respiratory support may be required.",
        ),
        (
            {"altered_mentation", "hypotension"},
            "Possible haemodynamic compromise with neurological involvement.",
        ),
    ]

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def analyze(self, patient_data: dict[str, Any]) -> dict[str, Any]:
        """
        Extract clinical context from structured patient data.

        Args:
            patient_data: Raw patient dict (vitals + labs + demographics).
                         An optional ``clinical_notes`` key is accepted for
                         display only — it is never used for risk scoring.

        Returns:
            Dict with:
                detected_symptoms       : list[str]
                symptom_count           : int
                active_flags            : list[str]  (internal flag names)
                clinical_presentations  : list[str]
                clinical_summary        : str
                clinical_notes_display  : str | None
        """
        active_flags = self._detect_flags(patient_data)
        detected_symptoms = [self.SYMPTOM_LABELS[f] for f in active_flags]
        presentations = self._build_presentations(active_flags)
        summary = self._build_summary(patient_data, detected_symptoms, presentations)
        notes_display = patient_data.get("clinical_notes", None)

        return {
            "detected_symptoms": detected_symptoms,
            "symptom_count": len(detected_symptoms),
            "active_flags": active_flags,
            "clinical_presentations": presentations,
            "clinical_summary": summary,
            "clinical_notes_display": notes_display,
        }

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _detect_flags(self, data: dict[str, Any]) -> list[str]:
        """Return list of active clinical flag keys."""
        return [key for key, fn in self.THRESHOLDS.items() if fn(data)]

    def _build_presentations(self, active_flags: list[str]) -> list[str]:
        """Match active flags against syndrome rules."""
        flag_set = set(active_flags)
        presentations: list[str] = []
        for required_flags, text in self.PRESENTATION_RULES:
            if required_flags & flag_set:  # Any overlap triggers
                if text not in presentations:
                    presentations.append(text)
        return presentations

    def _build_summary(
        self,
        data: dict[str, Any],
        symptoms: list[str],
        presentations: list[str],
    ) -> str:
        """Generate a concise clinical summary paragraph."""
        age = data.get("age", "Unknown")
        sex_raw = data.get("sex", "U")
        sex = "Male" if str(sex_raw).upper() in ("M", "MALE") else "Female" if str(sex_raw).upper() in ("F", "FEMALE") else "Unknown"
        spo2 = data.get("spo2", "?")
        hr = data.get("heart_rate", "?")
        sbp = data.get("systolic_bp", "?")
        rr = data.get("respiratory_rate", "?")

        intro = f"{age}-year-old {sex} patient presenting with vital signs: SpO₂ {spo2}%, HR {hr} bpm, BP {sbp} mmHg, RR {rr}/min."

        if symptoms:
            sym_str = ", ".join(symptoms[:5])
            extra = f" +{len(symptoms) - 5} more" if len(symptoms) > 5 else ""
            intro += f" Key clinical findings: {sym_str}{extra}."

        if presentations:
            pres_str = " ".join(presentations[:2])
            intro += f" {pres_str}"

        if not symptoms and not presentations:
            intro += " No significant clinical flags detected at current threshold levels."

        return intro
