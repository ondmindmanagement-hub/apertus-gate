# Technical Report — Apertus Gate

## Track
2B · Apertus Adoption: Own Project

## Problem
Agentic systems increasingly cross the boundary between generating text and taking actions. The difficult question is not only whether an LLM can produce an answer, but whether a proposed action is safe and appropriate to automate.

## Prototype
Apertus Gate inserts a review step before execution. It sends a proposed action and contextual constraints to Apertus 1.5 and requests a strict JSON assessment: risk level, decision, reasons, missing information, and a safe next step. The prototype never performs the action itself.

## Apertus usage
Apertus 1.5 is the semantic risk reasoner. It considers reversibility, external side effects, financial/legal/security impact, data sensitivity and whether human approval is needed.

A deterministic demo policy exists only so the UI remains inspectable without credentials. It is explicitly labelled and is not counted as Apertus inference.

## Technical rigour
Output is normalized against a fixed schema. Unknown risk labels fail to high; unknown decisions fail to human_review. Inputs are bounded. Credentials remain server-side. Unit tests cover JSON extraction, normalization and safe fallback behavior.

## Sovereign deployability
The inference interface is provider-neutral and OpenAI-compatible. It can target a Swiss-hosted Apertus service, Public AI, or a self-hosted Apertus instance without changing the browser application.

## Value, cost and scalability
The gate adds one small inference call only at decision boundaries rather than every internal step. A production implementation can use policy rules to bypass obvious low-risk actions and reserve Apertus evaluation for ambiguous or high-impact transitions.

## Limitations
This is a hackathon prototype, not a formal compliance engine. LLM judgments can be wrong. Production use requires organization-specific policy, calibrated evaluations, stronger authentication, persistent audit storage and human-review workflows.

## Next steps
1. Add a reproducible benchmark of labelled action scenarios.
2. Compare 8B and 70B decision consistency.
3. Add signed decision records and tamper-evident audit logs.
4. Integrate a real approval queue.
