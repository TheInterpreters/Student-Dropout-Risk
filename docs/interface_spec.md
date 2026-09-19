# Decision-Support and Human-Study Interface Specification

## Purpose and scope

The project will deliver a lightweight browser-based research prototype, preferably in
Streamlit. It will demonstrate the frozen dropout model and administer the forward-
simulation study. It is not a production AIT service and will not accept real AIT
student records.

## Shared technical pipeline

Both interface modes must load the same versioned artefacts used in the final evaluation:

1. feature schema and temporal window;
2. preprocessing pipeline;
3. frozen TabICL configuration and decision threshold;
4. explanation configuration and feature-group mapping;
5. model-card version and limitation text.

The interface must reject missing, extra, invalid or out-of-range fields rather than
silently changing them. Model, data-split and interface versions must be shown in an
audit panel.

## Mode A — decision-support demonstration

This mode will use only pre-approved, pseudonymised UCI test cases. It will show:

- the student profile and prediction time;
- frozen dropout class and probability;
- local feature contributions with direction and magnitude;
- faithfulness and stability summaries or a clear warning when evidence is weak;
- immutable/historical factors separated from potentially changeable conditions;
- a feasible support-oriented counterfactual, or an explicit no-recourse result;
- intended-use, non-causality and non-deployment warnings.

This mode demonstrates decision support. It must not phrase the prediction as a diagnosis,
guarantee or automated decision.

## Mode B — blinded forward-simulation study

The study mode must:

- display the consent screen before any case;
- assign a pseudonymous participant ID and randomized A/B group using a recorded seed;
- present the same 10 pre-selected UCI cases in randomized order;
- show the profile only to Group A;
- add feature contributions for Group B while hiding the output, probability, threshold,
  base value and predicted class until the response is submitted;
- record predicted output, confidence, integer completion time and the three free-text
  responses defined in `human_study_instrument.md`;
- prevent answer revision after the model output is revealed;
- support withdrawal and record only the permitted exclusion reason.

## Data handling and deployment boundary

- No names, AIT student IDs or AIT administrative records will be collected.
- Raw free text will remain outside version control.
- The prototype will run locally or in a controlled course environment; no public
  deployment will occur without a separate privacy and security review.
- Only aggregate study results and paraphrased comments will enter the report.
- Instructor guidance and any applicable institutional approval must be confirmed before
  participant recruitment.

## Acceptance checks before use

1. The interface produces the same probabilities as the evaluation pipeline for fixed
   test cases.
2. Group B cannot see any value that directly reveals the model output before answering.
3. Both groups receive identical profiles and differ only in explanation visibility.
4. Case order, assignment seed, timer and exclusion log are reproducible.
5. Invalid fields are rejected and no real-person data are persisted.
6. The displayed model version, explanation settings and limitations match the model card.

## Implementation gate

Interface implementation begins only after the model, threshold, explanation protocol
and 10 study cases are frozen. Until then, this document defines the required behaviour
without creating a misleading deployment around a provisional model.
