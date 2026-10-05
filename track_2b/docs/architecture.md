# Architecture

Apertus Gate separates policy/UI from model hosting.

Browser -> Review service -> Apertus endpoint -> Normalizer -> Decision artifact

The review service never executes the proposed action. A downstream system may enforce the decision artifact.
