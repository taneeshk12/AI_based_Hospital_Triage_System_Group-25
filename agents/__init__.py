"""
HCAI Agents Package
-------------------
Human-Centered AI agent modules for the OmniHealth Clinical Decision Support System.

ML Triage Agents:
    - CardiacAgent:         XGBoost cardiac risk classification
    - SepsisAgent:          XGBoost sepsis probability scoring
    - RespiratoryAgent:     Random Forest ensemble respiratory distress detection
    - GeneralHealthAgent:   XGBoost undifferentiated triage risk

HCAI Support Agents:
    - ConfidenceAgent:  Analyzes model certainty and determines human review requirements
    - SymptomAgent:     Extracts clinical context from structured vital signs and labs
    - LLMAgent:         Generates clinician-friendly interpretations via Groq (non-diagnostic)
    - SummaryAgent:     Orchestrates all agents and produces the final HCAI context payload
"""

from .confidence_agent import ConfidenceAgent
from .symptom_agent import SymptomAgent
from .llm_agent import LLMAgent
from .summary_agent import SummaryAgent
from .cardiac_agent_api import CardiacAgent
from .sepsis_agent_api import SepsisAgent
from .respiratory_agent_api import RespiratoryAgent
from .general_agent_api_xgboost import GeneralHealthAgent

__all__ = [
    "ConfidenceAgent", "SymptomAgent", "LLMAgent", "SummaryAgent",
    "CardiacAgent", "SepsisAgent", "RespiratoryAgent", "GeneralHealthAgent",
]
