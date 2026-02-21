Architecture Overview (AI Governance Advisor)

Purpose: Deterministic governance classifier that outputs risk tier, required controls, approvals, and audit artifacts.

UI: Streamlit app (app.py) collects use-case description + metadata and displays governance outputs.

Policy engine: policy_rules.py implements rule-based sensitive data detection + risk classification + controls/approvals mapping.

Artifact generation: artifact_generator.py writes an audit log (CSV/JSON) and decision memo (Markdown) for traceability.

Design principle: Governance outputs are deterministic and auditable; model responses are optional.