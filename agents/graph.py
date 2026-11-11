from __future__ import annotations

from dataclasses import asdict, dataclass, field

from rag.retriever import Hit, TfidfKnowledgeBase
from security.guardrails import screen_input, screen_output

TECHNIQUE_RULES = (
    (("phish", "invoice", "mailbox", "attachment"), "T1566", "Initial Access", "high"),
    (("powershell", "encodedcommand", "-enc", "cmd.exe"), "T1059", "Execution", "high"),
    (("impossible travel", "privileged", "new admin", "valid account"), "T1078", "Defense Evasion", "medium"),
)

REMEDIATION = {
    "T1566": [
        "Quarantine the message and block the sender domain.",
        "Reset the mailbox session and review mailbox rules.",
        "Hunt for the same sender and attachment hash across the tenant.",
    ],
    "T1059": [
        "Isolate the host from the network.",
        "Capture the process tree and the decoded command line for the case record.",
        "Block the parent script path in application control while the host is rebuilt.",
    ],
    "T1078": [
        "Disable the account and revoke active sessions.",
        "Require phishing-resistant MFA before re-enabling access.",
        "Review privilege grants made in the same window.",
    ],
}


@dataclass
class Report:
    status: str
    severity: str
    technique_ids: list[str]
    narrative: str
    remediation: list[str]
    detection_draft: str
    citations: list[dict[str, str | float]]
    steps: list[dict[str, object]] = field(default_factory=list)
    guardrail_findings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


def run_investigation(alert_text: str, retriever: TfidfKnowledgeBase | None = None) -> Report:
    """Run the four analyst stages and record every decision."""
    knowledge = retriever or TfidfKnowledgeBase()
    steps: list[dict[str, object]] = []
    screen = screen_input(alert_text)
    steps.append(
        {
            "agent": "guardrails",
            "summary": "blocked" if screen.blocked else "accepted",
            "evidence": screen.reasons or screen.findings or ["no sensitive tokens"],
        }
    )
    if screen.blocked:
        return Report(
            status="refused",
            severity="none",
            technique_ids=[],
            narrative="The alert text tripped a prompt-injection control, so no investigation was run.",
            remediation=["Treat the alert body as untrusted content and open the case from the original sensor record."],
            detection_draft="",
            citations=[],
            steps=steps,
            guardrail_findings=screen.reasons,
        )

    detection = _detect(screen.redacted)
    steps.append(
        {
            "agent": "detection",
            "summary": f"{detection['severity']} {', '.join(detection['technique_ids']) or 'unmapped'}",
            "evidence": detection["matched_terms"],
        }
    )
    query = screen.redacted + " " + " ".join(detection["technique_ids"])
    hits = knowledge.search(query, top_k=3)
    steps.append(
        {
            "agent": "threat_intel",
            "summary": f"{len(hits)} knowledge chunks",
            "evidence": [hit.source for hit in hits],
        }
    )
    narrative = screen_output(_narrate(screen.redacted, detection, hits))
    remediation = _remediate(detection["technique_ids"])
    draft = _draft_detection(detection)
    steps.append(
        {
            "agent": "investigation",
            "summary": "narrative cites retrieved chunks only",
            "evidence": [hit.source for hit in hits],
        }
    )
    steps.append(
        {
            "agent": "remediation",
            "summary": f"{len(remediation)} analyst actions",
            "evidence": detection["technique_ids"],
        }
    )
    return Report(
        status="completed",
        severity=detection["severity"],
        technique_ids=detection["technique_ids"],
        narrative=narrative,
        remediation=remediation,
        detection_draft=draft,
        citations=[
            {"source": hit.source, "title": hit.title, "score": round(hit.score, 3)} for hit in hits
        ],
        steps=steps,
        guardrail_findings=screen.findings,
    )


def _detect(text: str) -> dict[str, object]:
    folded = text.lower()
    matched: list[tuple[str, str, str]] = []
    terms: list[str] = []
    for keys, technique, tactic, severity in TECHNIQUE_RULES:
        found = [key for key in keys if key in folded]
        if found:
            matched.append((technique, tactic, severity))
            terms.extend(found)
    if not matched:
        return {"technique_ids": [], "tactics": [], "severity": "low", "matched_terms": []}
    rank = {"high": 2, "medium": 1, "low": 0}
    severity = max((item[2] for item in matched), key=lambda item: rank[item])
    return {
        "technique_ids": sorted({item[0] for item in matched}),
        "tactics": sorted({item[1] for item in matched}),
        "severity": severity,
        "matched_terms": sorted(set(terms)),
    }


def _narrate(alert: str, detection: dict[str, object], hits: list[Hit]) -> str:
    techniques = ", ".join(detection["technique_ids"]) or "no mapped technique"
    tactics = ", ".join(detection["tactics"]) or "unmapped"
    if not hits:
        evidence = "No knowledge-base chunk scored above the abstain threshold."
    else:
        evidence = " ".join(f"[{hit.source}] {hit.title}." for hit in hits)
    return (
        f"Severity {detection['severity']}. Mapped techniques: {techniques} ({tactics}). "
        f"The alert, after redaction, was: {alert.strip()} "
        f"Retrieved evidence: {evidence} "
        "The narrative uses only those chunks. An analyst still owns the disposition."
    )


def _remediate(technique_ids: list[str]) -> list[str]:
    actions: list[str] = []
    for technique in technique_ids:
        actions.extend(REMEDIATION.get(technique, []))
    if not actions:
        actions.append("Keep the case open and ask for the original sensor record before acting.")
    return actions


def _draft_detection(detection: dict[str, object]) -> str:
    techniques = detection["technique_ids"]
    if not techniques:
        return ""
    terms = detection["matched_terms"]
    selection = " or ".join(f"alert_text contains '{term}'" for term in terms) or "none"
    return (
        "title: Draft detection for analyst review\n"
        f"tags:\n  - attack.{techniques[0].lower()}\n"
        "logsource:\n  product: security_alert\n  service: copilot\n"
        "detection:\n"
        f"  selection: {selection}\n"
        "  condition: selection\n"
        "falsepositives:\n  - analyst must confirm the sensor context\n"
        "level: high\n"
        "status: draft\n"
    )
