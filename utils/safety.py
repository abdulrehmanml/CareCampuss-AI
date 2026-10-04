"""Deterministic emergency screen. Runs BEFORE any AI call and cannot be overridden by it."""

EMERGENCY_LINE = "1122"  # Rescue 1122, Pakistan

EMERGENCY_TERMS = [
    "chest pain", "heart attack", "can't breathe", "cannot breathe", "difficulty breathing",
    "shortness of breath", "unconscious", "fainted", "seizure", "convulsion", "stroke",
    "face drooping", "slurred speech", "severe bleeding", "heavy bleeding", "vomiting blood",
    "coughing blood", "poison", "overdose", "suicide", "kill myself", "snake bite",
    "severe burn", "head injury", "not breathing", "labour pain", "labor pain",
    # Roman Urdu
    "seene mein dard", "seene me dard", "saans nahi", "saans lene mein", "behosh",
    "khoon bahut", "dora", "zeher", "khudkushi",
    # Urdu script
    "سینے میں درد", "سانس", "بے ہوش", "دورہ", "زہر", "شدید خون",
]


def is_emergency(text: str) -> bool:
    t = text.lower()
    return any(term in t for term in EMERGENCY_TERMS)
