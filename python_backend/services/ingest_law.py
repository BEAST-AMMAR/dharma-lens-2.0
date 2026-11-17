import sys
import os
from dotenv import load_dotenv

# Load root .env.local and .env files
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env.local'))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))
load_dotenv()

from sentence_transformers import SentenceTransformer
from supabase import create_client, Client

# ──────────────────────────────────────────────────────────────────
# FAIL-FAST ENVIRONMENT — No hardcoded fallback credentials
# ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL:
    raise RuntimeError("CRITICAL: VITE_SUPABASE_URL environment variable is missing.")
if not SUPABASE_KEY:
    raise RuntimeError("CRITICAL: SUPABASE_SERVICE_ROLE_KEY or VITE_SUPABASE_ANON_KEY environment variable is missing.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Load DL Embedding Model (runs on CPU to keep GPU VRAM free for LLM)
print("Loading CPU Embedding Model (all-mpnet-base-v2, 768-dim)...")
try:
    model = SentenceTransformer('all-mpnet-base-v2', device='cpu')
except Exception as e:
    print(f"[Warning] Loading all-mpnet-base-v2 failed ({e}). Falling back to BAAI/bge-m3...")
    model = SentenceTransformer('BAAI/bge-m3', device='cpu')


def embed_and_store_legal_text(source_type: str, section_number: str, title: str, content: str, superseded_by: str = None, replaces: str = None):
    """
    Generates a DL embedding for legal text and stores it in Supabase pgvector table.
    """
    print(f"Embedding {source_type} Section {section_number}...")
    
    embedding = model.encode(content).tolist()
    
    data = {
        "source_type": source_type,
        "section_number": section_number,
        "title": title,
        "content": content,
        "embedding": embedding,
        "superseded_by": superseded_by,
        "replaces": replaces,
        "metadata": {"length": len(content)}
    }
    
    try:
        res = supabase.table("legal_knowledge").insert(data).execute()
        print(f"  [OK] Stored {source_type} {section_number} successfully.")
    except Exception as err:
        print(f"  [ERR] Error storing section {section_number}: {err}")

def run_ingestion_pipeline():
    """
    Ingest canonical Indian Legal Statutory Corpus (IPC, BNS, BNSS, BSA, Constitution).
    Expanded corpus covering the core sections most frequently encountered in Indian legal practice.
    """
    law_corpus = [
        # ── Bharatiya Nyaya Sanhita (BNS 2023) — Criminal Law ──
        {
            "source": "BNS",
            "section": "103",
            "title": "Punishment for Murder",
            "content": "Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine. This section replaces IPC Section 302.",
            "replaces": "IPC 302"
        },
        {
            "source": "BNS",
            "section": "303",
            "title": "Theft",
            "content": "Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property in order to such taking, commits theft. Punishable with imprisonment up to 3 years, or with fine, or both.",
            "replaces": "IPC 378"
        },
        {
            "source": "BNS",
            "section": "318",
            "title": "Cheating",
            "content": "Whoever, by deceiving any person, fraudulently or dishonestly induces the person so deceived to deliver any property to any person, or to consent that any person shall retain any property, commits the offence of cheating.",
            "replaces": "IPC 420"
        },
        {
            "source": "BNS",
            "section": "64",
            "title": "Punishment for Rape",
            "content": "Whoever commits rape shall be punished with rigorous imprisonment for a term which shall not be less than ten years but which may extend to imprisonment for life, and shall also be liable to fine.",
            "replaces": "IPC 376"
        },
        {
            "source": "BNS",
            "section": "106",
            "title": "Causing Death by Negligence",
            "content": "Whoever causes the death of any person by doing any rash or negligent act not amounting to culpable homicide shall be punished with imprisonment which may extend to five years, and shall also be liable to fine.",
            "replaces": "IPC 304A"
        },
        {
            "source": "BNS",
            "section": "85",
            "title": "Cruelty by Husband or Relatives",
            "content": "Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine.",
            "replaces": "IPC 498A"
        },
        {
            "source": "BNS",
            "section": "74",
            "title": "Assault on Woman",
            "content": "Whoever assaults or uses criminal force to any woman, intending to outrage or knowing it to be likely that he will thereby outrage her modesty, shall be punished with imprisonment which may extend to two years, or with fine, or both.",
            "replaces": "IPC 354"
        },
        {
            "source": "BNS",
            "section": "351",
            "title": "Criminal Intimidation",
            "content": "Whoever threatens another with any injury to his person, reputation or property, or to the person or reputation of any one in whom that person is interested, with intent to cause alarm to that person, commits criminal intimidation.",
            "replaces": "IPC 506"
        },
        {
            "source": "BNS",
            "section": "3(5)",
            "title": "Common Intention",
            "content": "When a criminal act is done by several persons in furtherance of the common intention of all, each of such persons is liable for that act in the same manner as if it were done by him alone.",
            "replaces": "IPC 34"
        },
        {
            "source": "BNS",
            "section": "61",
            "title": "Criminal Conspiracy",
            "content": "When two or more persons agree to do, or cause to be done, an illegal act, or an act which is not illegal by illegal means, such an agreement is designated a criminal conspiracy.",
            "replaces": "IPC 120B"
        },
        
        # ── Indian Penal Code (IPC 1860) — Legacy Criminal Law ──
        {
            "source": "IPC",
            "section": "302",
            "title": "Punishment for Murder",
            "content": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
            "superseded_by": "BNS 103"
        },
        {
            "source": "IPC",
            "section": "378",
            "title": "Theft",
            "content": "Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property, commits theft.",
            "superseded_by": "BNS 303"
        },
        {
            "source": "IPC",
            "section": "420",
            "title": "Cheating and Dishonestly Inducing Delivery of Property",
            "content": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, shall be punished with imprisonment which may extend to seven years, and shall also be liable to fine.",
            "superseded_by": "BNS 318"
        },
        {
            "source": "IPC",
            "section": "376",
            "title": "Punishment for Rape",
            "content": "Whoever commits rape shall be punished with rigorous imprisonment for a term which shall not be less than ten years but may extend to imprisonment for life, and shall also be liable to fine.",
            "superseded_by": "BNS 64"
        },
        {
            "source": "IPC",
            "section": "304A",
            "title": "Causing Death by Negligence",
            "content": "Whoever causes the death of any person by doing any rash or negligent act not amounting to culpable homicide, shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both.",
            "superseded_by": "BNS 106"
        },
        {
            "source": "IPC",
            "section": "498A",
            "title": "Husband or Relative of Husband Subjecting Woman to Cruelty",
            "content": "Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine.",
            "superseded_by": "BNS 85"
        },
        
        # ── Bharatiya Nagarik Suraksha Sanhita (BNSS 2023) — Procedural Law ──
        {
            "source": "BNSS",
            "section": "173",
            "title": "Information in Cognizable Cases (FIR)",
            "content": "Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction, and be read over to the informant.",
            "replaces": "CrPC 154"
        },
        {
            "source": "BNSS",
            "section": "180",
            "title": "Examination of Witnesses by Police",
            "content": "Any police officer making an investigation may examine orally any person supposed to be acquainted with the facts and circumstances of the case.",
            "replaces": "CrPC 161"
        },
        {
            "source": "BNSS",
            "section": "35",
            "title": "When Police May Arrest Without Warrant",
            "content": "Any police officer may without an order from a Magistrate and without a warrant, arrest any person who has been concerned in any cognizable offence, or against whom a reasonable complaint or credible information has been received.",
            "replaces": "CrPC 41"
        },
        {
            "source": "BNSS",
            "section": "482",
            "title": "Anticipatory Bail",
            "content": "Where any person has reason to believe that he may be arrested on an accusation of having committed a non-bailable offence, he may apply to the High Court or the Court of Session for a direction for bail.",
            "replaces": "CrPC 438"
        },
        
        # ── Constitution of India — Fundamental Rights ──
        {
            "source": "Constitution",
            "section": "Article 14",
            "title": "Equality Before Law",
            "content": "The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India."
        },
        {
            "source": "Constitution",
            "section": "Article 19",
            "title": "Protection of Certain Rights Regarding Freedom of Speech",
            "content": "All citizens shall have the right to freedom of speech and expression; to assemble peaceably and without arms; to form associations or unions; to move freely throughout the territory of India; to reside and settle in any part of the territory of India; and to practise any profession, or to carry on any occupation, trade or business."
        },
        {
            "source": "Constitution",
            "section": "Article 20",
            "title": "Protection in Respect of Conviction for Offences",
            "content": "No person shall be convicted of any offence except for violation of a law in force at the time of the commission of the act charged as an offence, nor be subjected to a penalty greater than that which might have been inflicted under the law in force at the time of the commission of the offence."
        },
        {
            "source": "Constitution",
            "section": "Article 21",
            "title": "Protection of Life and Personal Liberty",
            "content": "No person shall be deprived of his life or personal liberty except according to procedure established by law."
        },
        {
            "source": "Constitution",
            "section": "Article 22",
            "title": "Protection Against Arrest and Detention",
            "content": "No person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest nor shall he be denied the right to consult, and to be defended by, a legal practitioner of his choice."
        },
        {
            "source": "Constitution",
            "section": "Article 32",
            "title": "Remedies for Enforcement of Fundamental Rights",
            "content": "The right to move the Supreme Court by appropriate proceedings for the enforcement of the rights conferred by this Part is guaranteed. The Supreme Court shall have power to issue directions or orders or writs."
        },
        {
            "source": "Constitution",
            "section": "Article 300A",
            "title": "Persons Not to Be Deprived of Property Save by Authority of Law",
            "content": "No person shall be deprived of his property save by authority of law. Recognizes property ownership as a human and constitutional right."
        },

        # ── Transfer of Property Act, 1882 (Land & Property Conveyancing) ──
        {
            "source": "TPA",
            "section": "54",
            "title": "Sale of Immovable Property",
            "content": "Sale is a transfer of ownership in exchange for a price paid or promised or part-paid and part-promised. In the case of tangible immovable property of the value of one hundred rupees and upwards, transfer can be made only by a registered instrument.",
            "replaces": None
        },
        {
            "source": "TPA",
            "section": "58",
            "title": "Mortgage and Mortgage-money Defined",
            "content": "A mortgage is the transfer of an interest in specific immovable property for the purpose of securing the payment of money advanced or to be advanced by way of loan, an existing or future debt, or the performance of an engagement which may give rise to a pecuniary liability.",
            "replaces": None
        },
        {
            "source": "TPA",
            "section": "105",
            "title": "Lease of Immovable Property",
            "content": "A lease of immovable property is a transfer of a right to enjoy such property, made for a certain time, express or implied, or in perpetuity, in consideration of a price paid or promised, or of money, a share of crops, service or any other thing of value.",
            "replaces": None
        },
        {
            "source": "TPA",
            "section": "122",
            "title": "Gift Defined",
            "content": "Gift is the transfer of certain existing movable or immovable property made voluntarily and without consideration, by one person, called the donor, to another, called the donee, and accepted by or on behalf of the donee.",
            "replaces": None
        },
        {
            "source": "TPA",
            "section": "53A",
            "title": "Part Performance",
            "content": "Where any person contracts to transfer for consideration any immovable property by writing signed by him or on his behalf, and the transferee has in part performance of the contract taken possession of the property, the transferor is debarred from enforcing against the transferee any right in respect of the property.",
            "replaces": None
        },

        # ── Indian Registration Act, 1908 ──
        {
            "source": "Registration Act",
            "section": "17",
            "title": "Documents of which Registration is Compulsory",
            "content": "Instruments of gift of immovable property; other non-testamentary instruments which purport or operate to create, declare, assign, limit or extinguish any right, title or interest of the value of one hundred rupees and upwards, to or in immovable property; leases of immovable property from year to year, or for any term exceeding one year, or reserving a yearly rent.",
            "replaces": None
        },
        {
            "source": "Registration Act",
            "section": "49",
            "title": "Effect of Non-Registration of Documents Required to be Registered",
            "content": "No document required by section 17 to be registered shall affect any immovable property comprised therein, or be received as evidence of any transaction affecting such property, unless it has been registered.",
            "replaces": None
        },

        # ── Indian Stamp Act, 1899 ──
        {
            "source": "Stamp Act",
            "section": "33",
            "title": "Examination and Impounding of Instruments",
            "content": "Every person having by law or consent of parties authority to receive evidence, and every person in charge of a public office, before whom any instrument chargeable with duty is produced, shall impound the same if it appears that such instrument is not duly stamped.",
            "replaces": None
        },
        {
            "source": "Stamp Act",
            "section": "35",
            "title": "Instruments Not Duly Stamped Inadmissible in Evidence",
            "content": "No instrument chargeable with duty shall be admitted in evidence for any purpose by any person having by law or consent of parties authority to receive evidence, or shall be acted upon, registered or authenticated by any such person or by any public officer, unless such instrument is duly stamped.",
            "replaces": None
        },

        # ── Bharatiya Sakshya Adhiniyam, 2023 (BSA - Evidence Law) ──
        {
            "source": "BSA",
            "section": "57",
            "title": "Primary Evidence",
            "content": "Primary evidence means the document itself produced for the inspection of the Court. Where a document is executed in several parts, each part is primary evidence of the document.",
            "replaces": "IEA 62"
        },
        {
            "source": "BSA",
            "section": "58",
            "title": "Secondary Evidence",
            "content": "Secondary evidence includes certified copies, copies made from the original by mechanical processes, copies compared with the original, counterparts of documents as against the parties who did not execute them, and oral accounts of contents given by persons who have seen it.",
            "replaces": "IEA 63"
        },
        {
            "source": "BSA",
            "section": "61",
            "title": "Electronic or Digital Record",
            "content": "Nothing in this Adhiniyam shall apply to electronic records unless accompanied by a certificate signed by a person occupying a responsible official position in relation to the operation of the relevant device.",
            "replaces": "IEA 65B"
        },
        {
            "source": "BSA",
            "section": "84",
            "title": "Presumption as to Ancient Documents (30 Years Old)",
            "content": "Where any document, purporting or proved to be thirty years old, is produced from any custody which the Court in the particular case considers proper, the Court may presume that the signature and every other part of such document, which purports to be in the handwriting of any particular person, is in that person's handwriting, and that it was duly executed and attested.",
            "replaces": "IEA 90"
        },
    ]
    
    print(f"\n{'='*60}")
    print(f"  VIDHICHAKSHU - Legal Knowledge Ingestion Pipeline")
    print(f"  Corpus Size: {len(law_corpus)} statutory sections")
    print(f"  Target: Supabase pgvector (legal_knowledge table)")
    print(f"{'='*60}\n")
    
    for i, law in enumerate(law_corpus, 1):
        print(f"[{i}/{len(law_corpus)}] ", end="")
        embed_and_store_legal_text(
            source_type=law["source"],
            section_number=law["section"],
            title=law["title"],
            content=law["content"],
            superseded_by=law.get("superseded_by"),
            replaces=law.get("replaces")
        )
    
    print(f"\n{'='*60}")
    print(f"  Ingestion Complete: {len(law_corpus)} sections embedded & stored.")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    print("Starting Legal Knowledge Ingestion Pipeline...")
    run_ingestion_pipeline()
    print("Pipeline Complete.")
