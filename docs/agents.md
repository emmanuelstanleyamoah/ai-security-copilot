# Agents

The graph in `agents/graph.py` is five recorded stages:

| Stage | Role |
| --- | --- |
| guardrails | Accept or refuse the alert text |
| detection | Map terms to technique IDs and a severity |
| threat_intel | Retrieve knowledge chunks |
| investigation | Write the cited narrative |
| remediation | Return containment steps and a draft detection |

Detection, intel, investigation, and remediation are the four analyst stages. Guardrails wrap them.

## Contracts

Each stage reads the alert or the previous stage's structured fields and appends a step with evidence. Evidence is a list of terms, filenames, or control names. That is the explanation an analyst sees.

## Detection coverage

The reference rules cover T1566 phishing, T1059 command and scripting, and T1078 valid accounts. Anything else stays unmapped and low severity, with a recommendation to wait for the original sensor record.

## Draft detections

The remediation stage emits a short Sigma-style draft marked `status: draft`. It is a review artifact. It is not deployed to a SIEM by this service.

## LangGraph

The stages are plain functions with an explicit state object, which is the same shape a LangGraph node expects: state in, state out. The reference build does not import LangGraph, so tests do not depend on it. A later graph can call these functions from nodes without changing their inputs.
