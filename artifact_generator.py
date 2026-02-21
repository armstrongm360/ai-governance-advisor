import os
import csv
from datetime import datetime

AUDIT_DIR = "audit_logs"
MEMO_DIR = "decision_memos"


def _ensure_dirs():
    os.makedirs(AUDIT_DIR, exist_ok=True)
    os.makedirs(MEMO_DIR, exist_ok=True)


def write_audit_log(record: dict) -> str:
    """
    Writes/appends a simple CSV audit log.
    TODO (later): replace with JSONL + hashed IDs if you want sophistication.
    """
    _ensure_dirs()
    path = os.path.join(AUDIT_DIR, "audit_log.csv")

    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "domain": record.get("domain"),
        "automation_level": record.get("automation_level"),
        "risk_tier": record.get("risk_tier"),
        "sensitive_flags": ",".join(record.get("sensitive_flags") or []),
        "system_owner": record.get("system_owner"),
        "requester_role": record.get("requester_role"),
    }

    write_header = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    return path


def generate_decision_memo(record: dict) -> str:
    """
    Generates a simple markdown decision memo artifact.
    """
    _ensure_dirs()
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(MEMO_DIR, f"decision_memo_{ts}.md")

    memo = f"""# AI Governance Decision Memo

## Use Case Summary
**Domain:** {record.get("domain")}
**Automation Level:** {record.get("automation_level")}
**System Owner:** {record.get("system_owner")}
**Requester Role:** {record.get("requester_role")}

## Proposed Use Case
{record.get("use_case")}

## Data Inputs (as described)
{record.get("data_inputs")}

## Risk Classification
**Tier:** {record.get("risk_tier")}
**Rationale:** {record.get("rationale")}

**Sensitive Indicators:** {", ".join(record.get("sensitive_flags") or ["None detected"])}

## Required Controls
{chr(10).join([f"- {c}" for c in (record.get("controls") or [])])}

## Required Approvals
{chr(10).join([f"- {a}" for a in (record.get("approvals") or [])])}

## Decision
- [ ] Approved to proceed
- [ ] Approved with conditions
- [ ] Not approved

## Notes
(Decision notes / conditions / next steps)
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(memo)

    return path
