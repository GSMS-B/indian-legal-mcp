import os
import json
import sqlite3
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
EXTRACTED_DATA_DIR = os.path.join(BASE_DIR, "data", "extracted_acts")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "sections.json")
DB_FILE = os.path.join(BASE_DIR, "legal.db")

CORE_ACTS = [
    ('BNS', 'Bharatiya Nyaya Sanhita, 2023', 2023, 'current', None),
    ('BNSS', 'Bharatiya Nagarik Suraksha Sanhita, 2023', 2023, 'current', None),
    ('BSA', 'Bharatiya Sakshya Adhiniyam, 2023', 2023, 'current', None),
    ('IPC', 'Indian Penal Code, 1860', 1860, 'repealed', 'BNS'),
    ('CRPC', 'Code of Criminal Procedure, 1973', 1973, 'repealed', 'BNSS'),
    ('IEA', 'Indian Evidence Act, 1872', 1872, 'repealed', 'BSA'),
    ('COI', 'Constitution of India', 1950, 'current', None),
    ('CPC', 'Code of Civil Procedure, 1908', 1908, 'current', None),
    ('MVA', 'Motor Vehicles Act, 1988', 1988, 'current', None),
    ('NIA', 'Negotiable Instruments Act, 1881', 1881, 'current', None)
]

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'^\[Context:.*?\]\n*', '', text, flags=re.DOTALL)
    return text.strip()

def roman_to_int(s):
    rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    int_val = 0
    s = s.upper()
    try:
        for i in range(len(s)):
            if i > 0 and rom_val[s[i]] > rom_val[s[i - 1]]:
                int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
            else:
                int_val += rom_val[s[i]]
        return str(int_val)
    except KeyError:
        return s

def parse_bns_chapter(chapter_str):
    if not chapter_str:
        return None, None
    if chapter_str.startswith("HAPTER "):
        chapter_str = "C" + chapter_str
    parts = chapter_str.split(' ', 2)
    if len(parts) >= 2 and parts[0].upper() == 'CHAPTER':
        c_num_roman = parts[1]
        c_num = roman_to_int(c_num_roman)
        c_title = parts[2] if len(parts) > 2 else None
        return c_num, c_title
    return chapter_str, None

def load_core_sections():
    normalized_sections = []
    
    file_handlers = {
        'ipc.json': lambda item: {
            'act_code': 'IPC',
            'chapter_number': str(item.get('chapter', '')) if item.get('chapter') is not None else None,
            'chapter_title': item.get('chapter_title'),
            'section_number': str(item.get('Section', '')),
            'section_title': item.get('section_title'),
            'text': clean_text(item.get('section_desc', ''))
        },
        'crpc.json': lambda item: {
            'act_code': 'CRPC',
            'chapter_number': str(item.get('chapter', '')) if item.get('chapter') is not None else None,
            'chapter_title': None,
            'section_number': str(item.get('section', '')),
            'section_title': item.get('section_title'),
            'text': clean_text(item.get('section_desc', ''))
        },
        'iea.json': lambda item: {
            'act_code': 'IEA',
            'chapter_number': str(item.get('chapter', '')) if item.get('chapter') is not None else None,
            'chapter_title': None,
            'section_number': str(item.get('section', '')),
            'section_title': item.get('section_title'),
            'text': clean_text(item.get('section_desc', ''))
        },
        'nia.json': lambda item: {
            'act_code': 'NIA',
            'chapter_number': str(item.get('chapter', '')) if item.get('chapter') is not None else None,
            'chapter_title': None,
            'section_number': str(item.get('section', '')),
            'section_title': item.get('section_title'),
            'text': clean_text(item.get('section_desc', ''))
        },
        'cpc.json': lambda item: {
            'act_code': 'CPC',
            'chapter_number': None,
            'chapter_title': None,
            'section_number': str(item.get('section', '')),
            'section_title': item.get('title'),
            'text': clean_text(item.get('description', ''))
        },
        'MVA.json': lambda item: {
            'act_code': 'MVA',
            'chapter_number': None,
            'chapter_title': None,
            'section_number': str(item.get('section', '')),
            'section_title': item.get('title'),
            'text': clean_text(item.get('description', ''))
        },
        'articles.jsonl': lambda item: {
            'act_code': 'COI',
            'chapter_number': str(item.get('part_number', '')) if item.get('part_number') else None,
            'chapter_title': f"{item.get('part_title', '')} - {item.get('chapter_title', '')}".strip(" -") if item.get('part_title') and item.get('chapter_title') else (item.get('part_title') or item.get('chapter_title')),
            'section_number': str(item.get('article_number', '')),
            'section_title': item.get('article_title'),
            'text': (clean_text(item.get('text', '')) + (f"\n\n[Editorial Notes: {clean_text(item.get('editorial_notes'))}]" if item.get('editorial_notes') else "")).strip()
        },
        'bns_sections.json': lambda item: {
            'act_code': 'BNS',
            'chapter_number': str(item.get('chapter', '')) if item.get('chapter') else None,
            'chapter_title': None,
            'section_number': str(item.get('section_number', '')),
            'section_title': item.get('section_title'),
            'text': clean_text(item.get('text', ''))
        },
        'bnss_sections.json': lambda item: {
            'act_code': 'BNSS',
            'chapter_number': str(item.get('chapter', '')) if item.get('chapter') else None,
            'chapter_title': None,
            'section_number': str(item.get('section_number', '')),
            'section_title': item.get('section_title'),
            'text': clean_text(item.get('text', ''))
        },
        'bsa_sections.json': lambda item: {
            'act_code': 'BSA',
            'chapter_number': str(item.get('chapter', '')) if item.get('chapter') else None,
            'chapter_title': None,
            'section_number': str(item.get('section_number', '')),
            'section_title': item.get('section_title'),
            'text': clean_text(item.get('text', ''))
        }
    }

    # Preamble for Constitution of India
    full_ds_path = os.path.join(RAW_DATA_DIR, "CONSTITUTION_DATASET.json")
    preamble_loaded = False
    if os.path.exists(full_ds_path):
        try:
            with open(full_ds_path, 'r', encoding='utf-8') as pf:
                cdata = json.load(pf)
                p = cdata.get('preamble', {})
                p_text = clean_text(p.get('text', ''))
                if p.get('editorial_notes'):
                    p_text += f"\n\n[Editorial Notes: {clean_text(p.get('editorial_notes'))}]"
                normalized_sections.append({
                    'act_code': 'COI',
                    'chapter_number': '0',
                    'chapter_title': 'Preamble',
                    'section_number': '0',
                    'section_title': 'Preamble',
                    'text': p_text
                })
                preamble_loaded = True
        except Exception as e:
            print(f"Warning: Could not read Preamble from CONSTITUTION_DATASET.json: {e}")

    if not preamble_loaded:
        normalized_sections.append({
            'act_code': 'COI',
            'chapter_number': '0',
            'chapter_title': 'Preamble',
            'section_number': '0',
            'section_title': 'Preamble',
            'text': "WE, THE PEOPLE OF INDIA, having solemnly resolved to constitute India into a SOVEREIGN SOCIALIST SECULAR DEMOCRATIC REPUBLIC and to secure to all its citizens: JUSTICE, social, economic and political; LIBERTY of thought, expression, belief, faith and worship; EQUALITY of status and of opportunity; and to promote among them all FRATERNITY assuring the dignity of the individual and the unity and integrity of the Nation; IN OUR CONSTITUENT ASSEMBLY this twenty-sixth day of November, 1949, do HEREBY ADOPT, ENACT AND GIVE TO OURSELVES THIS CONSTITUTION."
        })

    for filename, handler in file_handlers.items():
        filepath = os.path.join(RAW_DATA_DIR, filename)
        if not os.path.exists(filepath):
            continue
            
        if filename.endswith('.jsonl'):
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    item = json.loads(line)
                    normalized_sections.append(handler(item))
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    normalized_item = handler(item)
                    if normalized_item['act_code'] in ('BNS', 'BNSS', 'BSA'):
                        c_num, c_title = parse_bns_chapter(normalized_item['chapter_number'])
                        normalized_item['chapter_number'] = c_num
                        normalized_item['chapter_title'] = c_title
                    normalized_sections.append(normalized_item)
                    
    return normalized_sections

def load_extracted_acts():
    extracted_acts = []
    extracted_sections = []
    seen_codes = set()
    
    core_filenames = {
        'ipc.json', 'crpc.json', 'iea.json', 'nia.json', 'cpc.json', 'MVA.json',
        'bns_sections.json', 'bnss_sections.json', 'bsa_sections.json',
        'constitution_of_india.json', 'CONSTITUTION_DATASET.json',
        'bns_to_ipc.json', 'bnss_to_crpc.json', 'bsa_to_iea.json',
        'crpc_to_bnss.json', 'iea_to_bsa.json', 'ipc_to_bns.json'
    }
    
    scan_dirs = []
    if os.path.exists(RAW_DATA_DIR):
        scan_dirs.append(RAW_DATA_DIR)
    if os.path.exists(EXTRACTED_DATA_DIR) and EXTRACTED_DATA_DIR != RAW_DATA_DIR:
        scan_dirs.append(EXTRACTED_DATA_DIR)
        
    for sdir in scan_dirs:
        files = sorted([f for f in os.listdir(sdir) if f.endswith('.json') and f not in core_filenames])
        for f in files:
            fpath = os.path.join(sdir, f)
            try:
                with open(fpath, 'r', encoding='utf-8') as jf:
                    d = json.load(jf)
                if not (isinstance(d, dict) and 'act_code' in d and 'sections' in d):
                    continue
                code = d['act_code']
                name = d['act_name']
                year = d.get('year')
                if code not in seen_codes:
                    extracted_acts.append((code, name, year, 'current', None))
                    seen_codes.add(code)
                    for s in d['sections']:
                        extracted_sections.append({
                            'act_code': s['act_code'],
                            'chapter_number': str(s['chapter_number']) if s.get('chapter_number') is not None else None,
                            'chapter_title': s.get('chapter_title'),
                            'section_number': str(s['section_number']),
                            'section_title': s.get('section_title') or '',
                            'text': clean_text(s.get('text', ''))
                        })
            except Exception as e:
                print(f"Warning reading {f}: {e}")
                
    return extracted_acts, extracted_sections

def get_all_acts():
    extracted_acts, _ = load_extracted_acts()
    return CORE_ACTS + extracted_acts

def normalize_data():
    core_sections = load_core_sections()
    extracted_acts, extracted_sections = load_extracted_acts()
    all_sections = core_sections + extracted_sections
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_sections, f, indent=2, ensure_ascii=False)
        
    print(f"Normalized {len(all_sections)} sections across {len(CORE_ACTS) + len(extracted_acts)} acts into {OUTPUT_FILE}.")
    return all_sections

def load_constitution_schedules(conn):
    filepath = os.path.join(RAW_DATA_DIR, "schedules.jsonl")
    if not os.path.exists(filepath):
        return
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS constitution_schedules (
      id              INTEGER PRIMARY KEY AUTOINCREMENT,
      schedule_number TEXT NOT NULL,
      schedule_title  TEXT NOT NULL,
      text            TEXT NOT NULL
    );
    """)
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS constitution_schedules_fts USING fts5(
      schedule_title, text, content='constitution_schedules', content_rowid='id'
    );
    """)
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            cursor.execute("""
                INSERT INTO constitution_schedules (schedule_number, schedule_title, text)
                VALUES (?, ?, ?)
            """, (item.get('schedule_number', ''), item.get('schedule_title', ''), clean_text(item.get('text', ''))))
            
    cursor.execute("""
        INSERT INTO constitution_schedules_fts (rowid, schedule_title, text)
        SELECT id, schedule_title, text FROM constitution_schedules
    """)
    conn.commit()

def load_constitution_appendices(conn):
    filepath = os.path.join(RAW_DATA_DIR, "appendices.jsonl")
    if not os.path.exists(filepath):
        return
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS constitution_appendices (
      id              INTEGER PRIMARY KEY AUTOINCREMENT,
      appendix_number TEXT NOT NULL,
      appendix_title  TEXT NOT NULL,
      text            TEXT NOT NULL
    );
    """)
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS constitution_appendices_fts USING fts5(
      appendix_title, text, content='constitution_appendices', content_rowid='id'
    );
    """)
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            cursor.execute("""
                INSERT INTO constitution_appendices (appendix_number, appendix_title, text)
                VALUES (?, ?, ?)
            """, (item.get('appendix_number', ''), item.get('appendix_title', ''), clean_text(item.get('text', ''))))
            
    cursor.execute("""
        INSERT INTO constitution_appendices_fts (rowid, appendix_title, text)
        SELECT id, appendix_title, text FROM constitution_appendices
    """)
    conn.commit()

def load_section_mappings(conn):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS section_mappings (
      id                INTEGER PRIMARY KEY AUTOINCREMENT,
      mapping_pair      TEXT NOT NULL,
      source_act        TEXT NOT NULL,
      source_section    TEXT NOT NULL,
      source_lookup_key TEXT NOT NULL,
      target_act        TEXT,
      target_section    TEXT,
      target_lookup_key TEXT,
      status            TEXT NOT NULL,
      mapping_statement TEXT NOT NULL,
      source_title      TEXT,
      target_title      TEXT,
      source_chapter    TEXT,
      target_chapter    TEXT
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mappings_lookup ON section_mappings(source_act, source_lookup_key);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mappings_sec ON section_mappings(source_act, source_section);")
    
    mapping_files = [
        ('ipc_to_bns.json', 'IPC_TO_BNS', 'IPC', 'BNS'),
        ('bns_to_ipc.json', 'BNS_TO_IPC', 'BNS', 'IPC'),
        ('crpc_to_bnss.json', 'CRPC_TO_BNSS', 'CRPC', 'BNSS'),
        ('bnss_to_crpc.json', 'BNSS_TO_CRPC', 'BNSS', 'CRPC'),
        ('iea_to_bsa.json', 'IEA_TO_BSA', 'IEA', 'BSA'),
        ('bsa_to_iea.json', 'BSA_TO_IEA', 'BSA', 'IEA')
    ]
    
    act_name_map = {
        'Indian Penal Code, 1860': 'IPC',
        'Bharatiya Nyaya Sanhita, 2023': 'BNS',
        'Code of Criminal Procedure, 1973': 'CRPC',
        'Bharatiya Nagarik Suraksha Sanhita, 2023': 'BNSS',
        'Indian Evidence Act, 1872': 'IEA',
        'Bharatiya Sakshya Adhiniyam, 2023': 'BSA'
    }
    
    mapping_data = []
    for filename, pair, def_src_act, def_tgt_act in mapping_files:
        filepath = os.path.join(RAW_DATA_DIR, filename)
        if not os.path.exists(filepath):
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            items = json.load(f)
            for item in items:
                source = item.get('source') or {}
                target = item.get('target') or {}
                
                src_act = act_name_map.get(source.get('act'), def_src_act)
                tgt_act = act_name_map.get(target.get('act'), def_tgt_act) if target.get('act') else None
                
                src_sec = str(source.get('section', ''))
                src_key = str(item.get('lookup_key', ''))
                tgt_sec = str(target.get('section', '')) if target and target.get('section') is not None else None
                tgt_key = str(target.get('sub_section') or target.get('section') or '') if target else None
                status = item.get('status', '')
                stmt = item.get('mapping_statement', '')
                src_title = source.get('title')
                tgt_title = target.get('title') if target else None
                src_chap = source.get('chapter')
                tgt_chap = target.get('chapter') if target else None
                
                mapping_data.append((
                    pair, src_act, src_sec, src_key, tgt_act, tgt_sec, tgt_key,
                    status, stmt, src_title, tgt_title, src_chap, tgt_chap
                ))
                
    cursor.executemany("""
        INSERT INTO section_mappings (
            mapping_pair, source_act, source_section, source_lookup_key,
            target_act, target_section, target_lookup_key,
            status, mapping_statement, source_title, target_title,
            source_chapter, target_chapter
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, mapping_data)
    conn.commit()

def init_db(sections=None):
    if sections is None:
        sections = normalize_data()
        
    all_acts = get_all_acts()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS sections_fts;")
    cursor.execute("DROP TABLE IF EXISTS sections;")
    cursor.execute("DROP TABLE IF EXISTS acts;")
    cursor.execute("DROP TABLE IF EXISTS constitution_schedules_fts;")
    cursor.execute("DROP TABLE IF EXISTS constitution_schedules;")
    cursor.execute("DROP TABLE IF EXISTS constitution_appendices_fts;")
    cursor.execute("DROP TABLE IF EXISTS constitution_appendices;")
    cursor.execute("DROP TABLE IF EXISTS section_mappings;")
    
    cursor.execute("""
    CREATE TABLE acts (
      act_code    TEXT PRIMARY KEY,
      act_name    TEXT NOT NULL,
      year        INTEGER,
      status      TEXT NOT NULL CHECK(status IN ('current','repealed')),
      replaced_by TEXT
    );
    """)
    
    cursor.execute("""
    CREATE TABLE sections (
      id             INTEGER PRIMARY KEY AUTOINCREMENT,
      act_code       TEXT NOT NULL REFERENCES acts(act_code),
      chapter_number TEXT,
      chapter_title  TEXT,
      section_number TEXT NOT NULL,
      section_title  TEXT,
      text           TEXT NOT NULL,
      UNIQUE(act_code, section_number)
    );
    """)
    
    cursor.execute("CREATE INDEX idx_sections_act ON sections(act_code, section_number);")
    cursor.execute("CREATE INDEX idx_sections_act_only ON sections(act_code);")
    
    cursor.execute("""
    CREATE VIRTUAL TABLE sections_fts USING fts5(
      section_title, text, content='sections', content_rowid='id'
    );
    """)
    
    cursor.executemany("INSERT INTO acts (act_code, act_name, year, status, replaced_by) VALUES (?, ?, ?, ?, ?)", all_acts)
    
    section_data = [
        (s['act_code'], s['chapter_number'], s['chapter_title'], s['section_number'], s['section_title'], s['text'])
        for s in sections
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO sections (act_code, chapter_number, chapter_title, section_number, section_title, text)
        VALUES (?, ?, ?, ?, ?, ?)
    """, section_data)
    
    cursor.execute("""
        INSERT INTO sections_fts (rowid, section_title, text)
        SELECT id, section_title, text FROM sections
    """)
    
    conn.commit()
    print(f"Loaded {len(all_acts)} acts and {len(section_data)} sections into legal.db.")
    
    load_constitution_schedules(conn)
    load_constitution_appendices(conn)
    load_section_mappings(conn)
    
    cursor.execute("PRAGMA optimize;")
    conn.commit()
    conn.close()
    print(f"Database {DB_FILE} fully populated and indexed successfully.")

if __name__ == "__main__":
    sections = normalize_data()
    init_db(sections)
