"""
VidhiChakshu (विधि-चक्षु) - Core AI Engine Test Suite
Tests PII redaction, archaic lexicon detection, and statutory knowledge graph traversals.
"""

import sys
import os

# Ensure python_backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
if os.path.exists(env_path):
    load_dotenv(env_path)

from services.pii_redactor import redact_indian_pii_regex
from services.lexicon_service import analyze_archaic_terms, ARCHAIC_LEGAL_LEXICON
from services.agent_rag import legal_graph, init_legal_graph
from services.pdf_generator import generate_certified_pdf_report
from services.ai_pipeline import extract_heritage_deed_intelligence

def test_pii_redaction_aadhaar():
    sample_text = "The applicant's Aadhaar number is 1234-5678-9012 and mobile is +91-9876543210."
    redacted = redact_indian_pii_regex(sample_text)
    assert "[AADHAAR_REDACTED]" in redacted
    assert "1234-5678-9012" not in redacted
    assert "[PHONE_REDACTED]" in redacted
    assert "9876543210" not in redacted

def test_pii_redaction_pan():
    sample_text = "Taxpayer PAN card identifier is ABCDE1234F registered in Mumbai."
    redacted = redact_indian_pii_regex(sample_text)
    assert "[PAN_REDACTED]" in redacted
    assert "ABCDE1234F" not in redacted

def test_archaic_lexicon_detection():
    sample_deed = (
        "This Bainama of agricultural land bearing Khasra No 142 is executed with "
        "clear Chauhaddi boundaries. The seller is a recognized Watandar holding Sanad rights."
    )
    terms = analyze_archaic_terms(sample_deed)
    term_names = [t["term"] for t in terms]
    assert "Bainama" in term_names
    assert "Khasra" in term_names
    assert "Chauhaddi" in term_names
    assert "Watandar" in term_names
    assert "Sanad" in term_names

def test_legal_knowledge_graph_structure():
    init_legal_graph()
    # Check criminal law mappings
    assert legal_graph.has_node("IPC_302")
    assert legal_graph.has_node("BNS_103")
    assert legal_graph.has_edge("IPC_302", "BNS_103")
    assert legal_graph.edges["IPC_302", "BNS_103"]["relation"] == "SUPERSEDED_BY"

    # Check property law nodes
    assert legal_graph.has_node("TPA_54")
    assert legal_graph.has_node("REG_17")
    assert legal_graph.has_edge("TPA_54", "REG_17")

    # Check constitutional rights
    assert legal_graph.has_node("Article_300A")
    assert legal_graph.has_node("Article_21")

def test_certified_pdf_generation():
    doc_data = {
        "document_id": "test_deed_1942.pdf",
        "summary": "This is a certified legal summary of an ancestral Bainama property deed.",
        "layman_summary": "This document proves clear ownership of the farm land.",
        "chauhaddi": {
            "plot_number": "Survey No 45/2",
            "area": "2 Bighas 10 Biswas",
            "village": "Mauza Rampur",
            "north": "Government Canal",
            "south": "Village Road",
            "east": "Land of Ram Lal",
            "west": "Field of Sham Sundar",
            "boundary_notes": "All four borders clearly marked and demarcated."
        },
        "lineage": {
            "patriarch_or_head": "Pandit Hariram Sharma",
            "family_members": [
                {"name": "Pandit Hariram Sharma", "relation": "Patriarch", "share": "100%", "generation": 1},
                {"name": "Gopal Sharma", "relation": "Son", "share": "50%", "generation": 2},
                {"name": "Mohan Sharma", "relation": "Son", "share": "50%", "generation": 2}
            ],
            "succession_type": "Ancestral Coparcenary"
        },
        "title_chain": [
            {"date_or_period": "1942", "event": "Sanad Grant", "parties": "Crown to Hariram", "status": "verified", "significance": "Root of title"},
            {"date_or_period": "1975", "event": "Succession", "parties": "To Gopal & Mohan", "status": "verified", "significance": "Mutation completed"}
        ],
        "title_health_score": 92,
        "title_defects": ["Minor spelling discrepancy in mutation entry #402"],
        "archaic_terms": [
            {
                "term": "Bainama",
                "origin": "Perso-Arabic",
                "category": "Conveyancing",
                "meaning": "Absolute deed of sale",
                "modern_significance": "Registered Sale Deed under TPA 1882",
                "citizen_summary": "Permanent land sale document"
            }
        ]
    }
    pdf_bytes = generate_certified_pdf_report(doc_data)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

if __name__ == "__main__":
    test_pii_redaction_aadhaar()
    test_pii_redaction_pan()
    test_archaic_lexicon_detection()
    test_legal_knowledge_graph_structure()
    test_certified_pdf_generation()
    print("[SUCCESS] All VidhiChakshu AI Engine test cases passed successfully!")
