from __future__ import annotations

import re
from dataclasses import dataclass, field

INJECTION_PATTERNS = (
    r"ignore (all |any )?(previous|prior) instructions",
    r"reveal (the )?system prompt",
    r"you are now",
    r"disregard (the )?(policy|guardrails|rules)",
    r"exfiltrate",
)

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SECRET_RE = re.compile(
    r"\b(?:AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,})\b"
)
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


@dataclass(frozen=True)
class ScreenResult:
    blocked: bool
    reasons: list[str] = field(default_factory=list)
    redacted: str = ""
    findings: list[str] = field(default_factory=list)


def screen_input(text: str) -> ScreenResult:
    folded = text.lower()
    reasons = [
        "prompt_injection"
        for pattern in INJECTION_PATTERNS
        if re.search(pattern, folded)
    ]
    redacted, findings = _redact(text)
    if reasons:
        return ScreenResult(blocked=True, reasons=reasons, redacted=redacted, findings=findings)
    return ScreenResult(blocked=False, reasons=[], redacted=redacted, findings=findings)


def screen_output(text: str) -> str:
    redacted, _findings = _redact(text)
    return redacted


def _redact(text: str) -> tuple[str, list[str]]:
    findings: list[str] = []

    def mark(label: str):
        def _sub(_match: re.Match[str]) -> str:
            findings.append(label)
            return f"[REDACTED_{label}]"

        return _sub

    redacted = SECRET_RE.sub(mark("SECRET"), text)
    redacted = EMAIL_RE.sub(mark("EMAIL"), redacted)
    redacted = SSN_RE.sub(mark("SSN"), redacted)
    return redacted, findings
