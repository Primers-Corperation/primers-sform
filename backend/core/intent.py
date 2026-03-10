
from enum import Enum, auto

class Intent(Enum):
    EMPIRICAL_ANALYSIS = auto()
    COMPARATIVE_REASONING = auto()
    PLANNING = auto()
    EXPLANATION = auto()
    VALIDATION = auto()
    INGESTION = auto()
    KNOWLEDGE_ACQUISITION = auto()
    TEACHING = auto()
    EXECUTIVE_INSIGHTS = auto()
    APPLY_REFACTOR = auto()
    UPLOAD = auto()
    FALLBACK = auto()

class IntentRouter:
    def route(self, user_input: str) -> Intent:
        normalized = user_input.lower().strip()
        
        # Priority 0: Conversational Fillers (Always Fallback)
        if normalized.startswith("teach:"):
            return Intent.TEACHING
        if normalized.startswith("upload file:"):
            return Intent.UPLOAD

        fillers = ["hey", "hello", "hi", "how are you", "who are you", "good morning"]
        if any(normalized == f or normalized.startswith(f + " ") for f in fillers):
            return Intent.FALLBACK

        # Priority 1: Technical Commands
        if "compare" in normalized or "vs" in normalized:
            return Intent.COMPARATIVE_REASONING
        if "plan" in normalized and "refactor" in normalized:
            return Intent.PLANNING
        if "analyze" in normalized or "review" in normalized:
            return Intent.EMPIRICAL_ANALYSIS
        if "why" in normalized or "explain" in normalized:
            return Intent.EXPLANATION
        if "validate" in normalized or "check" in normalized:
            return Intent.VALIDATION
        if "ingest" in normalized:
            return Intent.INGESTION
        if "learn" in normalized or "github" in normalized:
            return Intent.KNOWLEDGE_ACQUISITION
        
        if "executive" in normalized or "report" in normalized or "cto" in normalized:
            return Intent.EXECUTIVE_INSIGHTS
            
        if "sync" in normalized and "ecosystem" in normalized:
            return Intent.KNOWLEDGE_ACQUISITION
            
        if "apply" in normalized and "refactor" in normalized:
            return Intent.APPLY_REFACTOR
            
        return Intent.FALLBACK
