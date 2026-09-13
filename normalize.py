import json
import sqlite3
import os
import re

RAW_DATA_DIR = "data/raw"
OUTPUT_FILE = "data/sections.json"
DB_FILE = "legal.db"

ACTS = [
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
    # Strip the [Context: ...] prefix if it exists
    # It might span multiple lines or have newlines after it
    text = re.sub(r'^\[Context:.*?\]\n*', '', text, flags=re.DOTALL)
    return text.strip()

def normalize_data():
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
            'chapter_title': None, # CrPC raw doesn't have chapter title
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
        'constitution_of_india.json': lambda item: {
            'act_code': 'COI',
            'chapter_number': None,
            'chapter_title': None,
            'section_number': str(item.get('article', '')),
            'section_title': item.get('title'),
            'text': clean_text(item.get('description', ''))
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
            return s # Not a valid roman numeral, return as is

    def parse_bns_chapter(chapter_str):
        if not chapter_str:
            return None, None
        
        # Sometimes "CHAPTER" is misspelled as "HAPTER"
        if chapter_str.startswith("HAPTER "):
            chapter_str = "C" + chapter_str
            
        parts = chapter_str.split(' ', 2)
        if len(parts) >= 2 and parts[0].upper() == 'CHAPTER':
            c_num_roman = parts[1]
            c_num = roman_to_int(c_num_roman)
            c_title = parts[2] if len(parts) > 2 else None
            return c_num, c_title
        return chapter_str, None

    act_counts = {}
    short_or_empty_texts = []

    for filename, handler in file_handlers.items():
        filepath = os.path.join(RAW_DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Warning: File {filename} not found in {RAW_DATA_DIR}")
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            act_code_counts = 0
            for item in data:
                normalized_item = handler(item)
                
                # Further refine BNS chapter parsing
                if normalized_item['act_code'] in ('BNS', 'BNSS', 'BSA'):
                    c_num, c_title = parse_bns_chapter(normalized_item['chapter_number'])
                    normalized_item['chapter_number'] = c_num
                    normalized_item['chapter_title'] = c_title

                text_len = len(normalized_item['text'])
                if text_len < 5:
                    short_or_empty_texts.append(normalized_item)
                    
                normalized_sections.append(normalized_item)
                act_code_counts += 1
                
            act_counts[normalized_item['act_code']] = act_code_counts

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(normalized_sections, f, indent=2, ensure_ascii=False)

    print("--- Normalization Summary ---")
    for act, count in act_counts.items():
        print(f"{act}: {count} sections")
        
    if short_or_empty_texts:
        print("\nWarning: The following sections have empty or very short (<5 chars) text:")
        for item in short_or_empty_texts:
            print(f"  {item['act_code']} - Section {item['section_number']}: '{item['text']}'")
            
    return normalized_sections

def init_db(sections):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
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
    
    cursor.execute("""
    CREATE VIRTUAL TABLE sections_fts USING fts5(
      section_title, text, content='sections', content_rowid='id'
    );
    """)
    
    cursor.executemany("INSERT INTO acts (act_code, act_name, year, status, replaced_by) VALUES (?, ?, ?, ?, ?)", ACTS)
    
    section_data = [
        (s['act_code'], s['chapter_number'], s['chapter_title'], s['section_number'], s['section_title'], s['text'])
        for s in sections
    ]
    
    # We might have duplicates if raw files had duplicates, need to handle or ignore them
    # Given UNIQUE(act_code, section_number), let's use INSERT OR IGNORE
    cursor.executemany("""
        INSERT OR IGNORE INTO sections (act_code, chapter_number, chapter_title, section_number, section_title, text)
        VALUES (?, ?, ?, ?, ?, ?)
    """, section_data)
    
    cursor.execute("""
        INSERT INTO sections_fts (rowid, section_title, text)
        SELECT id, section_title, text FROM sections
    """)
    
    conn.commit()
    conn.close()
    print(f"Database {DB_FILE} created and populated successfully.")

if __name__ == "__main__":
    sections = normalize_data()
    init_db(sections)
