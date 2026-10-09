# Apertus Gate

Hack Apertus 2026 · Track 2B — Apertus Adoption: Own Project

Apertus Gate is a small, auditable review layer for AI actions. Before an agent performs an external action, the action and its context are sent to Apertus 1.5. The model returns a structured risk decision: allow, human_review, or required_block.

## Why

AI systems are useful when they can act, but high-impact actions should not be hidden behind a generic chat response. Apertus Gate makes the decision boundary explicit and inspectable.

## What it demonstrates

- Purposeful use of Apertus 1.5 for structured risk reasoning.
- Human-in-the-loop control for irreversible or sensitive actions.
- JSON output designed for logging and downstream policy enforcement.
- Provider portability through an OpenAI-compatible HTTP interface.
- Sovereign deployability: target a Swiss-hosted Apertus endpoint or self-hosted instance.
- Safe demo mode when no API key is available; demo mode is clearly labelled.

## Run

Python 3 only; no third-party application dependencies.

    make test
    python3 track_2b/src/server.py
    open http://127.0.0.1:8787

## Real Apertus inference

    export APERTUS_API_KEY="..."
    export APERTUS_API_URL="https://api.publicai.co/v1/chat/completions"
    export APERTUS_MODEL="swiss-ai/apertus-v1.5-8b"
    python3 server.py

The key is read only from the environment and is never written to the repository.

## Tests

    make test

## Architecture

Browser UI → local Python review service → Apertus 1.5 endpoint → strict JSON normalization → human-visible decision.

The application does not execute the proposed action. It only produces the decision artifact that another workflow could enforce.

## Security notes

- No API key in browser JavaScript.
- No key committed to Git.
- Inputs are bounded before inference.
- Invalid or unstructured model decisions fail toward human review.
- The project does not claim formal legal, medical, financial, or security certification.

## Hackathon clean-room statement

This repository was created during the Hack Apertus online event as a new open-source prototype. It does not contain proprietary BOLT source code.

## Licences

- Source code: Apache License 2.0.
- Documentation and non-code text: CC BY 4.0.

## Author

Omar Baró · Unfire

## Local request protection (10 October)

The test/demo server binds to loopback by default; Docker users must explicitly set HOST=0.0.0.0 for a published container port. POST input is capped at 12 KiB and typed before model inference; oversized fields are refused rather than silently truncated. Upstream errors do not echo provider response bodies. This is a small demonstration boundary, not a production security audit.
