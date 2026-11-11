# Architecture

The copilot is a local investigation pipeline. An alert is untrusted text. It is screened, classified, enriched from a knowledge base the project controls, and turned into a cited narrative plus containment steps an analyst can accept or reject.

```mermaid
flowchart LR
    user[Analyst] --> ui[Streamlit UI]
    ui --> api[FastAPI]
    api --> graph[Investigation graph]
    graph --> guards[Guardrails]
    graph --> kb[Knowledge base]
    kb --> report[Cited report]
    graph --> report
```

## Stages

1. Guardrails redact email addresses, national identifiers, and token-shaped secrets, and refuse prompt-injection text.
2. Detection maps a small set of terms to ATT&CK technique IDs. Unmapped alerts stay low severity.
3. Threat intel retrieves the top knowledge chunks. Weak scores are dropped.
4. Investigation writes a narrative that names those chunks.
5. Remediation returns a fixed containment list for the mapped technique and a draft detection for review.

## What is intentionally local

The default retriever is TF-IDF in `rag/retriever.py`. A Chroma adapter is in the same module for a dense index, and it is not required to run tests. Gemini is not called. The narrative is deterministic so an interviewer can trace a wrong answer to a rule or a retrieved file.

## State

Each stage appends a step: agent name, one-line summary, and the evidence it used. That list is the explanation. There is no hidden chain of thought.
