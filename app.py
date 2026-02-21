import json
import hashlib
import streamlit as st

from policy_rules import (
    classify_risk,
    required_controls,
    required_approvals,
    detect_sensitive_data
)
from artifact_generator import write_audit_log, generate_decision_memo


# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="AI Governance Advisor (Prototype)", layout="wide")

st.title("AI Governance Advisor (Prototype)")
st.caption("Classifies AI use cases, recommends controls, and generates audit artifacts.")


# ----------------------------
# Session state defaults
# ----------------------------
DEFAULTS = {
    # metadata
    "mode": "Mock (free)",
    "system_owner": "Academic Affairs",
    "requester_role": "Faculty",
    "domain": "Instruction",
    "automation_level": "Assist (suggestions)",
    "automation_authority": "Assist (human decides)",
    "external_vendor": "No (local or institutional system)",

    # text inputs
    "use_case": "",
    "data_inputs": "",

    # app behavior
    "last_signature": None,
    "last_risk_tier": None,
    "history": []  # list of dicts
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ----------------------------
# Helpers
# ----------------------------
def _signature(payload: dict) -> str:
    """Stable signature so we can detect 'inputs changed' vs 'unchanged'."""
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_sample_case(case_index: int = 0):
    """Callback: load sample case safely (no 'cannot be modified' errors)."""
    try:
        with open("sample_cases.json", "r", encoding="utf-8") as f:
            cases = json.load(f)
        case = cases[case_index]
        st.session_state["use_case"] = case.get("use_case", "")
        st.session_state["data_inputs"] = case.get("data_inputs", "")
    except Exception as e:
        st.error(f"Could not load sample case: {e}")


def reset_all(clear_history: bool = False):
    """Callback: reset BOTH metadata and text inputs."""
    for k, v in DEFAULTS.items():
        if k == "history":
            continue
        st.session_state[k] = v

    # Clear comparison state so next run shows as "fresh"
    st.session_state["last_signature"] = None
    st.session_state["last_risk_tier"] = None

    if clear_history:
        st.session_state["history"] = []

    st.rerun()


def add_history(record: dict):
    st.session_state["history"].insert(0, record)
    # keep last 8 entries
    st.session_state["history"] = st.session_state["history"][:8]


# ----------------------------
# Sidebar: metadata (with keys)
# ----------------------------
with st.sidebar:
    st.header("Mode")
    st.radio(
        "Response mode",
        ["Mock (free)", "Local Model (Ollama)", "API (optional)"],
        key="mode"
    )

    st.divider()
    st.header("Use case metadata")

    st.text_input("System owner (role)", key="system_owner")

    st.selectbox(
        "Requester role",
        ["Faculty", "Staff", "Student Support", "IT", "Leadership"],
        key="requester_role"
    )

    st.selectbox(
        "Domain",
        ["Instruction", "Student Support", "Advising", "Assessment/Grading", "Admissions", "Operations"],
        key="domain"
    )

    st.selectbox(
        "Automation level",
        ["None (content generation only)", "Assist (suggestions)", "Recommend (rank/score)", "Decide (automated decisions)"],
        key="automation_level"
    )

    st.selectbox(
        "Decision authority",
        ["None (content generation only)", "Assist (human decides)", "Recommend (strong influence)", "Automated decision"],
        key="automation_authority"
    )

    st.selectbox(
        "External vendor involved",
        ["No (local or institutional system)", "Yes (OpenAI, vendor API, SaaS tool)"],
        key="external_vendor"
    )

    st.divider()
    st.button(
        "Reset ALL inputs (including metadata)",
        on_click=reset_all,
        kwargs={"clear_history": True},
        use_container_width=True
    )

# ----------------------------
# Layout
# ----------------------------
col1, col2 = st.columns([1, 1])


with col1:
    st.subheader("Describe the proposed AI use case")

    st.text_area(
        "Use case description",
        height=220,
        key="use_case"
    )

    st.subheader("Data inputs (paste examples if helpful)")
    st.text_area(
        "What data might be included?",
        height=140,
        key="data_inputs"
    )

    # Sample loader 
    st.divider()
    st.subheader("Quick sample tests")

    with open("sample_cases.json", "r", encoding="utf-8") as f:
        cases = json.load(f)

    for i in range(len(cases)):
        st.button(
            f"Load sample case #{i+1}",
            on_click=load_sample_case,
            kwargs={"case_index": i}
        )

with col2:
    st.subheader("Governance output")
    evaluate = st.button("Evaluate this case", use_container_width=True)

    # Pull current inputs directly from session_state (single source of truth)
    payload = {
        "domain": st.session_state["domain"],
        "automation_level": st.session_state["automation_level"],
        "automation_authority": st.session_state["automation_authority"],
        "external_vendor": st.session_state["external_vendor"],
        "use_case": st.session_state["use_case"],
        "data_inputs": st.session_state["data_inputs"],
    }

    sensitive_flags = detect_sensitive_data(st.session_state["data_inputs"])

    risk_tier, rationale = classify_risk(
        domain=st.session_state["domain"],
        automation_level=st.session_state["automation_level"],
        sensitive_flags=sensitive_flags,
        use_case_text=st.session_state["use_case"]
    )

    # --------
    # Change detection feedback
    # --------
    sig = _signature(payload)

    # Always define these so we never NameError
    inputs_changed = False
    tier_changed = False

    if st.session_state["last_signature"] is not None:
        inputs_changed = (sig != st.session_state["last_signature"])
        tier_changed = (risk_tier != st.session_state["last_risk_tier"])

        if inputs_changed and not tier_changed:
            st.info(
                f"Inputs changed, but the risk tier stayed **{risk_tier}**. "
                "(This is expected when the main drivers didn’t change.)"
            )

        if tier_changed:
            if risk_tier == "HIGH":
                st.warning("Risk tier changed to HIGH based on your latest inputs.")
            elif risk_tier == "MEDIUM":
                st.warning("Risk tier changed to MEDIUM based on your latest inputs.")
            else:
                st.success("Risk tier changed to LOW based on your latest inputs.")

    # Update last result (so next run compares)
    st.session_state["last_signature"] = sig
    st.session_state["last_risk_tier"] = risk_tier
    
    # Display
    st.markdown(f"### Risk Tier: **{risk_tier}**")
    st.markdown("### Why this tier?")
    if rationale.strip():
        # Turn the rationale into bullet points (simple split heuristic)
        bullets = [x.strip() for x in rationale.split(".") if x.strip()]
        for b in bullets:
            st.write(f"• {b}.")
    else:
        st.write("• No rule triggers recorded.")

    if sensitive_flags:
        st.error(f"Sensitive indicators detected: {', '.join(sorted(set(sensitive_flags)))}")

    controls = required_controls(risk_tier)
    approvals = required_approvals(risk_tier)

    st.markdown("### Required Controls")
    # non-toggleable (so they read like requirements)
    for c in controls:
        st.checkbox(c, value=True, disabled=True)

    st.markdown("### Required Approvals")
    for a in approvals:
        st.write(f"- {a}")

    st.divider()
    st.markdown("### Generate audit artifacts")
    if st.button("Generate log + decision memo"):
        record = {
            "system_owner": st.session_state["system_owner"],
            "requester_role": st.session_state["requester_role"],
            "domain": st.session_state["domain"],
            "automation_level": st.session_state["automation_level"],
            "automation_authority": st.session_state["automation_authority"],
            "external_vendor": st.session_state["external_vendor"],
            "use_case": st.session_state["use_case"],
            "data_inputs": st.session_state["data_inputs"],
            "risk_tier": risk_tier,
            "rationale": rationale,
            "sensitive_flags": sensitive_flags,
            "controls": controls,
            "approvals": approvals
        }

        log_path = write_audit_log(record)
        memo_path = generate_decision_memo(record)

        add_history({
            "tier": risk_tier,
            "domain": st.session_state["domain"],
            "automation": st.session_state["automation_level"],
            "vendor": "Yes" if "Yes" in st.session_state["external_vendor"] else "No",
            "sensitive": ",".join(sorted(set(sensitive_flags))) if sensitive_flags else "None",
        })

        st.success("Artifacts generated.")
        st.write("Log:", log_path)
        st.write("Decision memo:", memo_path)

    # Mini history 
    if st.session_state["history"]:
        st.divider()
        st.markdown("### Recent runs (for testing)")
        st.table(st.session_state["history"])

st.divider()

st.caption("Prototype note: Governance outputs are deterministic and auditable; model responses are optional.")
st.markdown("Source code: https://github.com/armstrongm360/ai-governance-advisor")
