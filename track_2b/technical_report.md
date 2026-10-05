# Technical report - Apertus Gate

- **Track:** Track 2B - Apertus Gate
- **Event:** Online
- **Team:** Unfire - Omar Baró
- **Demo:** https://raw.githubusercontent.com/ondmindmanagement-hub/apertus-gate/main/demo/apertus-gate-demo.mp4

## 1. Summary

Apertus Gate adds an explicit review boundary before an agent performs an external action. A proposed action and its context are sent to Apertus 1.5, which returns a structured risk decision: allow, human_review, or required_block, plus reasons, missing information and a safe next step. The prototype never executes the action. In a live test, Apertus 1.5 70B classified an unapproved EUR 25,000 supplier payment as high risk and required_block, directing the workflow to human approval.

## 2. Architecture

Browser UI -> Python review service -> OpenAI-compatible Apertus endpoint -> strict JSON normalization -> human-visible decision.

Credentials stay server-side. Inputs are bounded. Unknown risk labels normalize to high and unknown decisions normalize to human_review.

### Target architecture (mandatory)

Apertus Gate is deployable in all three allowed target architectures.

**a) On-premise:** the Docker container runs on organisation-managed infrastructure and points to a locally hosted Apertus service.

**b) Air-gapped:** the container and Apertus weights can run on an isolated internal network. The application has no mandatory external runtime dependency; the hosted endpoint is only one configuration option.

**c) Sovereign Swiss cloud:** the same container can target a Swiss-hosted Apertus endpoint with Swiss jurisdiction and data residency.

Build-time dependency: a Docker base image. Runtime dependencies: Python standard library plus the configured Apertus endpoint. In fully local deployment the endpoint is local/private.

## 3. Use of Apertus

- **Model:** swiss-ai/Apertus-v1.5-8B for the default API configuration; live evidence was collected with Apertus 1.5 70B.
- **How it is used:** inference / risk reasoning at action boundaries.
- **Where it runs:** provider-neutral OpenAI-compatible endpoint; live evidence used Public AI on CSCS infrastructure in Lugano.

The system prompt requires a fixed JSON schema containing risk_level, decision, reasons, missing_information and safe_next_step. The model is asked to consider reversibility, external side effects, financial/legal/security impact, data sensitivity and whether a human should approve before execution.

No fine-tuning or adapters are used.

## 4. Data

No private or human-subject dataset is required.

The repository includes a small developer-created evaluation set in data/evaluation_cases.json and one developer-created live model-response record in data/apertus_live_run_2026-10-06.json.

All evaluation prompts were created by the project author for the hackathon. No personal data is included. The repository data is released with the project under the applicable open-source documentation/data terms.

## 5. Evaluation

Task: classify proposed AI actions into a review decision that fails safely when the action is high impact or when model output is malformed.

| Setup | Metric | Result |
|---|---|---|
| Deterministic demo policy | Unit tests | 5/5 passing |
| Apertus 1.5 70B live test | High-risk unapproved payment | high / required_block |
| Output normalizer | Invalid risk/decision labels | defaults to high / human_review |

The live test used an unapproved EUR 25,000 supplier payment. Apertus returned high risk, required_block, and human approval as the safe next step.

## 6. Limitations

This is a hackathon prototype, not a formal compliance system. LLM decisions can be wrong or inconsistent. Only one live 70B case is currently included, and the developer evaluation set is small. Production use would require organization-specific policy, calibration data, authenticated reviewers, persistent audit storage, stronger input validation, model/version pinning and systematic evaluation across many scenarios.

## 7. Reproducibility

Repository: https://github.com/ondmindmanagement-hub/apertus-gate

Run from a clean checkout:

    make run

The Makefile builds and starts a Docker container. Without a key, the UI runs a clearly labelled deterministic demo policy. For real Apertus inference, export APERTUS_API_KEY and optionally APERTUS_API_URL / APERTUS_MODEL before make run.

Tests:

    make test

Live evidence is stored at data/apertus_live_run_2026-10-06.json.

Exact submission commit will be recorded before final submission.

## 8. Next steps

1. Expand the labelled action benchmark.
2. Compare Apertus 8B and 70B consistency.
3. Add signed decision records and tamper-evident audit logs.
4. Add a real human approval queue.
5. Measure latency and cost per decision boundary.

## License

Creative Commons Attribution 4.0 (CC-BY-4.0) for this report. Source code is Apache-2.0.

## References

- Apertus documentation: https://apertus-ai.org/docs/
- Hack Apertus Track 2B template: https://github.com/HackApertus/project-template/tree/main/track_2b
- Public AI API docs: https://platform.publicai.co/docs
