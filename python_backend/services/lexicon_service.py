"""
VidhiChakshu (विधि-चक्षु) - Historical & Archaic Revenue Legal Lexicon Service
Comprehensive dictionary of century-old Persian, Urdu, Marathi (Modi), Kannada (Halegannada),
and Sanskrit land revenue, judicial, and conveyancing terminology.
"""

import re
from typing import List, Dict, Any

# Comprehensive Historical Revenue and Legal Lexicon
ARCHAIC_LEGAL_LEXICON: List[Dict[str, Any]] = [
    # ── Persian / Urdu / Nastaliq Land Revenue & Conveyancing Terms ──
    {
        "term": "Bainama",
        "aliases": ["Beynama", "Bynamah", "Bae-Nama", "बयनामा", "بیع نامہ"],
        "origin": "Perso-Arabic (Urdu)",
        "category": "Conveyance / Title Deed",
        "meaning": "Deed of absolute sale. A formal legal instrument transferring complete ownership of immovable property from seller (Baye) to buyer (Mushtari).",
        "modern_significance": "Equivalent to a registered Sale Deed under Section 54 of the Transfer of Property Act, 1882.",
        "citizen_summary": "Sale Deed (Proof of full purchase and ownership of the property)."
    },
    {
        "term": "Khasra",
        "aliases": ["Khasra No", "Khasra Number", "खसरा", "خسرہ"],
        "origin": "Persian",
        "category": "Land Survey & Demarcation",
        "meaning": "A specific agricultural field or plot number assigned during official cadastral land surveys.",
        "modern_significance": "Survey Number or Cadastral Plot Number in modern revenue and land records.",
        "citizen_summary": "Plot or Survey Number identifying your exact piece of land on the village map."
    },
    {
        "term": "Khatauni",
        "aliases": ["Khatoni", "Khatauni No", "खतौनी", "کھتونی"],
        "origin": "Persian",
        "category": "Record of Rights (RoR)",
        "meaning": "Register of holdings. An official revenue ledger showing all land parcels owned by a cultivator/landowner in a village, their areas, and land revenue payable.",
        "modern_significance": "Modern Record of Rights (RoR) / Jamabandi Register.",
        "citizen_summary": "Owner's passbook listing all plots owned by a person in that village."
    },
    {
        "term": "Jamabandi",
        "aliases": ["Jambandi", "जमाबंदी", "جمع بندی"],
        "origin": "Persian",
        "category": "Revenue Assessment",
        "meaning": "Annual land revenue assessment roll and master register of rights, ownership, tenancies, and revenue dues.",
        "modern_significance": "Core Record of Rights (RoR) maintained under state Land Revenue Codes.",
        "citizen_summary": "Master Government Land Record showing legal ownership and crop details."
    },
    {
        "term": "Fard",
        "aliases": ["Fard-e-Malkiyat", "Fard Malkiyat", "फर्द", "فرد"],
        "origin": "Arabic / Persian",
        "category": "Certified Title Extract",
        "meaning": "An official certified extract from the land register issued by the Patwari/Revenue officer showing proof of ownership.",
        "modern_significance": "Certified Copy of Record of Rights / 7/12 Extract / RTC.",
        "citizen_summary": "Official certificate issued by the Patwari proving you are the recognized owner."
    },
    {
        "term": "Dakhil-Kharij",
        "aliases": ["Dakhil Kharij", "Intiqal", "दाखिल-खारिज", "दाखिल खारिज", "داخل خارج", "انتقال"],
        "origin": "Persian / Arabic",
        "category": "Property Mutation",
        "meaning": "Mutation of land. 'Kharij' = striking off the former owner's name; 'Dakhil' = recording the new owner's name in revenue records.",
        "modern_significance": "Revenue Mutation (Namantaran / Ferfar). Does not confer title by itself, but updates fiscal liability.",
        "citizen_summary": "Name transfer in government tax books after a sale, gift, or inheritance."
    },
    {
        "term": "Sanad",
        "aliases": ["Sanad-e-Malkiyat", "सनद", "سند"],
        "origin": "Arabic / Persian",
        "category": "Royal / Sovereign Grant",
        "meaning": "A deed of grant, charter, patent, or royal diploma issued by a sovereign, Maharaja, or British Governor-General conferring title, privilege, or tax exemption.",
        "modern_significance": "Primary evidentiary document of crown grant or root of title.",
        "citizen_summary": "Official government or royal deed granting land rights to an individual or family."
    },
    {
        "term": "Haq-Dar",
        "aliases": ["Haqdar", "हक़दार", "حقدار"],
        "origin": "Persian",
        "category": "Legal Entitlement",
        "meaning": "The legitimate holder of a legal right, share, or interest in an ancestral property.",
        "modern_significance": "Rightful Owner / Title Holder.",
        "citizen_summary": "Legitimate legal owner entitled to the property."
    },
    {
        "term": "Girvi",
        "aliases": ["Rahan", "Rehan", "गिरवी", "रहन", "رہن"],
        "origin": "Hindi / Persian",
        "category": "Encumbrance / Mortgage",
        "meaning": "Pledge or mortgage of property as collateral security for a debt or loan.",
        "modern_significance": "Mortgage under Section 58 of the Transfer of Property Act, 1882.",
        "citizen_summary": "Mortgage: Property was pledged as security for an unpaid loan."
    },
    {
        "term": "Kabza",
        "aliases": ["Qabza", "Qabzah", "क़ब्ज़ा", "कब्जा", "قبضہ"],
        "origin": "Arabic / Persian",
        "category": "Possession",
        "meaning": "Physical and de facto control or possession over a land parcel or dwelling.",
        "modern_significance": "Possession under Specific Relief Act 1963 and Limitation Act 1963 (Adverse Possession).",
        "citizen_summary": "Actual physical occupation and control of the land."
    },
    {
        "term": "Chauhaddi",
        "aliases": ["Chardivari", "Hadd-o-Khalf", "चौहद्दी", "چوہدی"],
        "origin": "Hindi / Persian",
        "category": "Boundary Demarcation",
        "meaning": "The four physical boundaries (North, South, East, West) describing adjacent lands, roads, or owners.",
        "modern_significance": "Boundary schedule in a conveyance deed. In Indian law, 'boundaries prevail over survey numbers' in case of conflict.",
        "citizen_summary": "The 4 boundary walls/neighbors (East, West, North, South) outlining the land."
    },
    {
        "term": "Shajra",
        "aliases": ["Shajra Kishtwar", "Shajra Nasab", "शजरा", "شجرہ"],
        "origin": "Arabic / Persian",
        "category": "Map & Pedigree",
        "meaning": "Either the village cadastral map showing field boundaries ('Shajra Kishtwar') or ancestral genealogical pedigree tree ('Shajra Nasab').",
        "modern_significance": "Cadastral village survey map and family tree used in succession disputes.",
        "citizen_summary": "Official map of the village plots or the family tree determining heirs."
    },
    {
        "term": "Taqseem",
        "aliases": ["Taqseemnama", "Batwara", "तक़सीम", "بٹوارہ", "تقسیم"],
        "origin": "Arabic / Persian",
        "category": "Partition Deed",
        "meaning": "Formal partition or division of joint family property among co-sharers and legal heirs.",
        "modern_significance": "Partition Deed / Decree under the Hindu Succession Act or Partition Act.",
        "citizen_summary": "Family division agreement dividing land between brothers/heirs."
    },
    {
        "term": "Wasiyatnama",
        "aliases": ["Wasiyat", "वसीयतनामा", "वसीयत", "وصیت نامہ"],
        "origin": "Arabic / Persian",
        "category": "Testamentary Succession",
        "meaning": "Last will and testament written by a deceased landholder dictating succession of property.",
        "modern_significance": "Will under the Indian Succession Act, 1925.",
        "citizen_summary": "Will: Legal testament declaring who inherits after death."
    },
    {
        "term": "Mukhtarnama",
        "aliases": ["Mukhtar-e-Aam", "Mukhtar-e-Khas", "मुख़्तारनामा", "مختار نامہ"],
        "origin": "Persian",
        "category": "Agency / Authority",
        "meaning": "Power of attorney. 'Aam' is General Power of Attorney (GPA); 'Khas' is Special Power of Attorney (SPA).",
        "modern_significance": "Power of Attorney under Powers of Attorney Act, 1882.",
        "citizen_summary": "Power of Attorney giving someone legal permission to act or sell on your behalf."
    },
    {
        "term": "Waris",
        "aliases": ["Waris-e-Haqqi", "वारिस", "وارث"],
        "origin": "Arabic / Persian",
        "category": "Inheritance",
        "meaning": "Legal heir entitled by blood, marriage, or law to inherit ancestral estate.",
        "modern_significance": "Legal Heir / Successor-in-interest.",
        "citizen_summary": "Natural legal heir entitled to ancestral land."
    },
    {
        "term": "Ghair-Mawroosi",
        "aliases": ["Gair Maroosi", "ग़ैर-मौरूसी", "غیر موروثی"],
        "origin": "Persian",
        "category": "Tenancy",
        "meaning": "Tenant-at-will or temporary tenant without hereditary cultivation rights.",
        "modern_significance": "Non-occupancy tenant with no perpetual title.",
        "citizen_summary": "Temporary tenant who does NOT have permanent ownership rights."
    },

    # ── Marathi / Modi Script Revenue & Historical Terms (17th–mid-20th C.) ──
    {
        "term": "Vatan",
        "aliases": ["Watan", "वतन"],
        "origin": "Marathi / Arabic",
        "category": "Hereditary Office & Land Grant",
        "meaning": "Hereditary estate, land grant, or village office held in perpetuity by a family in exchange for administrative or artisanal services.",
        "modern_significance": "Subject to Bombay Inferior Village Watans Abolition Act and State Inam Abolition Acts.",
        "citizen_summary": "Hereditary land grant given centuries ago for serving the village or kingdom."
    },
    {
        "term": "Watandar",
        "aliases": ["Watandars", "वतनदार"],
        "origin": "Marathi / Persian",
        "category": "Hereditary Titleholder",
        "meaning": "The holder of a Vatan estate or hereditary village office (e.g. Patil, Kulkarni, Deshmukh).",
        "modern_significance": "Historical grant holder whose rights were regularized into modern occupancy rights.",
        "citizen_summary": "Person holding hereditary grant rights over the village lands."
    },
    {
        "term": "Inam",
        "aliases": ["Inamdar", "Inam Land", "इनाम", "इनामदार"],
        "origin": "Arabic (via Marathi/Kannada)",
        "category": "Tax-Free Sovereign Grant",
        "meaning": "Land granted tax-free or with favorable quit-rent (Jodi) by Maratha Peshwas, Sultans, or the British for distinguished service or religious endowment (Devasthan).",
        "modern_significance": "Abolished under Inam Abolition Acts, converting holders into modern occupants (Bhogvatdar Class I/II).",
        "citizen_summary": "Tax-exempt gift land granted by historical kings/rulers."
    },
    {
        "term": "Mirasi",
        "aliases": ["Mirasdar", "मिरास", "मिरासदार"],
        "origin": "Arabic / Marathi",
        "category": "Permanent Hereditary Ownership",
        "meaning": "A hereditary landowner in Maharashtra who possessed full proprietary rights, could sell or mortgage, and could never be dispossessed so long as land revenue was paid.",
        "modern_significance": "Highest form of historical private property ownership in Western India.",
        "citizen_summary": "Full private owner with permanent rights to sell or pass down land."
    },
    {
        "term": "Upari",
        "aliases": ["Upri", "उपरी"],
        "origin": "Marathi",
        "category": "Tenant-at-Will",
        "meaning": "A stranger or tenant cultivating village land without hereditary tenure; tenant-at-will on state or Mirasi land.",
        "modern_significance": "Tenant protected under Tenancy and Agricultural Lands Acts (Kul Kaida).",
        "citizen_summary": "Tenant farmer with temporary cultivation permission, not an owner."
    },
    {
        "term": "Ferfar",
        "aliases": ["Hakka Nond", "फेरफार", "हक्क नोंद"],
        "origin": "Marathi",
        "category": "Mutation Entry",
        "meaning": "Village Form VI register entry recording changes in land rights, sales, partitions, heirships, or bank encumbrances.",
        "modern_significance": "Mutation register entry in Maharashtra Land Revenue Code (V.F. 6).",
        "citizen_summary": "Official government entry recording a transfer or inheritance on the 7/12 extract."
    },
    {
        "term": "Satbara",
        "aliases": ["7/12", "7/12 Extract", "सातबारा"],
        "origin": "Marathi",
        "category": "Record of Rights (RoR)",
        "meaning": "Village Form VII (ownership & rights) + Form XII (agricultural crops & tenancy) combined extract in Maharashtra and Gujarat.",
        "modern_significance": "Primary revenue document evidencing occupancy and possession of agricultural land.",
        "citizen_summary": "The vital 7/12 land document showing who owns the land and what is grown on it."
    },
    {
        "term": "Gatkuli",
        "aliases": ["गटकुळी"],
        "origin": "Marathi",
        "category": "Relinquished Village Land",
        "meaning": "Land whose original Mirasdar had died out or fled during famine/war, reverting temporarily to village collective administration.",
        "modern_significance": "Government wasteland or re-allotted tenancy land.",
        "citizen_summary": "Abandoned ancestral land that temporarily reverted to village control."
    },

    # ── Kannada / Halegannada Historical & Revenue Terms ──
    {
        "term": "Kadatha",
        "aliases": ["Kadita", "ಕಡತ"],
        "origin": "Kannada",
        "category": "Historical Register / Deed",
        "meaning": "A historical black cloth or palm-leaf register treated with paste and charcoal, used in Mysore Kingdom and Vijayanagara empire for recording land transactions.",
        "modern_significance": "Historical archival deed used as evidence of ancient title.",
        "citizen_summary": "Ancient cloth/palm-leaf register containing historical property deeds."
    },
    {
        "term": "Pahani",
        "aliases": ["RTC", "ಪಹಣಿ"],
        "origin": "Kannada",
        "category": "Record of Rights (RoR)",
        "meaning": "Record of Rights, Tenancy and Crop inspection (RTC) register in Karnataka detailing landholder names, extent, soil type, and tenancy.",
        "modern_significance": "Core statutory land record under Section 128-129 of Karnataka Land Revenue Act, 1964.",
        "citizen_summary": "Karnataka's official RTC document showing who owns the plot."
    },
    {
        "term": "Mulageni",
        "aliases": ["Moola Geni", "ಮೂಲಗೇಣಿ"],
        "origin": "Kannada",
        "category": "Perpetual Hereditary Lease",
        "meaning": "Permanent, perpetual, hereditary tenancy with fixed rent, where the tenant cannot be evicted except for non-payment of rent.",
        "modern_significance": "Perpetual hereditary tenancy recognized under Karnataka Land Reforms Act.",
        "citizen_summary": "Permanent hereditary lease: Tenant can hold the land forever and pass to heirs."
    },
    {
        "term": "Chalageni",
        "aliases": ["Chala Geni", "ಚಾಲಗೇಣಿ"],
        "origin": "Kannada",
        "category": "Temporary Tenancy",
        "meaning": "Terminable tenancy-at-will from year to year without permanent occupancy rights.",
        "modern_significance": "Agricultural tenancy regulated under land reforms.",
        "citizen_summary": "Temporary year-by-year rental agreement with no permanent ownership."
    },
    {
        "term": "Gramatana",
        "aliases": ["Grama Tana", "ಗ್ರಾಮಠಾಣ"],
        "origin": "Kannada",
        "category": "Village Settlement Area",
        "meaning": "Land reserved specifically for residential habitation within the village settlement boundary (Abadi).",
        "modern_significance": "Residential village land exempt from agricultural land revenue conversion rules.",
        "citizen_summary": "Village residential plot meant for building a house, not for farming."
    },
    # ── Eastern Indian (Kaithi / Bihar / Bengal) & Western Revenue Additions ──
    {
        "term": "Khatian",
        "aliases": ["Khatiyan", "खतियान", "খতিয়ান"],
        "origin": "Persian / Hindi",
        "category": "Record of Rights (RoR)",
        "meaning": "Official Cadastral Survey and Settlement Record of Rights (RoR) in Bihar, Jharkhand, and Bengal detailing title holders, plot boundaries, and tenancy status.",
        "modern_significance": "Primary foundational document for establishing ancestral title and chain-of-title in Eastern India.",
        "citizen_summary": "The master government survey document proving who owns what plot in the village."
    },
    {
        "term": "Kewala",
        "aliases": ["Kewalah", "Kaula", "केवाला"],
        "origin": "Perso-Arabic",
        "category": "Conveyance / Title Deed",
        "meaning": "An absolute registered Sale Deed executed for transfer of immovable property in Bihar, Jharkhand, and eastern Uttar Pradesh.",
        "modern_significance": "Equivalent to an absolute Sale Deed under Section 54 of the Transfer of Property Act, 1882.",
        "citizen_summary": "Sale Deed proving full legal purchase and transfer of land ownership."
    },
    {
        "term": "Malguzari",
        "aliases": ["Malguzar", "मालगुज़ारी", "मालगुजारी"],
        "origin": "Persian",
        "category": "Revenue Assessment",
        "meaning": "Land revenue or land rent payable by the landholder/proprietor to the government or state treasury.",
        "modern_significance": "Modern Land Revenue (Lagaan) assessment paid to the state revenue department.",
        "citizen_summary": "Annual government land tax or rent paid on the property."
    },
    {
        "term": "Bakast",
        "aliases": ["Bakashat", "Bakasht", "बकाश्त"],
        "origin": "Persian",
        "category": "Tenancy Rights",
        "meaning": "Cultivated land held in direct possession and private cultivation by former Zamindars/proprietors at the time of Zamindari Abolition.",
        "modern_significance": "Recognized as settled raiyati land with permanent heritable occupancy rights under state land reform acts.",
        "citizen_summary": "Land directly farmed by the original owner that became their permanent property after land reforms."
    },
    {
        "term": "Gair Mazarua",
        "aliases": ["Gairmajarua", "Gair-Mazarua", "गैरमजरूआ", "गैर मजरूआ"],
        "origin": "Arabic / Persian",
        "category": "Public / Government Land",
        "meaning": "Uncultivated or non-agricultural land. Divided into 'Aam' (common community land: roads, ponds, cremation grounds) and 'Khas' (state government proprietary waste/forest land).",
        "modern_significance": "Government public land; alienation or private sale is illegal and void ab initio.",
        "citizen_summary": "Government or common village land that cannot be privately sold or bought."
    },
    {
        "term": "Tauzi",
        "aliases": ["Tauzi No", "Touzi", "तौजी"],
        "origin": "Persian",
        "category": "Revenue Unit Identifier",
        "meaning": "Revenue roll account number representing an estate (Mahal) on the Collectorate revenue register in Bengal and Bihar.",
        "modern_significance": "Historical estate identifier vital for tracing root title in British-era land grants.",
        "citizen_summary": "Old British-era revenue estate number used to trace ancient family land holdings."
    },
    {
        "term": "Chakbandi",
        "aliases": ["Chak-Bandi", "चकबंदी"],
        "origin": "Hindi / Persian",
        "category": "Land Consolidation",
        "meaning": "Consolidation of scattered, fragmented agricultural land holdings into compact, rectangular plots (Chaks).",
        "modern_significance": "Updates survey numbers and creates consolidated allotment registers with updated Chauhaddi.",
        "citizen_summary": "Government land consolidation scheme that united scattered tiny plots into one large field."
    },
    {
        "term": "Ferfar",
        "aliases": ["Ferfar Nond", "फेरफार", "फेरफार नोंद"],
        "origin": "Marathi",
        "category": "Property Mutation",
        "meaning": "Mutation register entry under Section 148 of the Maharashtra Land Revenue Code recording title transfers, partitions, or encumbrances.",
        "modern_significance": "Official mutation extract (Village Form VI) required along with the 7/12 extract.",
        "citizen_summary": "Official Maharashtra mutation register entry recording changes in land ownership."
    },
    {
        "term": "Satbara",
        "aliases": ["7/12", "7/12 Extract", "सातबारा", "सातबारा उतारा"],
        "origin": "Marathi",
        "category": "Record of Rights & Crops",
        "meaning": "Village Form VII (Record of Rights, ownership, and liabilities) combined with Form XII (Register of crops and cultivation) in Maharashtra.",
        "modern_significance": "Primary conclusive document of land title and occupancy rights in Maharashtra.",
        "citizen_summary": "The master 7/12 property card showing who owns the land, loans on it, and what crops are grown."
    },
    {
        "term": "Shajra",
        "aliases": ["Shajra Map", "Aks Shajra", "शजरा", "شجرہ"],
        "origin": "Arabic / Persian",
        "category": "Cadastral Village Map",
        "meaning": "Detailed cadastral map of the entire village displaying every field boundary, Khasra number, pathway, canal, and waterbody.",
        "modern_significance": "Primary cadastral boundary map used in boundary disputes and partition suits.",
        "citizen_summary": "The official cloth village map showing every single plot's shape and boundaries."
    }
]

def analyze_archaic_terms(text: str) -> List[Dict[str, Any]]:
    """
    Scans document text for historical Persian, Urdu, Marathi, and Kannada
    revenue terms and extracts their modern legal and citizen-friendly meanings.
    """
    if not text:
        return []

    found_terms = []
    text_lower = text.lower()

    for entry in ARCHAIC_LEGAL_LEXICON:
        matched = False
        all_variants = [entry["term"]] + entry.get("aliases", [])
        
        for variant in all_variants:
            # Word boundary check for ASCII; substring search for Unicode scripts
            is_ascii = all(ord(c) < 128 for c in variant)
            if is_ascii:
                pattern = r'\b' + re.escape(variant.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    matched = True
                    break
            else:
                if variant in text:
                    matched = True
                    break

        if matched:
            found_terms.append({
                "term": entry["term"],
                "origin": entry["origin"],
                "category": entry["category"],
                "meaning": entry["meaning"],
                "modern_significance": entry["modern_significance"],
                "citizen_summary": entry["citizen_summary"]
            })

    return found_terms
