import json
import os
from datetime import datetime

AUDIT_LOG = "data/audit_log.jsonl"

def log_event(action, matter, detail=None):
    """Append a structured event to the audit log (JSON Lines)."""
    os.makedirs("data", exist_ok=True)
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "matter": matter,
        "detail": detail or {}
    }
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    return event

def read_log():
    """Return all logged events."""
    if not os.path.exists(AUDIT_LOG):
        return []
    events = []
    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events