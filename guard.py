import re

# Patterns that suggest a prompt-injection attempt in a document.
# Keep this list small and explainable for the demo.
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"forget\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"you\s+are\s+now\s+",
    r"new\s+instructions?\s*:",
    r"system\s*prompt",
    r"reveal\s+(all\s+)?(client|matter|document|file)",
    r"list\s+(all\s+)?(client|matter|document|file)",
    r"print\s+(all\s+)?(client|matter|document|file)",
    r"output\s+(all\s+)?(client|matter|document|file)",
]

def detect_injection(text):
    """
    Return a list of matched injection patterns found in `text`.
    Empty list means clean.
    """
    if not text:
        return []
    matches = []
    for pattern in INJECTION_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            matches.append({"pattern": pattern, "match": m.group(0)})
    return matches


def redact_pii(text):
    """
    Redact South African ID numbers and common phone/account patterns in output text.
    Returns (redacted_text, count_of_redactions).
    """
    if not text:
        return text, 0

    redactions = 0
    result = text

    # SA ID number: 13 digits, often written with spaces
    sa_id_pattern = r"\b\d{2}\s?\d{2}\s?\d{2}\s?\d{7}\s?\d{2}\b"

    def _redact_id(m):
        nonlocal redactions
        redactions += 1
        return "[REDACTED ID]"

    result = re.sub(sa_id_pattern, _redact_id, result)

    # SA phone numbers: +27... or 0XX...
    phone_pattern = r"(\+27\s?\d{2}\s?\d{3}\s?\d{4}|0\d{2}\s?\d{3}\s?\d{4})"

    def _redact_phone(m):
        nonlocal redactions
        redactions += 1
        return "[REDACTED PHONE]"

    result = re.sub(phone_pattern, _redact_phone, result)

    return result, redactions