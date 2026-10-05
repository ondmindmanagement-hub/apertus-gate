# Apertus Gate - Track 2B

Apertus Gate is a sovereign human-approval layer for AI workflows.

Before an external action is executed, the action and its context are reviewed by Apertus 1.5. The review returns a structured decision artifact with risk level, decision, reasons, missing information, and a safe next step.

## Run

From the repository root:

    make run

Then open:

    http://127.0.0.1:8787

Without APERTUS_API_KEY, the UI runs an explicitly labelled deterministic demo policy. To use real Apertus inference, export the key and optionally the endpoint/model before running:

    export APERTUS_API_KEY="..."
    export APERTUS_API_URL="https://api.publicai.co/v1/chat/completions"
    export APERTUS_MODEL="swiss-ai/apertus-v1.5-8b"
    make run

## Architecture

Browser UI -> Python review service -> Apertus 1.5 -> strict JSON normalization -> human-visible decision.

The prototype never executes the proposed external action.

## Target architecture

The project is deployable in all three allowed Track 2B target architectures:

- On-premise: run the Docker container on organization-managed infrastructure with a local or private Apertus endpoint.
- Air-gapped: point the container at a locally hosted Apertus instance reachable only on the internal network; no external service is required by the application itself.
- Sovereign Swiss cloud: deploy the same container with a Swiss-hosted Apertus endpoint and Swiss data residency.

## Tests

    make test

## Live evidence

data/apertus_live_run_2026-10-06.json records a live Apertus 1.5 70B run through Public AI / CSCS Lugano during the hackathon.

## Licences

Source code: Apache-2.0.
Documentation: CC-BY-4.0.
