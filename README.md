# AI Governance Advisor

## Institutional AI Risk Classification and Governance Control Prototype

---

## Overview

The AI Governance Advisor is a Streamlit-based prototype demonstrating how institutions can operationalize artificial intelligence governance through structured risk classification, audit logging, and formal decision documentation.

This system translates institutional governance principles into executable workflows, enabling consistent and accountable oversight of AI use cases in academic and administrative contexts.

---

## Live Demonstration

A live deployment of the AI Governance Advisor is available here:

https://aigovernanceadvisor-xlyzcym7mrc2c9ukutn79t.streamlit.app/

This interactive prototype allows users to:

- classify AI use cases by institutional risk level  
- view required governance controls  
- generate audit logs  
- generate formal governance decision memos  

This deployment demonstrates how institutional AI governance can be operationalized as a working system.

---

## Institutional Problem

Artificial intelligence is rapidly being deployed across institutional functions, including:

* grading and feedback
* admissions screening
* academic advising
* student support automation

However, most institutions lack operational governance systems capable of:

* classifying risk consistently
* enforcing governance controls
* documenting approval decisions
* maintaining audit trails

Governance often exists only as policy—not implementation.

This prototype demonstrates how governance can be implemented as a working system.

---

## System Functions

The application performs four governance functions:

### 1. Risk Classification

Classifies AI use cases into institutional risk tiers based on:

* sensitive data exposure
* automation authority level
* decision impact domain

Risk tiers:

* LOW
* MEDIUM
* HIGH
* CRITICAL

---

### 2. Governance Control Assignment

Automatically generates required institutional governance controls, including:

* human review requirements
* documentation requirements
* approval workflows
* audit requirements

---

### 3. Audit Log Generation

Creates persistent governance audit records documenting:

* classification decisions
* justification
* timestamps

---

### 4. Decision Memo Generation

Produces formal governance decision memoranda suitable for institutional documentation.

---

## Architecture

Governance pipeline:

User Input
↓
Risk Classification Engine
↓
Governance Control Engine
↓
Audit Log Generator
↓
Decision Memo Generator

See:

docs/

---

## Technology

Python
Streamlit
JSON rule engine
Markdown artifact generation

---

## Example Outputs

See:

audit_logs/

decision_memos/

---

## Run locally

Install requirements:

```
pip install -r requirements.txt
```

Run:

```
streamlit run app.py
```

---

## Author

Mathew Armstrong
MS Data Science

AI Governance and Digital Learning Systems Portfolio

---

## Portfolio Purpose

This prototype demonstrates the practical implementation of institutional artificial intelligence governance architecture.

It forms part of a broader director-level portfolio focused on AI governance, institutional risk management, and digital learning systems design.

