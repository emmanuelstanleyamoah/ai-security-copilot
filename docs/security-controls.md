# Security controls

Alerts are attacker-influenced content. The copilot treats them that way.

## Prompt injection

`security/guardrails.py` refuses the investigation when the alert asks the system to ignore instructions, reveal a system prompt, change persona, or disregard policy. Retrieval does not run after a refusal. The audit trail records the control name.

## Sensitive data

Email addresses, US national-identifier shapes, and common token prefixes are replaced with `[REDACTED_EMAIL]`, `[REDACTED_SSN]`, or `[REDACTED_SECRET]` before the narrative is stored. The same redaction runs on the output.

## Output limits

The draft detection is marked `status: draft`. Containment steps are chosen from a fixed map keyed by technique ID. The model path cannot invent a new action in the default build because there is no model call.

## What this does not claim

This is not Microsoft Presidio and it is not Guardrails AI. Those libraries cover the same jobs with broader recognizers. The in-repo controls are here so a reviewer can read the exact checks. Swap in Presidio or Guardrails AI behind `screen_input` and `screen_output` without changing the API.

## Access

The API has no authentication in this reference build. Put it behind an identity provider before any real alert data is sent to it. Do not point it at a production log pipeline as-is.
