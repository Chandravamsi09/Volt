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
