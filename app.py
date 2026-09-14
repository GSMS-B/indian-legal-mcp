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
import spaces

@spaces.GPU
def _dummy_gpu():
    pass

# Suppress harmless deprecation warnings from underlying libraries (like Starlette)
warnings.filterwarnings("ignore")

DB_FILE = "legal.db"
VALID_ACTS = {"BNS", "BNSS", "BSA", "IPC", "CRPC", "IEA", "COI", "CPC", "MVA", "NIA"}

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
    act_code_upper = act_code.upper()
    if act_code_upper not in VALID_ACTS:
        return False, f"Invalid act_code '{act_code}'. Valid codes are: {', '.join(sorted(VALID_ACTS))}."
    return True, act_code_upper

ACT_DESCRIPTIONS = {
    "BNS": "The primary criminal code of India, replacing the IPC. It defines criminal offenses and their punishments.",
    "BNSS": "The primary procedural law for the administration of criminal justice in India, replacing the CrPC. It outlines procedures for investigation, arrest, and trial.",
    "BSA": "The primary law governing the admissibility of evidence in Indian courts, replacing the Indian Evidence Act.",
    "IPC": "The former primary criminal code of India (repealed and replaced by BNS).",
    "CRPC": "The former procedural law for criminal justice (repealed and replaced by BNSS).",
    "IEA": "The former law governing evidence admissibility (repealed and replaced by BSA).",
    "COI": "The supreme law of India, establishing the framework of fundamental political code, rights, and government structure.",
    "CPC": "The primary procedural law for the administration of civil proceedings in India.",
    "MVA": "The primary law regulating all aspects of road transport vehicles, including traffic rules and vehicle registration.",
    "NIA": "The law regulating Promissory Notes, Bills of Exchange and Cheques (frequently used for dishonour of cheques under Section 138)."
}

def list_acts() -> list:
    """List all available Acts in the database, with metadata and descriptions.
    Use this to see which legal codes are supported or find short codes.
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
        act_code: short code, one of BNS, BNSS, BSA, IPC, CRPC, IEA, COI, CPC, MVA, NIA.
    """
    is_valid, msg_or_code = validate_act(act_code)
    if not is_valid:
        return {"error": msg_or_code}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM acts WHERE act_code = ?", (msg_or_code,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            d = dict(row)
            d["description"] = ACT_DESCRIPTIONS.get(d["act_code"], "")
            return d
        return {"error": f"Act {msg_or_code} not found in database."}
    except Exception as e:
        return {"error": str(e)}

def get_section(act_code: str, section_number: str) -> dict:
    """[AI TOOL ORCHESTRATION INSTRUCTION: Only use this tool AFTER you have found the exact section number via search_keyword, or if the user explicitly provided it.]
    Get the exact text of ONE section (or Constitution article) by its number.
    Use this when someone asks about a specific, known section number,
    e.g. 'what does BNS Section 103 say' or 'show me IPC 302'.

    If the Act is repealed (IPC, CRPC, or IEA), the result includes a note
    that it no longer applies to new cases and names what replaced it.

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
            SELECT chapter_number, chapter_title, section_number, section_title, text 
            FROM sections 
            WHERE act_code = ? AND section_number = ?
        """, (msg_or_code, str(section_number)))
        
        section_row = cursor.fetchone()
        
        if not section_row:
            conn.close()
            return {"error": f"Section {section_number} not found in {msg_or_code}."}
            
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
        act_code: e.g. 'BNS', 'MVA'.
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
    """Get every section within one chapter of an Act, with full text.
    Only meaningful for BNS, BNSS, BSA, IPC, CRPC, IEA.
    For CPC, MVA, and COI, which lack chapter grouping in this dataset,
    it returns a clear message instead of empty data.

    Args:
        act_code: e.g. 'BNS'.
        chapter_number: e.g. '1', '16'.
    """
    is_valid, msg_or_code = validate_act(act_code)
    if not is_valid:
        return {"error": msg_or_code}
        
    if msg_or_code in ["CPC", "MVA", "COI"]: # COI also lacks chapters in this dataset
        return {"message": f"Act {msg_or_code} does not have chapter grouping in this dataset."}
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT chapter_number, chapter_title, section_number, section_title, text 
            FROM sections 
            WHERE act_code = ? AND chapter_number = ?
            ORDER BY id
        """, (msg_or_code, str(chapter_number)))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"error": f"Chapter {chapter_number} not found in {msg_or_code}."}
            
        return {
            "chapter_title": rows[0]["chapter_title"],
            "total_sections_in_chapter": len(rows),
            "sections": [dict(row) for row in rows]
        }
    except Exception as e:
        return {"error": str(e)}

def get_section_range(act_code: str, start_section: str, end_section: str) -> dict:
    """Get all sections between a start and end number (inclusive) with full text.
    Numeric comparison handles letter-suffixed numbers (like '108A').
    If start and end are provided in reverse order, it silently corrects
    them and includes a note in the response.

    Args:
        act_code: e.g. 'BNS'.
        start_section: e.g. '100'.
        end_section: e.g. '110'.
    """
    is_valid, msg_or_code = validate_act(act_code)
    if not is_valid:
        return {"error": msg_or_code}
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Since section numbers contain strings, a purely lexical query from the DB 
        # might not work well for '100' to '110' if there are things like '99A'.
        # However, sections are inserted in order, so filtering by ID between the two sections might be best.
        
        cursor.execute("SELECT id FROM sections WHERE act_code = ? AND section_number = ?", (msg_or_code, str(start_section)))
        start_row = cursor.fetchone()
        
        cursor.execute("SELECT id FROM sections WHERE act_code = ? AND section_number = ?", (msg_or_code, str(end_section)))
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
        act_code: e.g. 'BNS'.
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
            "note": note_msg,
            "current_page": page,
            "total_pages": total_pages,
            "total_sections_in_act": total_sections,
            "has_next_page": page < total_pages,
            "sections": [dict(row) for row in rows]
        }
    except Exception as e:
        return {"error": str(e)}

def search_keyword(query: str, act_code: str | None = None) -> dict:
    """[AI TOOL ORCHESTRATION INSTRUCTION: ALWAYS use this tool FIRST when the specific section number is unknown. Never guess section numbers.]
    Search section titles and text. Exact title matches are ranked #1,
    partial title matches are #2, and body text matches are #3 (via BM25).
    This is exact/near-exact word matching, NOT meaning-based search.

    Args:
        query: search term(s), e.g. 'punishment for murder'.
        act_code: optional -- restrict search to one Act.
    """
    if not query:
        return {"error": "Query is required."}
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # We use bm25 weighting. The columns in sections_fts are:
        # section_title, text.
        # We weight section_title (col 0) at 10.0 and text (col 1) at 1.0
        safe_query = f'"{query}"' if not query.startswith('"') else query
        limit = 15
        
        sql = """
            SELECT s.act_code, s.chapter_number, s.section_number, s.section_title, s.text
            FROM sections_fts fts
            JOIN sections s ON fts.rowid = s.id
            WHERE sections_fts MATCH ?
        """
        params = [safe_query]
        
        if act_code:
            is_valid, msg_or_code = validate_act(act_code)
            if not is_valid:
                conn.close()
                return {"error": msg_or_code}
            sql += " AND s.act_code = ?"
            params.append(msg_or_code)
            
        sql += " ORDER BY (s.section_title COLLATE NOCASE = ?) DESC, (s.section_title LIKE '%' || ? || '%') DESC, bm25(sections_fts, 10.0, 1.0) LIMIT ?"
        params.append(query) # for the exact match clause
        params.append(query) # for the LIKE clause
        params.append(limit + 1)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]
            
        return {
            "returned_matches": len(rows),
            "has_more": has_more,
            "note": "Top results returned based on relevance (title matches ranked 10x higher than body text). Narrow search if has_more is true.",
            "results": [dict(row) for row in rows]
        }
    except Exception as e:
        return {"error": str(e)}



# ---------------------------------------------------------
# MCP RESOURCES
# ---------------------------------------------------------
@resource(uri_template="act_info://{act_code}")
def read_act_metadata(act_code: str) -> str:
    """Resource containing metadata for a specific Indian Legal Act."""
    info = get_act_info(act_code)
    return json.dumps(info, indent=2)

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
    return f"Compare {old_act} Section {old_section} with its modern equivalent in the new 2023 criminal codes (target: {new_act if new_act else 'the relevant new Act'}). Search for the modern equivalent using tools, retrieve both texts, and compare them side-by-side, noting changes in punishment or ingredients."

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

with gr.Blocks(title="Indian Legal MCP") as demo:
    gr.Markdown("""
    # Indian Legal MCP
    Structured access to 10 Indian Acts for AI agents: BNS, BNSS, BSA,
    IPC, CrPC, Indian Evidence Act, Constitution of India, CPC,
    Motor Vehicles Act, Negotiable Instruments Act.

    Not legal advice. Always verify anything that matters against the
    official Gazette (indiacode.nic.in). Historical Acts (IPC, CrPC,
    Evidence Act) are clearly marked as repealed and no longer apply to
    new cases -- they remain useful for matters from before 1 July 2024.
    """)
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
        fn=get_section, 
        inputs=[
            gr.Textbox(label="act_code", info="e.g. BNS, IPC, COI"),
            gr.Textbox(label="section_number", info="e.g. 103, 25A, 0")
        ], 
        outputs="json",
        description=get_section.__doc__,
        title="Get Section"
    )
    
    gr.Interface(
        fn=list_sections, 
        inputs=[gr.Textbox(label="act_code", info="e.g. BNS, MVA")], 
        outputs="json",
        description=list_sections.__doc__,
        title="List Sections"
    )
    
    gr.Interface(
        fn=get_chapter, 
        inputs=[
            gr.Textbox(label="act_code", info="e.g. BNS"),
            gr.Textbox(label="chapter_number", info="e.g. 1, 16")
        ], 
        outputs="json",
        description=get_chapter.__doc__,
        title="Get Chapter"
    )
    
    gr.Interface(
        fn=get_section_range, 
        inputs=[
            gr.Textbox(label="act_code", info="e.g. BNS"),
            gr.Textbox(label="start_section", info="e.g. 100"),
            gr.Textbox(label="end_section", info="e.g. 110")
        ], 
        outputs="json",
        description=get_section_range.__doc__,
        title="Get Section Range"
    )
    
    gr.Interface(
        fn=get_full_act, 
        inputs=[
            gr.Textbox(label="act_code", info="e.g. BNS"),
            gr.Number(label="page", value=1, precision=0, info="Page number (50 sections per page)")
        ], 
        outputs="json",
        description=get_full_act.__doc__,
        title="Get Full Act"
    )
    
    gr.Interface(
        fn=search_keyword, 
        inputs=[
            gr.Textbox(label="query", info="Search term(s), e.g. 'criminal conspiracy'"),
            gr.Textbox(label="act_code", info="(Optional) restrict search to one Act")
        ], 
        outputs="json",
        description=search_keyword.__doc__,
        title="Search Keyword"
    )


    with gr.Accordion("MCP Resources (Metadata)", open=False):
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
