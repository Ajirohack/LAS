"""
PII Redactor - Detect and redact Personally Identifiable Information.
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum

class PIIType(str, Enum):
    """Types of PII to detect."""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    NAME = "name"  # Requires NER
    ADDRESS = "address"  # Requires NER

class SensitivityLevel(str, Enum):
    """Sensitivity levels for redaction."""
    LOW = "low"  # Only SSN, credit cards
    MEDIUM = "medium"  # + emails, phones
    HIGH = "high"  # + IPs, potential names/addresses

class PIIRedactor:
    """
    Detect and redact PII from text.
    
    Uses regex patterns for common PII types.
    For production, integrate with Presidio or similar NER library.
    """
    
    def __init__(self, sensitivity: SensitivityLevel = SensitivityLevel.MEDIUM):
        self.sensitivity = sensitivity
        self.redaction_map: Dict[str, str] = {}  # For reversible redaction
        
        # Regex patterns
        self.patterns = {
            PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            PIIType.PHONE: r'\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
            PIIType.SSN: r'\b\d{3}-\d{2}-\d{4}\b',
            PIIType.CREDIT_CARD: r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            PIIType.IP_ADDRESS: r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        }
    
    def _should_redact(self, pii_type: PIIType) -> bool:
        """Check if PII type should be redacted based on sensitivity level."""
        if self.sensitivity == SensitivityLevel.LOW:
            return pii_type in [PIIType.SSN, PIIType.CREDIT_CARD]
        elif self.sensitivity == SensitivityLevel.MEDIUM:
            return pii_type in [PIIType.SSN, PIIType.CREDIT_CARD, PIIType.EMAIL, PIIType.PHONE]
        else:  # HIGH
            return True
    
    def redact(self, text: str, reversible: bool = False) -> Tuple[str, Dict[str, List[str]]]:
        """
        Redact PII from text.
        
        Args:
            text: Input text
            reversible: If True, store redactions for potential reversal
        
        Returns:
            Tuple of (redacted_text, detected_pii_dict)
        """
        redacted_text = text
        detected: Dict[str, List[str]] = {}
        
        for pii_type, pattern in self.patterns.items():
            if not self._should_redact(pii_type):
                continue
            
            matches = re.findall(pattern, text)
            if matches:
                detected[pii_type.value] = matches
                
                for match in matches:
                    placeholder = f"[REDACTED_{pii_type.value.upper()}]"
                    
                    if reversible:
                        # Store mapping for reversal
                        self.redaction_map[placeholder] = match
                    
                    redacted_text = redacted_text.replace(match, placeholder)
        
        return redacted_text, detected
    
    def unredact(self, redacted_text: str) -> str:
        """
        Reverse redactions (only if reversible=True was used).
        
        Args:
            redacted_text: Text with redactions
        
        Returns:
            Original text
        """
        unredacted = redacted_text
        for placeholder, original in self.redaction_map.items():
            unredacted = unredacted.replace(placeholder, original)
        return unredacted
    
    def detect_only(self, text: str) -> Dict[str, List[str]]:
        """
        Detect PII without redacting.
        
        Args:
            text: Input text
        
        Returns:
            Dictionary of detected PII by type
        """
        detected: Dict[str, List[str]] = {}
        
        for pii_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected[pii_type.value] = matches
        
        return detected

# Create singleton instance
_pii_redactor: Optional[PIIRedactor] = None

def get_pii_redactor(sensitivity: SensitivityLevel = SensitivityLevel.MEDIUM) -> PIIRedactor:
    """Get or create PIIRedactor instance."""
    global _pii_redactor
    if _pii_redactor is None:
        _pii_redactor = PIIRedactor(sensitivity=sensitivity)
    return _pii_redactor

# Example advanced PII detection with Presidio (commented - requires installation)
"""
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class PresidioPIIRedactor:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
    
    def redact(self, text: str):
        # Analyze text for PII
        results = self.analyzer.analyze(
            text=text,
            language='en',
            entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "LOCATION"]
        )
        
        # Anonymize detected PII
        anonymized = self.anonymizer.anonymize(text=text, analyzer_results=results)
        return anonymized.text
"""
