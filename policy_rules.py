from typing import List, Tuple

SENSITIVE_KEYWORDS = {
    "student_id": ["student id", "id number", "banner id", "emplid"],
    "grades": ["grade", "gpa", "score", "rubric"],
    "health": ["diagnosis", "disability", "iep", "504", "medical"],
    "contact": ["email address", "phone number", "home address", "mailing address","student email"],
}

def detect_sensitive_data(text: str) -> List[str]:
    """
    Basic rule-based detection.
    Students can extend this later (regex, NER, etc.).
    """
    flags = []
    t = (text or "").lower()

    for flag, keywords in SENSITIVE_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                flags.append(flag)
                break
    return flags

def classify_risk(domain, automation_level, sensitive_flags, use_case_text):

    domain = domain.strip()
    automation_level = automation_level.strip()
    text = (use_case_text or "").lower()

    tier = "LOW"
    rationale = []

    # BASELINE DOMAIN

    if domain == "Admissions":
        tier = "CRITICAL"
        rationale.append("Admissions decisions affect institutional access.")

    elif domain == "Assessment/Grading":
        tier = "HIGH"
        rationale.append("Grading affects academic progression.")

    elif domain in ["Student Support", "Advising"]:
        tier = "MEDIUM"
        rationale.append("Student support affects academic outcomes.")

    else:
        rationale.append("Lower-stakes instructional or operational use.")

    # AUTOMATION ESCALATION

    if automation_level.startswith("Decide"):

        if domain in ["Admissions"]:
            tier = "CRITICAL"
            rationale.append("Fully automated institutional decision.")

        else:
            tier = "HIGH"
            rationale.append("Automated decision authority.")

    # SENSITIVE DATA ESCALATION

    if "health" in sensitive_flags:
        tier = "CRITICAL"
        rationale.append("Health/disability data requires highest governance.")

    elif sensitive_flags and tier == "LOW":
        tier = "MEDIUM"
        rationale.append("Sensitive student data present.")

    # INSTITUTIONAL IMPACT KEYWORDS

    CRITICAL_KEYWORDS = [
        "admission decision",
        "dismissal",
        "expulsion",
        "financial aid",
        "scholarship decision",
        "degree award"
    ]

    if any(k in text for k in CRITICAL_KEYWORDS):
        tier = "CRITICAL"
        rationale.append("Institution-level decision authority detected.")

    return tier, " ".join(rationale)

def required_controls(risk_tier: str) -> List[str]:
    """
    Deterministic controls list: governance is consistent.
    """
    if risk_tier == "LOW":
        return [
            "Document purpose and scope",
            "Publish appropriate-use guidance",
            "Basic privacy review (data minimization)",
            "Human override available",
        ]

    if risk_tier == "MEDIUM":
        return [
            "Document purpose and scope",
            "Data classification + minimization checklist",
            "Vendor / model documentation recorded",
            "Bias/impact review (basic)",
            "Human-in-the-loop review for consequential outputs",
            "Logging enabled (inputs/outputs/decisions)",
        ]

    if risk_tier == "HIGH":
        return [
            "Formal DPIA / privacy impact assessment",
            "Security review + access controls",
            "Bias/impact review (formal)",
            "Human review required before actioning outputs",
            "Appeal process defined for affected users",
            "Ongoing monitoring + audit plan",
            "Logging enabled (inputs/outputs/decisions)",
        ]

    if risk_tier == "CRITICAL":
        return [
            "Formal DPIA required",
            "Executive approval required",
            "Legal review required",
            "Human oversight mandatory",
            "Full audit logging",
            "Bias testing required",
            "Formal appeals process required",
            "Continuous monitoring",
        ]

    # Fallback (in case risk_tier has an unexpected value)
    return [
        "Document purpose and scope",
        "Basic privacy review (data minimization)",
        "Human override available",
    ]

def required_approvals(risk_tier: str) -> List[str]:
    if risk_tier == "LOW":
        return ["System owner approval"]
    if risk_tier == "MEDIUM":
        return ["System owner approval", "Privacy review", "Academic leadership sign-off"]
    return ["System owner approval", "Privacy + Legal review", "Security review", "Executive sponsor sign-off"]
