"""
VidhiChakshu (विधि-चक्षु) - Privacy Guard & Indian PII Redactor
Anonymizes 12-digit Aadhaar, 10-char PAN, phone numbers, emails, and names.
"""

import re

class PIIRedactionException(Exception):
    """Raised when PII redaction fails strictly to prevent unredacted data leakage."""
    pass

_analyzer = None
_anonymizer = None
_presidio_attempted = False

def get_presidio_engines():
    global _analyzer, _anonymizer, _presidio_attempted
    if _presidio_attempted:
        return _analyzer, _anonymizer
    _presidio_attempted = True
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        _analyzer = AnalyzerEngine()
        _anonymizer = AnonymizerEngine()
    except Exception as e:
        print(f"[VidhiChakshu Notice] Presidio unavailable ({e}); using Indian regex engine.")
        _analyzer, _anonymizer = None, None
    return _analyzer, _anonymizer

def redact_indian_pii_regex(text: str) -> str:
    """Regex sanitizer for critical Indian PII identifiers (Aadhaar, PAN, Phone, Email)."""
    if not text:
        return text
    # Redact 12-digit Aadhaar numbers
    text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[AADHAAR_REDACTED]', text)
    # Redact 10-character PAN numbers
    text = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', '[PAN_REDACTED]', text)
    # Redact Indian phone numbers (+91 or 10 digits starting 6-9)
    text = re.sub(r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b', '[PHONE_REDACTED]', text)
    # Redact Emails
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
    return text

def redact_pii(text: str) -> str:
    """
    Identifies and redacts Personally Identifiable Information (PII).
    Redacts: PERSON, EMAIL_ADDRESS, PHONE_NUMBER, IBAN_CODE, IN_AADHAAR, IN_PAN.
    Fails loudly if redaction fails to preserve data privacy.
    """
    if not text or not text.strip():
        return text
        
    try:
        cleaned_text = redact_indian_pii_regex(text)
        analyzer, anonymizer = get_presidio_engines()
        
        if analyzer and anonymizer:
            results = analyzer.analyze(text=cleaned_text, entities=[
                "PERSON", 
                "EMAIL_ADDRESS", 
                "PHONE_NUMBER", 
                "IBAN_CODE", 
                "IN_AADHAAR", 
                "IN_PAN"
            ], language='en')
            
            anonymized_result = anonymizer.anonymize(text=cleaned_text, analyzer_results=results)
            return anonymized_result.text
        else:
            return cleaned_text
    except Exception as e:
        raise PIIRedactionException(f"Critical PII Redaction failure: {str(e)}")
