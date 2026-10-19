import gradio as gr
try:
    from gradio.mcp import prompt, resource
except ImportError:
    prompt = lambda *args, **kwargs: lambda f: f
    resource = lambda *args, **kwargs: lambda f: f
import sqlite3
import os
import json
import warnings
import math
import re
import spaces

@spaces.GPU
def _dummy_gpu():
    pass

# Suppress harmless deprecation warnings from underlying libraries (like Starlette)
warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "legal.db")
ACT_DESCRIPTIONS = {
    # 10 Core Acts
    "BNS": "The primary criminal code of India, replacing the IPC. It defines criminal offenses and their punishments.",
    "BNSS": "The primary procedural law for the administration of criminal justice in India, replacing the CrPC. It outlines procedures for investigation, arrest, and trial.",
    "BSA": "The primary law governing the admissibility of evidence in Indian courts, replacing the Indian Evidence Act.",
    "IPC": "The former primary criminal code of India (repealed and replaced by BNS).",
    "CRPC": "The former procedural law for criminal justice (repealed and replaced by BNSS).",
    "IEA": "The former law governing evidence admissibility (repealed and replaced by BSA).",
    "COI": "The supreme law of India (2026 edition, incorporating amendments up to the 106th Amendment Act), establishing the framework of fundamental political code, rights, government structure, 12 schedules, and 3 appendices.",
    "CPC": "The primary procedural law for the administration of civil proceedings in India.",
    "MVA": "The primary law regulating all aspects of road transport vehicles, including traffic rules and vehicle registration.",
    "NIA": "The law regulating Promissory Notes, Bills of Exchange and Cheques (frequently used for dishonour of cheques under Section 138).",

    # 92 Added Official Acts (102 Acts Total)
    "AADHAAR": "Statutory framework for targeted delivery of subsidies, benefits and services through unique 12-digit Aadhaar identification numbers and UIDAI.",
    "ACA": "Comprehensive law governing domestic arbitration, international commercial arbitration, enforcement of foreign arbitral awards, and conciliation.",
    "ADVOCATES": "Law relating to legal practitioners, constitution of Bar Councils, admission, enrollment, and professional conduct of advocates.",
    "AIR": "Law for the prevention, control and abatement of air pollution and establishing pollution control boards.",
    "ARMS": "Law consolidating and amending the regulation of firearms, ammunition, licensing, and penalties for illicit arms.",
    "ATA": "Law providing for adjudication of disputes regarding recruitment and conditions of service of public servants.",
    "BRA": "Primary legislation regulating all banking companies in India, detailing RBI licensing, inspection, management, and governance powers.",
    "CA": "Comprehensive statute governing company incorporation, corporate governance, CSR, director duties, audits, mergers, and winding up under NCLT.",
    "CALPRA": "Law prohibiting the engagement of children in all occupations and regulating adolescent working conditions.",
    "CGST": "Comprehensive indirect tax statute levying tax on intra-State supply of goods and services.",
    "CHIT": "Statute regulating chit fund business, agreements, administration, and investor protections.",
    "COMMERCIAL_COURTS": "Statute establishing specialized Commercial Courts, Commercial Appellate Divisions, and fast-track adjudication of commercial disputes.",
    "COMPETITION": "Law prohibiting anti-competitive agreements, abuse of dominant position, regulating combinations, and establishing the CCI.",
    "CONTEMPT_COURTS": "Statute defining and limiting the powers of courts in punishing civil and criminal contempt.",
    "COPYRIGHT": "Comprehensive statute protecting rights of authors, artists, and creators in literary, dramatic, musical, artistic, and cinematographic works.",
    "COW": "Unified code consolidating laws on minimum wages, payment of wages, equal remuneration, and bonus.",
    "CPA": "Consumer rights statute establishing Consumer Disputes Redressal Commissions (District, State, National) and CCPA against unfair trade practices.",
    "CSS": "Unified code amalgamating social security laws concerning EPFO, ESIC, gratuity, maternity benefit, and unorganised workers.",
    "CUSTOMS": "Principal statute governing levy and collection of customs duties, import/export regulations, and anti-smuggling enforcement.",
    "DESIGNS": "Law governing the registration and protection of industrial designs and shape configurations.",
    "DPA": "Strict penal statute prohibiting the giving or taking of dowry in marriage ceremonies.",
    "DPDPA": "Comprehensive data protection statute governing processing of digital personal data, consent, individual rights, and Data Protection Board of India.",
    "DV": "Civil-criminal protective legislation providing emergency protection orders, residence orders, and monetary relief against domestic violence.",
    "EASEMENTS": "Statute defining the law relating to easements, licenses, servitudes, and natural water and light rights.",
    "EPA": "Umbrella legislation for the protection, conservation, and improvement of the environment and handling of hazardous substances.",
    "FCA": "Law establishing specialized Family Courts to promote conciliation and speedy settlement of marital and family disputes.",
    "FEMA": "Statute facilitating external trade, payments, and promoting orderly development and maintenance of foreign exchange markets.",
    "GI": "Statute providing for the registration and enhanced legal protection of geographical indications of goods.",
    "HAMA": "Personal law codifying rules regarding legal adoption of children and maintenance of wives, children, and elderly parents among Hindus.",
    "HMA": "Personal law governing marriage, solemnization, restitution of conjugal rights, judicial separation, and divorce among Hindus.",
    "HSA": "Law codifying intestate succession and property inheritance rights of coparceners, male and female heirs among Hindus.",
    "IBC": "Landmark code consolidating corporate insolvency resolution (CIRP), liquidation, and personal bankruptcy under NCLT/IBBI.",
    "ICA": "Fundamental statute defining principles of contract formation, performance, breach, damages, indemnity, guarantee, bailment, and agency.",
    "IGST": "Tax statute governing levy and collection of tax on inter-State supply of goods and services and imports.",
    "IPA": "Statute defining the nature of partnerships, rights and duties of partners, relations to third parties, and dissolution of firms.",
    "IRC": "Unified labor code consolidating laws on trade unions, conditions of employment, industrial disputes, strikes, and lockouts.",
    "ISA": "General law consolidating intestate and testamentary succession, wills, probates, and letters of administration across communities.",
    "IT_ACT": "Primary cyber law legislation regulating electronic commerce, digital signatures, cyber offenses, electronic evidence, and cyber security.",
    "JJ": "Statute catering to the care, protection, and rehabilitation of children in conflict with law and children in need of care.",
    "LA": "Statute prescribing periods of limitation for suits, appeals, and applications in courts, and barring stale claims.",
    "LSAA": "Law constituting legal services authorities to provide free and competent legal services to weaker sections and organising Lok Adalats.",
    "MWPSC": "Statute providing speedy and inexpensive maintenance tribunals and protection for senior citizens and parents.",
    "NDPS": "Stringent criminal statute prohibiting the manufacture, possession, sale, and trafficking of narcotic drugs and psychotropic substances.",
    "NGT": "Statute establishing the National Green Tribunal for effective and expeditious disposal of cases relating to environmental protection.",
    "OSH": "Unified labor code regulating safety, health, and welfare conditions in factories, mines, docks, and establishments.",
    "PATENTS": "Comprehensive law governing patent grants, patentability criteria, rights of patentee, compulsory licensing, and patent infringement.",
    "PCA": "Anti-corruption criminal legislation penalizing bribery, criminal misconduct, and undue advantages involving public servants.",
    "PCMA": "Legislation prohibiting child marriages, declaring them voidable/void, and punishing promoters and participants.",
    "PCRA": "Penal statute punishing the preaching and practice of 'Untouchability' and enforcement of any disability arising therefrom.",
    "PHRA": "Statute providing for the constitution of the National Human Rights Commission (NHRC), State Commissions, and Human Rights Courts.",
    "PMLA": "Comprehensive anti-money laundering legislation for confiscation of proceeds of crime and prosecution of money laundering offenses.",
    "POCSO": "Specialized child protection criminal statute penalizing sexual assault, sexual harassment, and child pornography with child-friendly judicial procedures.",
    "POSH": "Protective law mandating Internal Complaints Committees (ICC), inquiry mechanisms, and safe workplaces for women.",
    "RBI": "Foundational statutory charter establishing and empowering the Reserve Bank of India to regulate currency, monetary policy, and credit.",
    "RDBA": "Statute establishing Debt Recovery Tribunals (DRT) and DRAT for expeditious recovery of debts due to banks and financial institutions.",
    "REGISTRATION": "Statute governing compulsory and optional registration of documents affecting immovable property and rights.",
    "RERA": "Statute regulating real estate projects, mandating project registration, escrow accounts, consumer protections, and establishing RERA authorities/tribunals.",
    "RFCTLARR": "Statute ensuring fair compensation, mandatory rehabilitation, and transparent land acquisition for public/infrastructure purposes.",
    "RTI": "Landmark transparency statute securing citizen access to information held by public authorities, appointing PIOs and Information Commissions.",
    "SARFAESI": "Statute enabling banks and financial institutions to enforce security interests without court intervention and regulate asset reconstruction.",
    "SCST": "Special penal statute preventing atrocities against SC and ST members, establishing Special Courts and victim rehabilitation.",
    "SGA": "Statute defining the law relating to the contract of sale of goods, conditions, warranties, transfer of property, and unpaid seller remedies.",
    "SMA": "Civil marriage legislation providing a special form of marriage and civil divorce for parties irrespective of religion or faith.",
    "SRA": "Statute governing specific performance of contracts, injunctions, declarations, and recovery of possession of property.",
    "STAMP": "Fiscal statute governing the payment and verification of stamp duties on instruments, deeds, and commercial agreements.",
    "TPA": "Fundamental property legislation regulating sales, mortgages, leases, exchanges, and gifts of immovable property.",
    "TRADEMARKS": "Comprehensive statute governing the registration, protection, and prevention of fraudulent use and infringement of trade marks.",
    "UAPA": "Stringent anti-terrorism and national security statute dealing with unlawful associations, terrorist acts, and designation of individuals as terrorists.",
    "VSA": "Forest conservation statute restricting de-reservation of forests or diversion of forest land for non-forest purposes.",
    "WATER": "Legislation providing for the prevention and control of water pollution and maintaining or restoring the wholesomeness of water.",
    "WPA": "Primary statute providing protection to wild animal, bird, and plant species, establishing national parks, wildlife sanctuaries, and hunting prohibitions.",

    # 21 New Added Acts (Total 102 Acts)
    "DCA": "Principal legislation regulating the import, manufacture, distribution, and sale of drugs and cosmetics in India to ensure safety and quality standards.",
    "EA": "Consolidated statute governing generation, transmission, distribution, trading, and use of electricity, open access, and Regulatory Commissions.",
    "FSSA": "Umbrella food legislation establishing science-based standards for food articles, regulating manufacturing, storage, distribution, and sale under FSSAI.",
    "FCRA": "Statute regulating the acceptance and utilization of foreign contributions or foreign hospitality by individuals and associations to safeguard national interest.",
    "GWA": "Comprehensive law consolidating the law relating to the appointment, declaration, powers, and duties of guardians of minor persons and property.",
    "ITA": "The direct tax code of India (2025 codification), governing taxation of income, assessments, capital gains, corporate tax, TDS, and tax administration.",
    "INSURANCE": "Foundational statute regulating insurance business in India, solvency margins, policyholder protections, investment rules, and insurance councils.",
    "IRDAI": "Statute establishing the Insurance Regulatory and Development Authority to promote, regulate, and ensure orderly growth of insurance and reinsurance businesses.",
    "LLP": "Corporate statute governing the formation, registration, limited liability, governance, partner duties, and winding up of Limited Liability Partnerships.",
    "MHA": "Protective legislation providing mental healthcare and services, protecting rights of persons with mental illness, and establishing Mental Health Review Boards.",
    "MSMED": "Statute promoting the development, enhancement of competitiveness, classification, and resolution of delayed payments to micro, small, and medium enterprises.",
    "MWPRDA": "Protective statute governing maintenance, mahr, dower, and properties of divorced Muslim women and incidental matters.",
    "MWPRMA": "Penal and civil statute declaring talaq-e-biddat (instantaneous triple talaq) void and illegal, punishing perpetrators, and securing subsistence allowance and child custody.",
    "PSSA": "Financial statute designating the Reserve Bank of India to regulate, supervise, and ensure safe and efficient payment and settlement systems in India.",
    "PBPTA": "Anti-corruption statute prohibiting benami property transactions, providing for attachment, adjudication, confiscation of benami properties, and criminal prosecution.",
    "RPA": "Foundational democratic legislation governing qualifications and disqualifications of MPs/MLAs, conduct of elections, corrupt practices, election petitions, and disputes.",
    "RTE": "Constitutional mandate statute providing free and compulsory elementary education to every child of the age of 6 to 14 years in neighborhood schools.",
    "RPWDA": "Rights-based statute giving effect to the UNCRPD, securing equality, accessibility, reservation, and protection against discrimination for persons with disabilities.",
    "SEBI": "Primary securities market statute establishing SEBI to protect the interests of investors in securities and promote the development and regulation of the securities market.",
    "SCRA": "Statute preventing undesirable transactions in securities by regulating stock exchanges, listing of public company securities, contracts, and derivatives.",
    "TELECOM": "Comprehensive reform statute consolidating the law relating to the development, expansion, and operation of telecommunication services, spectrum management, and networks."
}

VALID_ACTS = set(ACT_DESCRIPTIONS.keys())
MAPPABLE_ACTS = {"IPC", "BNS", "CRPC", "BNSS", "IEA", "BSA"}

CONVERSION_TARGET_MAP = {
    "IPC": "BNS",
    "BNS": "IPC",
    "CRPC": "BNSS",
    "BNSS": "CRPC",
    "IEA": "BSA",
    "BSA": "IEA"
}

SCHEDULE_NUM_MAP = {
    '1': 'first', 'first': 'first',
    '2': 'second', 'second': 'second',
    '3': 'third', 'third': 'third',
    '4': 'fourth', 'fourth': 'fourth',
    '5': 'fifth', 'fifth': 'fifth',
    '6': 'sixth', 'sixth': 'sixth',
    '7': 'seventh', 'seventh': 'seventh',
    '8': 'eighth', 'eighth': 'eighth',
    '9': 'ninth', 'ninth': 'ninth',
    '10': 'tenth', 'tenth': 'tenth',
    '11': 'eleventh', 'eleventh': 'eleventh',
    '12': 'twelfth', 'twelfth': 'twelfth'
}

ARABIC_TO_ROMAN = {
    '1': 'I', '2': 'II', '3': 'III', '4': 'IV', '5': 'V',
    '6': 'VI', '7': 'VII', '8': 'VIII', '9': 'IX', '10': 'X',
    '11': 'XI', '12': 'XII', '13': 'XIII', '14': 'XIV', '15': 'XV',
    '16': 'XVI', '17': 'XVII', '18': 'XVIII', '19': 'XIX', '20': 'XX',
    '21': 'XXI', '22': 'XXII', '23': 'XXIII', '24': 'XXIV', '25': 'XXV',
    '26': 'XXVI', '27': 'XXVII', '28': 'XXVIII', '29': 'XXIX', '30': 'XXX',
    '31': 'XXXI', '32': 'XXXII', '33': 'XXXIII', '34': 'XXXIV', '35': 'XXXV'
}
for k, v in list(ARABIC_TO_ROMAN.items()):
    ARABIC_TO_ROMAN[f"{k}A"] = f"{v}A"
    ARABIC_TO_ROMAN[f"{k}B"] = f"{v}B"

ROMAN_TO_ARABIC = {v: k for k, v in ARABIC_TO_ROMAN.items()}
ROMAN_NUM_MAP = ARABIC_TO_ROMAN

def get_db_connection():
    if not os.path.exists(DB_FILE):
        # Fallback to run normalize.py if db is missing.
        import normalize
        sections = normalize.normalize_data()
        normalize.init_db(sections)
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def validate_act(act_code: str):
    if not act_code:
        return False, "Act code is required."
    act_code_upper = act_code.upper().strip()
    if act_code_upper not in VALID_ACTS:
        return False, f"Invalid act_code '{act_code}'. Supported acts: {len(VALID_ACTS)} acts available. Valid codes include: {', '.join(sorted(VALID_ACTS)[:15])}... (call list_acts() to see all)."
    return True, act_code_upper

# ---------------------------------------------------------
# CORE MCP TOOLS
# ---------------------------------------------------------

def list_acts() -> list:
    """List all available Acts in the database, with metadata and descriptions.
    Use this to see which legal codes are supported or find short codes.
    Currently supports 102 official Acts of India.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM acts ORDER BY act_code")
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            d = dict(row)
            d["description"] = ACT_DESCRIPTIONS.get(d["act_code"], "")
            results.append(d)
        return results
    except Exception as e:
        return [{"error": str(e)}]

def get_act_info(act_code: str) -> dict:
    """Get metadata about one specific Act: its full name, year enacted,
    and whether it is still current law or has been repealed and replaced
    by something newer.

    Args:
        act_code: short code, e.g. BNS, BNSS, BSA, IPC, CRPC, IEA, COI, CPC, MVA, NIA, RERA, CA, IBC, RTI, ITA, SEBI, SCRA, etc. (102 Acts supported).
    """
    is_valid, msg_or_code = validate_act(act_code)
    if not is_valid:
        return {"error": msg_or_code}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM acts WHERE act_code = ?", (msg_or_code,))
        row = cursor.fetchone()
        
        if row:
            d = dict(row)
            cursor.execute("SELECT count(*) FROM sections WHERE act_code = ?", (msg_or_code,))
            d["total_sections"] = cursor.fetchone()[0]
            conn.close()
            d["description"] = ACT_DESCRIPTIONS.get(d["act_code"], "")
            return d
        conn.close()
        return {"error": f"Act {msg_or_code} not found in database."}
    except Exception as e:
        return {"error": str(e)}

TOPIC_ACT_MAP = {
    # Environment & Green
    "environment": ["EPA", "NGT", "AIR", "WATER", "WPA", "VSA"],
    "pollution": ["AIR", "WATER", "EPA", "NGT"],
    "air": ["AIR", "EPA"],
    "water": ["WATER", "EPA"],
    "forest": ["VSA", "WPA", "EPA"],
    "wildlife": ["WPA", "VSA"],
    "green tribunal": ["NGT", "EPA"],

    # Family & Matrimonial
    "hindu": ["HMA", "HSA", "HAMA"],
    "marriage": ["HMA", "SMA", "FCA", "PCMA", "MWPRMA"],
    "divorce": ["HMA", "SMA", "FCA", "MWPRDA", "MWPRMA"],
    "muslim": ["MWPRDA", "MWPRMA"],
    "talaq": ["MWPRMA", "MWPRDA"],
    "triple talaq": ["MWPRMA"],
    "adoption": ["HAMA", "JJ"],
    "maintenance": ["HAMA", "MWPSC", "DV", "MWPRDA", "BNSS", "CRPC"],
    "guardian": ["GWA", "HAMA"],
    "ward": ["GWA"],
    "custody": ["GWA", "HAMA", "MWPRMA"],
    "succession": ["HSA", "ISA"],
    "inheritance": ["HSA", "ISA"],
    "will": ["ISA"],
    "probate": ["ISA"],
    "family": ["FCA", "HMA", "HSA", "HAMA", "DV", "MWPRDA", "MWPRMA"],
    "senior citizens": ["MWPSC"],
    "parents": ["MWPSC", "HAMA"],

    # Women & Child Protection
    "women": ["DV", "POSH", "DPA", "BNS", "IPC"],
    "domestic violence": ["DV"],
    "sexual harassment": ["POSH", "BNS", "IPC"],
    "dowry": ["DPA", "BNS", "IPC"],
    "child": ["POCSO", "JJ", "CALPRA", "PCMA"],
    "children": ["POCSO", "JJ", "CALPRA", "PCMA"],
    "pocso": ["POCSO"],
    "juvenile": ["JJ"],
    "child labour": ["CALPRA"],
    "child marriage": ["PCMA"],

    # Corporate, Commercial & Finance
    "company": ["CA", "IBC", "COMMERCIAL_COURTS", "LLP"],
    "companies": ["CA", "IBC", "COMMERCIAL_COURTS", "LLP"],
    "corporate": ["CA", "IBC", "COMMERCIAL_COURTS", "LLP"],
    "director": ["CA"],
    "csr": ["CA"],
    "insolvency": ["IBC", "CA", "RDBA"],
    "bankruptcy": ["IBC", "RDBA"],
    "commercial": ["COMMERCIAL_COURTS", "ACA"],
    "competition": ["COMPETITION"],
    "arbitration": ["ACA"],
    "conciliation": ["ACA"],
    "real estate": ["RERA"],
    "rera": ["RERA"],
    "consumer": ["CPA"],
    "securities": ["SEBI", "SCRA", "CA"],
    "stock exchange": ["SCRA", "SEBI"],
    "shares": ["CA", "SEBI", "SCRA"],
    "insider trading": ["SEBI", "SCRA"],
    "llp": ["LLP", "IPA", "CA"],
    "limited liability partnership": ["LLP"],
    "msme": ["MSMED"],
    "small enterprises": ["MSMED"],
    "insurance": ["INSURANCE", "IRDAI"],
    "irdai": ["IRDAI", "INSURANCE"],

    # Banking & Tax
    "banking": ["BRA", "RBI", "NIA", "SARFAESI", "RDBA", "PSSA"],
    "bank": ["BRA", "RBI", "NIA", "SARFAESI", "RDBA", "PSSA"],
    "cheque": ["NIA"],
    "promissory note": ["NIA"],
    "negotiable": ["NIA"],
    "payment": ["PSSA", "RBI", "NIA"],
    "settlement": ["PSSA"],
    "sarfaesi": ["SARFAESI", "RDBA"],
    "debt recovery": ["RDBA", "SARFAESI"],
    "fema": ["FEMA", "PMLA"],
    "foreign exchange": ["FEMA"],
    "foreign contribution": ["FCRA"],
    "fcra": ["FCRA"],
    "chit fund": ["CHIT"],
    "tax": ["ITA", "CGST", "IGST", "CUSTOMS", "STAMP"],
    "income tax": ["ITA"],
    "direct tax": ["ITA"],
    "gst": ["CGST", "IGST"],
    "customs": ["CUSTOMS"],
    "stamp duty": ["STAMP"],
    "benami": ["PBPTA"],

    # Public Welfare, Health & Education
    "drugs": ["DCA", "NDPS"],
    "cosmetics": ["DCA"],
    "pharmacy": ["DCA"],
    "food": ["FSSA"],
    "food safety": ["FSSA"],
    "fssai": ["FSSA"],
    "electricity": ["EA"],
    "power": ["EA"],
    "mental health": ["MHA"],
    "mental healthcare": ["MHA"],
    "education": ["RTE"],
    "right to education": ["RTE"],
    "disability": ["RPWDA"],
    "disabilities": ["RPWDA"],
    "election": ["RPA", "COI"],
    "elections": ["RPA", "COI"],
    "telecom": ["TELECOM"],
    "telecommunications": ["TELECOM"],

    # Civil, Contract & Property
    "civil": ["CPC", "SRA", "ICA", "LA"],
    "cpc": ["CPC"],
    "contract": ["ICA", "SRA", "SGA"],
    "agreement": ["ICA", "ACA", "SRA"],
    "partnership": ["IPA"],
    "sale of goods": ["SGA"],
    "property": ["TPA", "EASEMENTS", "REGISTRATION", "RERA", "RFCTLARR"],
    "transfer of property": ["TPA"],
    "mortgage": ["TPA", "SARFAESI"],
    "easement": ["EASEMENTS"],
    "registration": ["REGISTRATION"],
    "land acquisition": ["RFCTLARR"],
    "motor vehicle": ["MVA"],
    "accident": ["MVA"],
    "limitation": ["LA"],
    "advocate": ["ADVOCATES"],

    # Labor & Employment
    "labor": ["COW", "CSS", "IRC", "OSH", "CALPRA"],
    "labour": ["COW", "CSS", "IRC", "OSH", "CALPRA"],
    "wages": ["COW"],
    "social security": ["CSS"],
    "epfo": ["CSS"],
    "gratuity": ["CSS"],
    "industrial relations": ["IRC"],
    "occupational safety": ["OSH"],

    # Cyber & Technology
    "cyber": ["IT_ACT", "DPDPA"],
    "data": ["DPDPA", "IT_ACT"],
    "privacy": ["DPDPA", "COI"],
    "personal data": ["DPDPA"],
    "dpdpa": ["DPDPA"],
    "information technology": ["IT_ACT"],
    "aadhaar": ["AADHAAR"],

    # Intellectual Property
    "ip": ["COPYRIGHT", "PATENTS", "TRADEMARKS", "DESIGNS", "GI"],
    "copyright": ["COPYRIGHT"],
    "patent": ["PATENTS"],
    "trademark": ["TRADEMARKS"],
    "design": ["DESIGNS"],
    "geographical indication": ["GI"],

    # Criminal & Public Order
    "criminal": ["BNS", "BNSS", "BSA", "IPC", "CRPC", "IEA"],
    "crime": ["BNS", "BNSS", "BSA", "IPC", "CRPC", "IEA"],
    "penal": ["BNS", "IPC"],
    "bns": ["BNS", "IPC"],
    "bnss": ["BNSS", "CRPC"],
    "bsa": ["BSA", "IEA"],
    "ipc": ["IPC", "BNS"],
    "crpc": ["CRPC", "BNSS"],
    "evidence": ["BSA", "IEA"],
    "murder": ["BNS", "IPC"],
    "bail": ["BNSS", "CRPC"],
    "corruption": ["PCA", "PMLA"],
    "money laundering": ["PMLA", "FEMA"],
    "narcotics": ["NDPS"],
    "terrorism": ["UAPA"],
    "arms": ["ARMS"],

    # Constitution, Rights & Public Administration
    "constitution": ["COI"],
    "fundamental rights": ["COI"],
    "information": ["RTI"],
    "right to information": ["RTI"],
    "rti": ["RTI"],
    "human rights": ["PHRA"],
    "civil rights": ["PCRA"],
    "sc st": ["SCST"],
    "tribunal": ["ATA", "NGT", "RDBA"],
    "contempt of court": ["CONTEMPT_COURTS"],
    "legal services": ["LSAA"]
}

def resolve_act(query: str) -> list:
    """[TOKEN OPTIMIZATION TOOL: Use this instead of list_acts to find act codes for any legal topic or statute name in a tiny, lightweight response.]
    Find the exact act_code(s) for any topic, statute name, or keyword.
    Returns a compact list of matching Acts with their act_code, official name, and enactment year.

    Examples:
        resolve_act('environment') -> [EPA, NGT, AIR, WATER, WPA, VSA]
        resolve_act('hindu') -> [HMA, HSA, HAMA]
        resolve_act('cheque') -> [NIA]
        resolve_act('company') -> [CA, IBC, COMMERCIAL_COURTS]
        resolve_act('marriage') -> [HMA, SMA, FCA, PCMA]
        resolve_act('data protection') -> [DPDPA, IT_ACT]

    Args:
        query: search term, topic, or statute name, e.g. 'environment', 'hindu', 'cheque', 'company', 'tax', 'labor', 'bail'.
    """
    if not query:
        return []
        
    q = str(query).strip().lower()
    q_words = re.findall(r'[a-zA-Z0-9]+', q)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT act_code, act_name, year, status FROM acts")
        all_acts = {row[0]: {"act_code": row[0], "act_name": row[1], "year": row[2], "status": row[3]} for row in cursor.fetchall()}
        conn.close()
    except Exception as e:
        return [{"error": str(e)}]
    
    matched_codes = []
    
    # 1. Direct act_code match
    code_upper = q.upper()
    if code_upper in all_acts:
        matched_codes.append(code_upper)
        
    # 2. Topic taxonomy map match
    for topic_kw, codes in TOPIC_ACT_MAP.items():
        if topic_kw == q or topic_kw in q or any(w == topic_kw for w in q_words):
            for c in codes:
                if c not in matched_codes and c in all_acts:
                    matched_codes.append(c)
                    
    # 3. Search in act_name
    for code, info in all_acts.items():
        if code not in matched_codes:
            name_lower = info["act_name"].lower()
            if q in name_lower or all(w in name_lower for w in q_words if len(w) > 2):
                matched_codes.append(code)
                
    return [all_acts[c] for c in matched_codes[:10]]

def get_section(act_code: str, section_number: str) -> dict:
    """[AI TOOL ORCHESTRATION INSTRUCTION: Only use this tool AFTER you have found the exact section number via search_keyword, or if the user explicitly provided it.]
    Get the exact text of ONE section (or Constitution article) by its number.
    Use this when someone asks about a specific, known section number,
    e.g. 'what does BNS Section 103 say', 'show me IPC 302', or 'what does COI Article 21 say'.

    If the Act is repealed (IPC, CRPC, or IEA), the result includes a note
    that it no longer applies to new cases and names what replaced it.
    For the Constitution of India (COI), section_number='0' retrieves the Preamble.

    Args:
        act_code: e.g. 'BNS', 'IPC', 'COI'.
        section_number: e.g. '103', '25A', '0' (Preamble), '394A'. Always given as a string.
    """
    is_valid, msg_or_code = validate_act(act_code)
    if not is_valid:
        return {"error": msg_or_code}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Fetch section details
        cursor.execute("""
            SELECT act_code, chapter_number, chapter_title, section_number, section_title, text 
            FROM sections 
            WHERE act_code = ? AND section_number = ?
        """, (msg_or_code, str(section_number).strip()))
        
        section_row = cursor.fetchone()
        
        if not section_row:
            conn.close()
            return {"error": f"Section/Article {section_number} not found in {msg_or_code}."}
            
        result = dict(section_row)
        
        # Fetch act status to append note if repealed
        cursor.execute("SELECT status, replaced_by FROM acts WHERE act_code = ?", (msg_or_code,))
        act_row = cursor.fetchone()
        conn.close()
        
        if act_row and act_row['status'] == 'repealed':
            replaced_by = act_row['replaced_by']
            result['note'] = f"This Act is repealed and no longer applies to new cases. It was replaced by {replaced_by}."
            
        return result
    except Exception as e:
        return {"error": str(e)}

def list_sections(act_code: str) -> list[dict]:
    """List every section NUMBER and TITLE in one Act, without the full body text.
    Use this to browse what exists in an Act before deciding which specific
    section or chapter to fetch in full -- much shorter than get_full_act.

    Args:
        act_code: e.g. 'BNS', 'MVA', 'COI'.
    """
    is_valid, msg_or_code = validate_act(act_code)
    if not is_valid:
        return [{"error": msg_or_code}]
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT chapter_number, section_number, section_title 
            FROM sections 
            WHERE act_code = ?
            ORDER BY id
        """, (msg_or_code,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        return [{"error": str(e)}]

def get_chapter(act_code: str, chapter_number: str) -> dict:
    """Get every section within one chapter (or Constitution Part) of an Act, with full text.
    Supports all chaptered Acts in the database (e.g. BNS, BNSS, BSA, IPC, CRPC, IEA, COI, CA, IBC, SEBI, SCRA, ITA, EA, DCA, LLP, MHA, MSMED, etc.).
    You can query by Roman numeral (e.g. 'I', 'III', 'VIA'), Arabic numeral (e.g. '1', '3', '6A'),
    or by chapter title keywords (e.g. 'Fundamental Rights', 'Adjudication', 'Demutualisation').
    For CPC and MVA, which lack chapter grouping in this dataset, it returns an informative message.

    Args:
        act_code: short code, e.g. 'BNS', 'COI', 'SEBI', 'SCRA', 'ITA', 'LLP'.
        chapter_number: chapter/part number or title, e.g. '1', 'I', 'Chapter 4', 'Part III', 'Fundamental Rights'.
    """
    is_valid, msg_or_code = validate_act(act_code)
    if not is_valid:
        return {"error": msg_or_code}
        
    if msg_or_code in ["CPC", "MVA"]:
        return {"message": f"Act {msg_or_code} does not have chapter grouping in this dataset."}
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        chap_raw = str(chapter_number).strip()
        # Clean any "Part " or "Chapter " prefix
        clean_val = re.sub(r'^(Part|Chapter)\s+', '', chap_raw, flags=re.IGNORECASE).strip().rstrip(':.-').strip()
        clean_upper = clean_val.upper()
        
        # Build candidate set for matching
        candidates = {chap_raw, clean_val, clean_upper}
        if clean_upper in ARABIC_TO_ROMAN:
            candidates.add(ARABIC_TO_ROMAN[clean_upper])
        if clean_upper in ROMAN_TO_ARABIC:
            candidates.add(ROMAN_TO_ARABIC[clean_upper])
            
        for c in list(candidates):
            candidates.add(f"CHAPTER {c}")
            candidates.add(f"PART {c}")
            
        # If query is numeric or roman numeral, match ONLY chapter_number to prevent partial vowel matches in titles
        is_num_or_roman = bool(re.match(r'^[0-9]+[A-Z]?$', clean_upper) or re.match(r'^[IVXLCDM]+[A-Z]?$', clean_upper))
        
        placeholders = " OR ".join(["chapter_number = ?"] * len(candidates))
        if is_num_or_roman:
            query_sql = f"""
                SELECT chapter_number, chapter_title, section_number, section_title, text 
                FROM sections 
                WHERE act_code = ? AND (
                    {placeholders}
                )
                ORDER BY id
            """
            params = [msg_or_code] + list(candidates)
        else:
            query_sql = f"""
                SELECT chapter_number, chapter_title, section_number, section_title, text 
                FROM sections 
                WHERE act_code = ? AND (
                    {placeholders} OR 
                    chapter_title LIKE ?
                )
                ORDER BY id
            """
            params = [msg_or_code] + list(candidates) + [f"%{clean_val}%"]
            
        cursor.execute(query_sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"error": f"Chapter/Part '{chapter_number}' not found in {msg_or_code}."}
            
        return {
            "act_code": msg_or_code,
            "chapter_number": rows[0]["chapter_number"],
            "chapter_title": rows[0]["chapter_title"],
            "total_sections_in_chapter": len(rows),
            "sections": [dict(row) for row in rows]
        }
    except Exception as e:
        return {"error": str(e)}

def get_section_range(act_code: str, start_section: str, end_section: str) -> dict:
    """Get all sections between a start and end number (inclusive) with full text.
    If start and end are provided in reverse order, it silently corrects
    them and includes a note in the response.

    Args:
        act_code: e.g. 'BNS', 'COI'.
        start_section: e.g. '100', '12'.
        end_section: e.g. '110', '19'.
    """
    is_valid, msg_or_code = validate_act(act_code)
    if not is_valid:
        return {"error": msg_or_code}
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM sections WHERE act_code = ? AND section_number = ?", (msg_or_code, str(start_section).strip()))
        start_row = cursor.fetchone()
        
        cursor.execute("SELECT id FROM sections WHERE act_code = ? AND section_number = ?", (msg_or_code, str(end_section).strip()))
        end_row = cursor.fetchone()
        
        if not start_row:
            conn.close()
            return {"error": f"Start section {start_section} not found in {msg_or_code}."}
            
        if not end_row:
            conn.close()
            return {"error": f"End section {end_section} not found in {msg_or_code}."}
            
        start_id = start_row['id']
        end_id = end_row['id']
        
        note = None
        if start_id > end_id:
            start_id, end_id = end_id, start_id
            note = "Start section appeared after end section. The range was automatically reversed."
            
        cursor.execute("""
            SELECT chapter_number, chapter_title, section_number, section_title, text 
            FROM sections 
            WHERE act_code = ? AND id >= ? AND id <= ?
            ORDER BY id
        """, (msg_or_code, start_id, end_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = {"sections": [dict(row) for row in rows]}
        if note:
            result["note"] = note
        return result
    except Exception as e:
        return {"error": str(e)}

def get_full_act(act_code: str, page: int = 1) -> dict:
    """Get an entire Act, in full, returned in paginated chunks (50 sections/page).
    Use only when genuinely needing the whole Act. If a page beyond the
    total pages is requested, it gracefully returns empty sections with a note.

    Args:
        act_code: e.g. 'BNS', 'COI'.
        page: The page number to fetch. Default is 1.
    """
    is_valid, msg_or_code = validate_act(act_code)
    if not is_valid:
        return {"error": msg_or_code}
        
    try:
        page = int(page)
        if page < 1:
            page = 1
            
        page_size = 50
        offset = (page - 1) * page_size
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total count for pagination metadata
        cursor.execute("SELECT COUNT(*) as count FROM sections WHERE act_code = ?", (msg_or_code,))
        total_sections = cursor.fetchone()['count']
        total_pages = math.ceil(total_sections / page_size)
        
        if total_pages > 0 and page > total_pages:
            conn.close()
            return {
                "note": f"Limit crossed! You requested page {page}, but {msg_or_code} only has {total_pages} pages.",
                "current_page": page,
                "total_pages": total_pages,
                "total_sections_in_act": total_sections,
                "has_next_page": False,
                "sections": []
            }
        
        cursor.execute("""
            SELECT chapter_number, chapter_title, section_number, section_title, text 
            FROM sections 
            WHERE act_code = ?
            ORDER BY id
            LIMIT ? OFFSET ?
        """, (msg_or_code, page_size, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        if page < total_pages:
            note_msg = f"Because {msg_or_code} is very large, data is returned in pages of {page_size} sections. Call this tool again with page={page + 1} for the next part."
        else:
            note_msg = f"This is the final page of {msg_or_code}."
            
        return {
            "act_code": msg_or_code,
            "note": note_msg,
            "current_page": page,
            "total_pages": total_pages,
            "total_sections_in_act": total_sections,
            "has_next_page": page < total_pages,
            "sections": [dict(row) for row in rows]
        }
    except Exception as e:
        return {"error": str(e)}

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "in", "to", "for", "with", "on", 
    "at", "by", "from", "as", "is", "are", "was", "were", "be", "been", 
    "that", "this", "it", "its", "which", "shall", "under", "any"
}

LEGAL_META = {
    "article", "articles", "section", "sections", "sec", "secs", "art", "arts", "act", "acts"
}

ALL_STOPWORDS = STOPWORDS | LEGAL_META

def search_keyword(query: str, act_code: str | None = None) -> dict:
    """[AI TOOL ORCHESTRATION INSTRUCTION: ALWAYS use this tool FIRST when the specific section number is unknown. Never guess section numbers.]
    Search section titles and text across all 102 Acts (including the 2026 Constitution of India, criminal, civil, commercial, corporate, labor, tax, environmental, public health, and family codes).
    Exact title matches rank #1, partial title matches rank #2, and body text matches rank #3 (via BM25).
    Handles exact phrases, multi-word keywords, section citations (e.g. 'Article 21: Life & Liberty'), and punctuation gracefully.
    If filtered by an Act that has no matching provisions, dynamically detects and suggests
    other Acts in the database where relevant provisions exist.

    Args:
        query: search term(s), e.g. 'punishment for murder', 'freedom of speech', 'anticipatory bail', 'arbitration agreement', 'corporate governance', 'cheque bounce'.
        act_code: optional -- restrict search to one Act (e.g. 'BNS', 'IPC', 'COI', 'CA', 'RERA', 'IBC').
    """
    if not query:
        return {"error": "Query is required."}
        
    query_str = str(query).strip()
    
    # 1. Check if query specifies a section/article number explicitly
    # Examples: "Article 21: Life & Liberty", "Section 302", "Sec 438", "Art. 19", "302"
    sec_num_match = re.search(r'\b(?:article|section|sec|art)\b[\s.:#]*([0-9]+[a-zA-Z]*)', query_str, re.IGNORECASE)
    extracted_sec_num = sec_num_match.group(1) if sec_num_match else None
    
    # If the entire query is just a section number (e.g. "302", "21A")
    if not extracted_sec_num and re.match(r'^[0-9]+[a-zA-Z]*$', query_str):
        extracted_sec_num = query_str

    # Extract alphanumeric tokens, stripping unsafe FTS5 operators (: & - ^)
    tokens = re.findall(r'[a-zA-Z0-9]+', query_str)
    if not tokens and not extracted_sec_num:
        return {"returned_matches": 0, "has_more": False, "results": []}

    # Content tokens for FTS: strip stopwords, legal meta (article/section/sec), and any extracted section number
    content_tokens = [
        t for t in tokens 
        if t.lower() not in ALL_STOPWORDS and (not extracted_sec_num or t.lower() != extracted_sec_num.lower())
    ]
    if not content_tokens and not extracted_sec_num:
        content_tokens = [t for t in tokens if t.lower() not in STOPWORDS] or tokens

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        limit = 15

        target_act = None
        if act_code:
            is_valid, msg_or_code = validate_act(act_code)
            if not is_valid:
                conn.close()
                return {"error": msg_or_code}
            target_act = msg_or_code

        is_explicit_phrase = query_str.startswith('"') and query_str.endswith('"') and len(query_str) > 2
        clean_query = query_str.strip('"')

        # Direct section lookup if section number was extracted
        direct_section_rows = []
        if extracted_sec_num:
            if target_act:
                cursor.execute("""
                    SELECT act_code, chapter_number, section_number, section_title, text
                    FROM sections
                    WHERE act_code = ? AND section_number = ?
                """, (target_act, extracted_sec_num))
                direct_section_rows = cursor.fetchall()
            else:
                cursor.execute("""
                    SELECT act_code, chapter_number, section_number, section_title, text
                    FROM sections
                    WHERE section_number = ?
                """, (extracted_sec_num,))
                direct_section_rows = cursor.fetchall()

        base_sql = """
            SELECT s.act_code, s.chapter_number, s.section_number, s.section_title, s.text
            FROM sections_fts fts
            JOIN sections s ON fts.rowid = s.id
            WHERE sections_fts MATCH ?
        """
        order_clause = " ORDER BY (s.section_title COLLATE NOCASE = ?) DESC, (s.section_title LIKE '%' || ? || '%') DESC, bm25(sections_fts, 10.0, 1.0) LIMIT ?"

        def run_fts_query(fts_expr, filter_act, query_limit=limit):
            sql = base_sql
            params = [fts_expr]
            if filter_act:
                sql += " AND s.act_code = ?"
                params.append(filter_act)
            sql += order_clause
            params.append(clean_query)
            params.append(clean_query)
            params.append(query_limit + 1)
            try:
                cursor.execute(sql, params)
                return cursor.fetchall()
            except Exception:
                return []

        fts_rows = []
        if content_tokens:
            # Strict AND match with content tokens (OR search completely removed to prevent false positive matches)
            fts_all = query_str if is_explicit_phrase else ' '.join(f'"{t}"' for t in content_tokens)
            fts_rows = run_fts_query(fts_all, target_act)

        # Combine direct section matches and FTS matches, deduplicating
        seen = set()
        combined_rows = []
        for r in direct_section_rows:
            key = (r["act_code"], r["section_number"])
            if key not in seen:
                seen.add(key)
                combined_rows.append(r)
                
        for r in fts_rows:
            key = (r["act_code"], r["section_number"])
            if key not in seen:
                seen.add(key)
                combined_rows.append(r)

        # Precision Multi-Tier Re-Ranking:
        # Guarantees that:
        # 1. Direct section number query match tops
        # 2. Exact title match (ignoring punctuation & case) ranks #1
        # 3. Title contains the exact query phrase
        # 4. Title contains all content query tokens
        # 5. Body text contains the exact query phrase
        # 6. Preserves SQLite FTS5 BM25 text relevance rank
        clean_q_norm = re.sub(r'[^a-zA-Z0-9\s]', ' ', clean_query).lower()
        clean_q_str = ' '.join(clean_q_norm.split())

        def get_row_sort_key(idx_and_row):
            orig_idx, row = idx_and_row
            is_direct_sec = 1 if (extracted_sec_num and str(row["section_number"]).lower() == str(extracted_sec_num).lower()) else 0
            
            title = row["section_title"] or ""
            clean_t = re.sub(r'[^a-zA-Z0-9\s]', ' ', title).lower()
            clean_t_str = ' '.join(clean_t.split())

            text = row["text"] or ""
            clean_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text).lower()
            clean_text_str = ' '.join(clean_text.split())
            
            # Tier 1: Exact title match ignoring punctuation, capitalization, and trailing hyphens/dots
            is_exact_title = 1 if (clean_q_str and clean_t_str == clean_q_str) else 0
            
            # Tier 2: Title starts with or contains the exact query phrase
            phrase_in_title = 1 if (clean_q_str and re.search(r'\b' + re.escape(clean_q_str) + r'\b', clean_t_str)) else 0
            
            # Tier 3: Count of content query tokens present in title & all tokens present
            tokens_in_title = sum(1 for t in content_tokens if re.search(r'\b' + re.escape(t.lower()) + r'\b', clean_t_str)) if content_tokens else 0
            all_tokens_in_title = 1 if (content_tokens and tokens_in_title == len(content_tokens)) else 0
            
            # Tier 4: Exact query phrase in body text
            phrase_in_text = 1 if (clean_q_str and re.search(r'\b' + re.escape(clean_q_str) + r'\b', clean_text_str)) else 0
            
            return (is_direct_sec, is_exact_title, phrase_in_title, all_tokens_in_title, tokens_in_title, phrase_in_text, -orig_idx)

        combined_rows = [r for _, r in sorted(enumerate(combined_rows), key=get_row_sort_key, reverse=True)]

        # 3. Dynamic Cross-Act Suggestions:
        # If act_code was restricted and 0 matches found in that act, check other Acts in DB dynamically
        cross_act_suggestions = []
        note_msg = "Top results returned based on relevance (exact title matches ranked first, followed by partial title and BM25 text relevance)."

        if not combined_rows and target_act:
            fts_check = ' '.join(f'"{t}"' for t in content_tokens) if content_tokens else None
            other_matches = run_fts_query(fts_check, filter_act=None, query_limit=5) if fts_check else []
            if other_matches:
                cross_act_suggestions = [
                    {"act_code": r["act_code"], "section_number": r["section_number"], "section_title": r["section_title"]}
                    for r in other_matches[:3]
                ]
                suggested_acts = list(dict.fromkeys(r["act_code"] for r in other_matches[:3]))
                note_msg = (
                    f"No provisions found matching '{query_str}' in Act {target_act}. "
                    f"However, matching provisions were found in {', '.join(suggested_acts)} "
                    f"(e.g. {suggested_acts[0]} Section/Article {other_matches[0]['section_number']}: '{other_matches[0]['section_title']}'). "
                    f"Try calling search_keyword without restricting act_code."
                )
            else:
                note_msg = f"No provisions found matching '{query_str}' in Act {target_act}."

        conn.close()

        has_more = len(combined_rows) > limit
        if has_more:
            combined_rows = combined_rows[:limit]

        response = {
            "returned_matches": len(combined_rows),
            "has_more": has_more,
            "note": note_msg,
            "results": [dict(row) for row in combined_rows]
        }
        if cross_act_suggestions:
            response["cross_act_suggestions"] = cross_act_suggestions
        return response
    except Exception as e:
        return {"error": str(e)}

# ---------------------------------------------------------
# NEW: CRIMINAL LAW CONVERSION / MAPPING TOOLS
# ---------------------------------------------------------

def convert_section(act_code: str, section_number: str, include_text: bool = True) -> dict:
    """Map/convert any criminal law section between the old repealed codes (IPC, CrPC, IEA)
    and the new 2023 criminal codes (BNS, BNSS, BSA) in either direction.

    Returns the corresponding section number, amendment status ('Retained', 'Change',
    'Deleted', 'New Section', 'New Sub-Section'), a concise mapping statement,
    and the full statutory text of both sections for instant comparison.

    Examples:
        convert_section('IPC', '302') -> maps to BNS Section 103 (Punishment for murder)
        convert_section('BNS', '103') -> maps to IPC Section 302 + highlights new sub-section 103(2) (Mob Lynching)
        convert_section('CRPC', '437') -> maps to BNSS Section 480 (Non-bailable offence bail)
        convert_section('IEA', '65B') -> maps to BSA Section 63 (Electronic records admissibility)
        convert_section('IPC', '377') -> notes that this section was repealed and deleted in BNS
        convert_section('BNS', '111') -> notes that Organised Crime is a newly introduced provision

    Args:
        act_code: Source Act short code ('IPC', 'BNS', 'CRPC', 'BNSS', 'IEA', or 'BSA').
        section_number: Section number (e.g. '302', '103', '1(1)', '437', '65B').
        include_text: If True (default), includes the exact statutory text of both source and target sections.
    """
    if not act_code:
        return {"error": "Act code is required."}
    
    src_act = act_code.upper().strip()
    if src_act not in MAPPABLE_ACTS:
        return {
            "error": f"Act '{act_code}' is not a criminal code supporting conversions. Mappable codes are: {', '.join(sorted(MAPPABLE_ACTS))}."
        }
        
    sec_str = str(section_number).strip()
    if not sec_str:
        return {"error": "Section number is required."}

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query section_mappings by lookup_key or section number
        cursor.execute("""
            SELECT * FROM section_mappings
            WHERE source_act = ? AND (source_lookup_key = ? OR source_section = ?)
            ORDER BY id
        """, (src_act, sec_str, sec_str))
        
        mappings = cursor.fetchall()
        
        if not mappings:
            conn.close()
            target_act = CONVERSION_TARGET_MAP.get(src_act, "new/old law")
            return {
                "error": f"Section '{section_number}' not found in conversion table for {src_act} to {target_act}."
            }
            
        results = []
        for m in mappings:
            mapping_dict = dict(m)
            item_status = mapping_dict['status']
            stmt = mapping_dict['mapping_statement']
            
            # Build Source Info
            source_info = {
                "act": mapping_dict['source_act'],
                "section": mapping_dict['source_section'],
                "lookup_key": mapping_dict['source_lookup_key'],
                "title": mapping_dict['source_title'],
                "chapter": mapping_dict['source_chapter']
            }
            
            # Build Target Info
            target_info = None
            if mapping_dict['target_act'] and mapping_dict['target_section']:
                target_info = {
                    "act": mapping_dict['target_act'],
                    "section": mapping_dict['target_section'],
                    "lookup_key": mapping_dict['target_lookup_key'],
                    "title": mapping_dict['target_title'],
                    "chapter": mapping_dict['target_chapter']
                }
            
            # Fetch statutory texts if requested
            if include_text:
                # Source text
                cursor.execute("""
                    SELECT text FROM sections 
                    WHERE act_code = ? AND section_number = ?
                """, (source_info['act'], source_info['section']))
                st = cursor.fetchone()
                source_info['text'] = st['text'] if st else ""
                
                # Target text
                if target_info:
                    cursor.execute("""
                        SELECT text FROM sections 
                        WHERE act_code = ? AND section_number = ?
                    """, (target_info['act'], target_info['section']))
                    tt = cursor.fetchone()
                    target_info['text'] = tt['text'] if tt else ""

            results.append({
                "status": item_status,
                "mapping_statement": stmt,
                "source": source_info,
                "target": target_info
            })
            
        conn.close()
        
        return {
            "source_act": src_act,
            "queried_section": sec_str,
            "total_matches": len(results),
            "conversions": results
        }
    except Exception as e:
        return {"error": str(e)}

# ---------------------------------------------------------
# NEW: CONSTITUTION SCHEDULES & APPENDICES TOOLS
# ---------------------------------------------------------

def get_constitution_schedule(schedule_number: str) -> dict:
    """Get the full text and tables of a specific Schedule of the Constitution of India (2026 Edition).
    Covers all 12 Schedules (First to Twelfth Schedule).

    Examples:
        get_constitution_schedule('Seventh') -> Union, State, and Concurrent Lists
        get_constitution_schedule('7') -> Same as 'Seventh'
        get_constitution_schedule('Eighth') -> Languages
        get_constitution_schedule('First') -> States and Union Territories

    Args:
        schedule_number: Schedule name or number (e.g. 'First', '7', 'Seventh', 'Eighth', '10').
    """
    if not schedule_number:
        return {"error": "schedule_number is required (e.g. 'First', '7', 'Seventh')."}
        
    try:
        clean_s = re.sub(r'schedule', '', str(schedule_number).strip(), flags=re.IGNORECASE).strip()
        clean_s = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', clean_s, flags=re.IGNORECASE).strip().lower()
        norm_word = SCHEDULE_NUM_MAP.get(clean_s, clean_s)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT schedule_number, schedule_title, text
            FROM constitution_schedules
            WHERE LOWER(schedule_number) = ? OR LOWER(schedule_number) = ?
        """, (clean_s, norm_word))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return {
            "error": f"Schedule '{schedule_number}' not found. Valid schedules are First through Twelfth (1 to 12)."
        }
    except Exception as e:
        return {"error": str(e)}

def list_constitution_schedules() -> list[dict]:
    """List all 12 Schedules of the Constitution of India with their numbers and titles."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT schedule_number, schedule_title FROM constitution_schedules ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        return [{"error": str(e)}]

def get_constitution_appendix(appendix_number: str) -> dict:
    """Get the full text of an Appendix to the Constitution of India (2026 Edition).
    Covers Appendix I (100th Amendment / Land Boundary Agreement),
    Appendix II (J&K Order 2019 / C.O. 272), and Appendix III (Declaration under Article 370(3) / C.O. 273).

    Args:
        appendix_number: 'I', 'II', 'III', or '1', '2', '3'.
    """
    if not appendix_number:
        return {"error": "appendix_number is required (e.g. 'I', 'II', 'III' or '1', '2', '3')."}
        
    try:
        app_map = {'1': 'i', '2': 'ii', '3': 'iii', 'i': 'i', 'ii': 'ii', 'iii': 'iii'}
        clean_a = str(appendix_number).strip().lower().replace("appendix", "").strip()
        norm_num = app_map.get(clean_a, clean_a)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT appendix_number, appendix_title, text
            FROM constitution_appendices
            WHERE LOWER(appendix_number) = ?
        """, (norm_num,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return {
            "error": f"Appendix '{appendix_number}' not found. Valid appendices are I, II, III (1 to 3)."
        }
    except Exception as e:
        return {"error": str(e)}

def list_constitution_appendices() -> list[dict]:
    """List all 3 Appendices of the Constitution of India with their numbers and titles."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT appendix_number, appendix_title FROM constitution_appendices ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        return [{"error": str(e)}]

# ---------------------------------------------------------
# MCP RESOURCES
# ---------------------------------------------------------

@resource(uri_template="act_info://{act_code}")
def read_act_metadata(act_code: str) -> str:
    """Resource containing metadata for a specific Indian Legal Act."""
    info = get_act_info(act_code)
    return json.dumps(info, indent=2)

@resource(uri_template="constitution://schedule/{schedule_number}")
def read_constitution_schedule_resource(schedule_number: str) -> str:
    """Resource providing the full text of a Constitution Schedule."""
    res = get_constitution_schedule(schedule_number)
    return json.dumps(res, indent=2)

@resource(uri_template="constitution://appendix/{appendix_number}")
def read_constitution_appendix_resource(appendix_number: str) -> str:
    """Resource providing the full text of a Constitution Appendix."""
    res = get_constitution_appendix(appendix_number)
    return json.dumps(res, indent=2)

# ---------------------------------------------------------
# MCP PROMPTS (Flagship Workflows)
# ---------------------------------------------------------

@prompt()
def explain_to_beginner(act_code: str, section_number: str) -> str:
    """Explain a specific legal section using simple, non-legal language for ordinary citizens."""
    return f"Explain {act_code} Section {section_number} step-by-step using simple language suitable for someone with zero legal background. Start with the basic idea, explain the practical meaning, and provide a simple hypothetical example. Use your tools to retrieve the section first."

@prompt()
def explain_legal_terms(act_code: str, section_number: str) -> str:
    """Identify and explain the difficult technical legal terms in a specific section."""
    return f"Identify difficult or technical legal terms in {act_code} Section {section_number}. For every term, provide its meaning in the context of the provision. Use your tools to read the section first."

@prompt()
def preliminary_legal_research(factual_problem: str) -> str:
    """Beginner lawyer workflow: Analyze a factual problem and find the most relevant laws."""
    return f"Analyze this factual problem: '{factual_problem}'. Identify the legal issues, likely relevant Acts, and search terms. Use the search_keyword tool to locate potentially relevant provisions. Return the relevant provisions with a concise explanation of why each is relevant."

@prompt()
def find_relevant_sections(facts: str) -> str:
    """Determine which statutory provisions apply to the given facts."""
    return f"Determine which statutory provisions apply to these facts: '{facts}'. Use keyword searches to find them, retrieve the full text, and present the results ranked by relevance."

@prompt()
def missing_information_checklist(facts: str) -> str:
    """Review incomplete facts and create a checklist of missing information needed for legal analysis."""
    return f"Review these facts: '{facts}'. Identify what legally relevant information is missing that could materially change the applicable provision, defence, or punishment. Do not assume missing facts."

@prompt()
def compare_old_and_new_law(old_act: str, old_section: str, new_act: str = "") -> str:
    """Compare an old repealed law (e.g., IPC) with its modern equivalent (e.g., BNS)."""
    return f"Compare {old_act} Section {old_section} with its modern equivalent in the new 2023 criminal codes (target: {new_act if new_act else 'the relevant new Act'}). Use the convert_section tool to retrieve the exact mapping and side-by-side statutory texts, and explain all material changes in punishment, ingredients, or structure."

@prompt()
def summarize_statutory_changes(legal_issue: str) -> str:
    """Identify material changes between old and new laws concerning a specific issue."""
    return f"Identify the material statutory changes between the old and new provisions concerning: '{legal_issue}'. Focus on additions, removed ingredients, and changed punishments."

@prompt()
def breakdown_legal_ingredients(act_code: str, section_number: str) -> str:
    """Extract and list the constituent legal elements (ingredients) of a section."""
    return f"Analyze {act_code} Section {section_number} and extract its constituent legal elements (required conduct, mental element, exceptions, punishment). Base each element strictly on the text."

@prompt()
def analyze_factual_scenario(scenario: str) -> str:
    """Analyze a user's fact pattern and explain how the law applies."""
    return f"Treat this as a factual scenario requiring statutory research: '{scenario}'. Extract facts, identify issues, search for relevant provisions, and explain how the provisions relate to the facts."

@prompt()
def draft_legal_research_note(issue: str) -> str:
    """Prepare a structured preliminary legal research note for a given issue."""
    return f"Prepare a preliminary legal research note on: '{issue}'. Use the structure: Issue, Relevant Provisions, Statutory Rule, Preliminary Analysis, Potential Counterarguments. Cite Acts and sections."

@prompt()
def draft_lawyer_quick_brief(legal_topic: str) -> str:
    """Produce a concise, lawyer-oriented brief on a specific topic."""
    return f"Produce a concise lawyer-oriented brief on: '{legal_topic}'. Start with relevant section numbers, the rule, essential elements, and practical significance based on statutory text."

@prompt()
def explain_to_client(legal_situation: str) -> str:
    """Convert legal analysis of a situation into a client-friendly explanation."""
    return f"Analyze this situation: '{legal_situation}'. Convert your legal analysis into an explanation suitable for a client with no legal background. Explain what the law says and what it means for them."

@prompt()
def create_law_student_study_note(act_code: str, section_number: str) -> str:
    """Turn a legal provision into a structured study note for exam revision."""
    return f"Turn {act_code} Section {section_number} into a structured study note. Include core rule, ingredients, exceptions, punishment, and one hypothetical example for a law student."

@prompt()
def verify_legal_claim(claim: str) -> str:
    """Evaluate a user's legal claim against the actual statutory corpus to check for accuracy."""
    return f"Evaluate this legal claim: '{claim}'. Identify the relevant Act/section, retrieve the full provision, and classify the claim as supported, partially supported, or unsupported based ONLY on the text."

@prompt()
def trace_concept_across_acts(legal_concept: str) -> str:
    """Trace how a specific legal concept (e.g., 'arrest') is treated across multiple different Acts."""
    return f"Trace the legal concept '{legal_concept}' across the available Indian Acts. Search systematically, group results by Act, and explain how the concept is treated differently."

# ---------------------------------------------------------
# SKILL REGISTRY & RETRIEVAL TOOLS
# ---------------------------------------------------------

SKILLS_DIR = os.path.join(BASE_DIR, "skills")

def list_skills(query: str = "") -> dict:
    """Discover expert legal research procedures and workflows available in the system.
    Returns the skills registry containing domain skill IDs, titles, triggers ('use_when'),
    covered act codes, recommended tool sequences, and reference files.
    
    If query is provided, filters skills by keyword matching against skill ID, title,
    trigger keywords, or act codes.

    Args:
        query: (Optional) Search filter, e.g. 'bail', 'FIR', 'cheque', 'SEBI', 'tax', 'divorce', 'IPR'.
    """
    reg_path = os.path.join(SKILLS_DIR, "registry.json")
    if not os.path.exists(reg_path):
        return {"error": "Skills registry not found on server."}
    with open(reg_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not query:
        return data
    q = query.strip().lower()
    filtered = []
    for s in data.get("skills", []):
        if (q in s["id"].lower() or 
            q in s["title"].lower() or 
            q in s["use_when"].lower() or 
            any(q == c.lower() for c in s.get("act_codes", []))):
            filtered.append(s)
    return {
        "version": data.get("version"),
        "total_matching": len(filtered),
        "skills": filtered
    }

def get_skill(skill_id: str, file: str = "SKILL.md") -> dict:
    """Retrieve procedural instructions and domain reference files for a legal skill.
    Call this tool after checking list_skills to load the exact workflow for a legal domain.
    Use skill_id='_core' to retrieve global legal reasoning, citation, and anti-hallucination rules.

    Args:
        skill_id: The skill identifier (e.g. '_core', 'criminal-law', 'banking-finance-recovery', 'taxation-and-customs', 'corporate-securities-insurance').
        file: Specific file to retrieve (default: 'SKILL.md', or reference files like 'reference/date_rule.md', 'reference/recovery_routes.md').
    """
    clean_id = str(skill_id).strip().replace("/", "").replace("\\", "")
    clean_file = str(file).strip().replace("\\", "/")
    if ".." in clean_file or clean_file.startswith("/"):
        return {"error": "Invalid file path: directory traversal prohibited."}
    target_path = os.path.join(SKILLS_DIR, clean_id, clean_file)
    if not os.path.exists(target_path):
        return {"error": f"Skill file not found: {clean_id}/{clean_file}"}
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {
        "skill_id": clean_id,
        "file": clean_file,
        "content": content
    }

# ---------------------------------------------------------
# GRADIO APPLICATION INTERFACE
# ---------------------------------------------------------

with gr.Blocks(title="Indian Legal MCP") as demo:
    gr.Markdown("""
    # ⚖️ Indian Legal MCP (v3.0)
    Structured, authoritative access to **102 Indian Acts & Codes (12,174 sections)** for AI agents:
    - **Criminal Codes**: Modern 2023 Sanhitas (BNS, BNSS, BSA) & Historical Codes (IPC, CrPC, IEA with bidirectional conversions), NDPS, PMLA, POCSO, UAPA, PCA, Arms Act, Contempt of Courts.
    - **Constitutional & Democratic Governance**: Constitution of India (2026 Edition: Articles 1–395, Preamble, all 12 Schedules, 3 Appendices), Representation of the People Act (RPA), RTI, Human Rights (PHRA), Legal Services (LSAA), Administrative Tribunals (ATA), Advocates Act.
    - **Commercial, Corporate & Securities**: Companies Act (CA), Insolvency & Bankruptcy Code (IBC), SEBI Act, Securities Contracts Regulation (SCRA), LLP Act, MSMED Act, Commercial Courts, Competition Act, Arbitration (ACA), RERA, Consumer Protection (CPA), Partnership (IPA), Sale of Goods (SGA), Chit Funds.
    - **Banking, Finance & Taxation**: Income-tax Act, 2025 (ITA), Banking Regulation (BRA), RBI Act, Negotiable Instruments (NIA), Insurance Act, IRDAI Act, SARFAESI, Debt Recovery (RDBA), FEMA, Foreign Contribution (FCRA), Payment Systems (PSSA), Benami Transactions (PBPTA), GST (CGST, IGST), Customs, Stamp Act.
    - **Civil, Property & Contracts**: CPC, Contract Act (ICA), Specific Relief (SRA), Transfer of Property (TPA), Easements, Registration, Limitation, Land Acquisition (RFCTLARR), Motor Vehicles Act (MVA).
    - **Unified Labor Codes**: Code on Wages (COW), Social Security (CSS), Industrial Relations (IRC), Occupational Safety (OSH), Child Labour Prohibition (CALPRA).
    - **Communications, Cyber & Technology**: Telecommunications Act (TELECOM), Digital Personal Data Protection Act (DPDPA), Information Technology Act (IT_ACT), Aadhaar Act.
    - **Intellectual Property**: Copyright, Patents, Trade Marks, Designs, Geographical Indications.
    - **Family & Personal Laws**: Hindu Marriage/Succession/Adoption (HMA, HSA, HAMA), Special Marriage (SMA), Indian Succession (ISA), Family Courts (FCA), Guardians & Wards (GWA), Muslim Women Protection on Divorce (MWPRDA) & Marriage (MWPRMA).
    - **Environmental & Green Law**: Environment Protection (EPA), National Green Tribunal (NGT), Air Act, Water Act, Wild Life Protection (WPA), Forest Conservation (VSA).
    - **Public Health, Healthcare & Utilities**: Drugs & Cosmetics Act (DCA), Food Safety and Standards (FSSA), Mental Healthcare (MHA), Electricity Act (EA).
    - **Social Protection, Education & Welfare**: Right to Education (RTE), Rights of Persons with Disabilities (RPWDA), Domestic Violence (DV), POSH, POCSO, Dowry Prohibition (DPA), Protection of Civil Rights (PCRA), SC/ST Prevention of Atrocities, Juvenile Justice (JJ), Senior Citizens Welfare (MWPSC).

    *Not legal advice. Always verify anything that matters against the official Gazette (indiacode.nic.in).*
    """)

    with gr.Tab("Core Legal Tools"):
        gr.Interface(
            fn=list_acts, 
            inputs=[], 
            outputs="json",
            description=list_acts.__doc__,
            title="List Acts"
        )
        
        gr.Interface(
            fn=get_act_info, 
            inputs=[gr.Textbox(label="act_code", info="Short code, e.g. BNS, IPC, COI")], 
            outputs="json",
            description=get_act_info.__doc__,
            title="Get Act Info"
        )
        
        gr.Interface(
            fn=resolve_act, 
            inputs=[gr.Textbox(label="query", info="Topic, keyword, or statute name, e.g. 'environment', 'hindu', 'cheque', 'company'")], 
            outputs="json",
            description=resolve_act.__doc__,
            title="Resolve Act Code"
        )
        
        gr.Interface(
            fn=get_section, 
            inputs=[
                gr.Textbox(label="act_code", info="e.g. BNS, IPC, COI"),
                gr.Textbox(label="section_number", info="e.g. 103, 25A, 0 (Preamble), 21")
            ], 
            outputs="json",
            description=get_section.__doc__,
            title="Get Section / Article"
        )
        
        gr.Interface(
            fn=list_sections, 
            inputs=[gr.Textbox(label="act_code", info="e.g. BNS, MVA, COI")], 
            outputs="json",
            description=list_sections.__doc__,
            title="List Sections / Articles"
        )
        
        gr.Interface(
            fn=get_chapter, 
            inputs=[
                gr.Textbox(label="act_code", info="e.g. BNS, IPC, COI"),
                gr.Textbox(label="chapter_number", info="e.g. 1, 16, or for COI: 'III', '3', 'Fundamental Rights'")
            ], 
            outputs="json",
            description=get_chapter.__doc__,
            title="Get Chapter / Constitution Part"
        )
        
        gr.Interface(
            fn=get_section_range, 
            inputs=[
                gr.Textbox(label="act_code", info="e.g. BNS, COI"),
                gr.Textbox(label="start_section", info="e.g. 100, 12"),
                gr.Textbox(label="end_section", info="e.g. 110, 19")
            ], 
            outputs="json",
            description=get_section_range.__doc__,
            title="Get Section Range"
        )
        
        gr.Interface(
            fn=get_full_act, 
            inputs=[
                gr.Textbox(label="act_code", info="e.g. BNS, COI"),
                gr.Number(label="page", value=1, precision=0, info="Page number (50 sections per page)")
            ], 
            outputs="json",
            description=get_full_act.__doc__,
            title="Get Full Act"
        )
        
        gr.Interface(
            fn=search_keyword, 
            inputs=[
                gr.Textbox(label="query", info="Search term(s), e.g. 'punishment for murder', 'freedom of speech'"),
                gr.Textbox(label="act_code", info="(Optional) restrict search to one Act")
            ], 
            outputs="json",
            description=search_keyword.__doc__,
            title="Search Keyword (FTS5 + BM25)"
        )

    with gr.Tab("Criminal Law Conversions (Old ↔ New)"):
        gr.Interface(
            fn=convert_section,
            inputs=[
                gr.Textbox(label="act_code", info="Source Act, e.g. IPC, BNS, CRPC, BNSS, IEA, BSA"),
                gr.Textbox(label="section_number", info="Section number, e.g. 302, 103, 1(1), 437, 65B"),
                gr.Checkbox(label="include_text", value=True, info="Include full statutory text of both sections")
            ],
            outputs="json",
            description=convert_section.__doc__,
            title="Convert Section (Old ↔ New Criminal Laws)"
        )

    with gr.Tab("Constitution Schedules & Appendices (2026 Edition)"):
        gr.Interface(
            fn=get_constitution_schedule,
            inputs=[gr.Textbox(label="schedule_number", info="e.g. First, Seventh, 7, Eighth, 10")],
            outputs="json",
            description=get_constitution_schedule.__doc__,
            title="Get Constitution Schedule"
        )
        gr.Interface(
            fn=list_constitution_schedules,
            inputs=[],
            outputs="json",
            description=list_constitution_schedules.__doc__,
            title="List Constitution Schedules"
        )
        gr.Interface(
            fn=get_constitution_appendix,
            inputs=[gr.Textbox(label="appendix_number", info="e.g. I, II, III or 1, 2, 3")],
            outputs="json",
            description=get_constitution_appendix.__doc__,
            title="Get Constitution Appendix"
        )
        gr.Interface(
            fn=list_constitution_appendices,
            inputs=[],
            outputs="json",
            description=list_constitution_appendices.__doc__,
            title="List Constitution Appendices"
        )

    with gr.Tab("Legal Research Skills & Workflows"):
        gr.Interface(
            fn=list_skills,
            inputs=[gr.Textbox(label="query", info="(Optional) Search filter, e.g. 'bail', 'FIR', 'cheque', 'SEBI', 'tax', 'divorce'")],
            outputs="json",
            description=list_skills.__doc__,
            title="List Skills"
        )
        gr.Interface(
            fn=get_skill,
            inputs=[
                gr.Textbox(label="skill_id", info="e.g. '_core', 'criminal-law', 'banking-finance-recovery', 'taxation-and-customs'"),
                gr.Textbox(label="file", value="SKILL.md", info="File to fetch: 'SKILL.md' or reference file like 'reference/date_rule.md'")
            ],
            outputs="json",
            description=get_skill.__doc__,
            title="Get Skill"
        )

    with gr.Accordion("MCP Resources", open=False):
        gr.Interface(
            fn=read_act_metadata,
            inputs=[gr.Textbox(label="act_code", info="Short code, e.g. BNS")],
            outputs="text",
            description="[Resource] Get metadata for a specific Act.",
            title="Read Act Metadata"
        )
        
    with gr.Accordion("Advanced AI Prompts (Workflows)", open=False):
        gr.Interface(fn=explain_to_beginner, inputs=["text", "text"], outputs="text", title="Explain to Beginner")
        gr.Interface(fn=explain_legal_terms, inputs=["text", "text"], outputs="text", title="Explain Legal Terms")
        gr.Interface(fn=preliminary_legal_research, inputs=["text"], outputs="text", title="Preliminary Legal Research")
        gr.Interface(fn=find_relevant_sections, inputs=["text"], outputs="text", title="Find Relevant Sections")
        gr.Interface(fn=missing_information_checklist, inputs=["text"], outputs="text", title="Missing Info Checklist")
        gr.Interface(fn=compare_old_and_new_law, inputs=["text", "text", "text"], outputs="text", title="Compare Old vs New Law")
        gr.Interface(fn=summarize_statutory_changes, inputs=["text"], outputs="text", title="Summarize Statutory Changes")
        gr.Interface(fn=breakdown_legal_ingredients, inputs=["text", "text"], outputs="text", title="Breakdown Legal Ingredients")
        gr.Interface(fn=analyze_factual_scenario, inputs=["text"], outputs="text", title="Analyze Factual Scenario")
        gr.Interface(fn=draft_legal_research_note, inputs=["text"], outputs="text", title="Draft Legal Research Note")
        gr.Interface(fn=draft_lawyer_quick_brief, inputs=["text"], outputs="text", title="Draft Lawyer Quick Brief")
        gr.Interface(fn=explain_to_client, inputs=["text"], outputs="text", title="Explain to Client")
        gr.Interface(fn=create_law_student_study_note, inputs=["text", "text"], outputs="text", title="Create Law Student Study Note")
        gr.Interface(fn=verify_legal_claim, inputs=["text"], outputs="text", title="Verify Legal Claim")
        gr.Interface(fn=trace_concept_across_acts, inputs=["text"], outputs="text", title="Trace Concept Across Acts")

if __name__ == "__main__":
    demo.launch(mcp_server=True)
