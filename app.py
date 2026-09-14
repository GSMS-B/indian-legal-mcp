import gradio as gr
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
    """Get the exact text of ONE section (or Constitution article) by its number.
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
    """Search section titles and text. Exact title matches are ranked #1,
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

if __name__ == "__main__":
    demo.launch(mcp_server=True)
