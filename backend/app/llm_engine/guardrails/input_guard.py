"""
LLM Safety Guardrails, Prompt Sanitization & PII Masking
"""

import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class GuardrailResult:
    passed: bool
    sanitized_text: str
    violations: List[str]
    masked_pii_count: int


class PromptGuardrail:
    """Detects prompt injections, masks PII (Emails, Phones, SSNs), and enforces boundaries."""

    # Regex patterns for sensitive PII
    EMAIL_PATTERN = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    PHONE_PATTERN = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    SSN_PATTERN = r"\b\d{3}-\d{2}-\d{4}\b"

    # Known prompt injection signatures
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"disregard\s+the\s+system\s+prompt",
        r"system\s*override",
        r"you\s+are\s+now\s+in\s+developer\s+mode",
    ]

    def sanitize(self, text: str, max_chars: int = 10000) -> GuardrailResult:
        violations = []
        sanitized = text[:max_chars]

        # 1. Check prompt injection
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                violations.append(f"Prompt injection pattern detected: '{pattern}'")

        # 2. Mask PII
        masked_pii = 0
        email_matches = len(re.findall(self.EMAIL_PATTERN, sanitized))
        if email_matches:
            sanitized = re.sub(self.EMAIL_PATTERN, "[REDACTED_EMAIL]", sanitized)
            masked_pii += email_matches

        phone_matches = len(re.findall(self.PHONE_PATTERN, sanitized))
        if phone_matches:
            sanitized = re.sub(self.PHONE_PATTERN, "[REDACTED_PHONE]", sanitized)
            masked_pii += phone_matches

        ssn_matches = len(re.findall(self.SSN_PATTERN, sanitized))
        if ssn_matches:
            sanitized = re.sub(self.SSN_PATTERN, "[REDACTED_SSN]", sanitized)
            masked_pii += ssn_matches

        passed = len(violations) == 0

        return GuardrailResult(
            passed=passed,
            sanitized_text=sanitized,
            violations=violations,
            masked_pii_count=masked_pii,
        )


guardrail = PromptGuardrail()

    def scan_and_audit(self, text: str) -> dict:
        """Run comprehensive multi-vector safety audit and return diagnostic report."""
        injection_detected = self.check_prompt_injection(text)
        sanitized_text = self.redact_pii(text)
        pii_found = sanitized_text != text

        risk_score = 0.0
        if injection_detected:
            risk_score += 0.8
        if pii_found:
            risk_score += 0.4
        risk_score = min(risk_score, 1.0)

        return {
            "is_safe": not injection_detected and risk_score < 0.7,
            "prompt_injection_flagged": injection_detected,
            "pii_detected": pii_found,
            "sanitized_content": sanitized_text,
            "risk_score": round(risk_score, 2),
            "safety_action": "BLOCK" if injection_detected else ("SANITIZE" if pii_found else "ALLOW"),
        }
