---
title: Indian Legal MCP
emoji: ⚖️
colorFrom: yellow
colorTo: gray
tags:
- mcp
- legal
sdk: gradio
sdk_version: 6.27.0
app_file: app.py
pinned: false
license: mit
---

<div align="center">

<img src="banner.png" alt="Indian Legal MCP banner" width="100%" />

# ⚖️ Indian Legal MCP

**Structured, authoritative access to 81 major Indian legal codes and statutes (~10,000 sections) — built for AI agents.**

![Python 3.10+](https://img.shields.io/badge/python-3.10+-orange.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-orange)](https://huggingface.co/spaces/GSMS-B/indian-legal-mcp)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Ready-gray.svg)](https://modelcontextprotocol.io/)
![Status](https://img.shields.io/badge/status-81%20Acts%20Merged-success.svg)

[Live Server](#-connect-to-the-live-server) • [Tools](#-available-tools) • [Acts Covered](#-acts-covered) • [Credits](#-credits--data-sources) • [License](#-license)

<br>

<img src="poster.png" alt="Indian Legal MCP Poster" width="100%" />

</div>

---

## 📖 What is this?

**Indian Legal MCP** is an enterprise-grade [Model Context Protocol](https://modelcontextprotocol.io/) server that gives AI assistants — Claude, ChatGPT, or any other MCP-compatible client — exact, structured access to the full statutory text of **81 major Indian Acts and Codes (9,901 sections)**, eliminating hallucinations on section numbers, ingredients of offenses, legal definitions, punishments, or repealed historical provisions.

Connect it once, and any AI agent can pull the exact text of a section, browse chapters, execute ranked keyword searches across the full corpus, verify whether a statute is current or repealed, or cross-reference criminal reforms — all sourced directly from official India Code statutes.

> **Disclaimer:** This is not legal advice. Always verify anything that matters against the official Gazette at [indiacode.nic.in](https://www.indiacode.nic.in). Historical Acts (IPC, CrPC, Indian Evidence Act) are clearly marked as repealed in every response — they remain useful for matters predating 1 July 2024, but no longer apply to new cases.

---

## ✨ Features

- **81 major Indian Acts & Codes** in one unified, high-speed queryable database (9,901 sections).
- **2026 Constitution of India Edition** — complete text of 506 Articles (with Constitutional Parts), all 12 Schedules, and 3 Appendices (incorporating amendments up to the 106th Amendment Act).
- **Comprehensive Domain Coverage** — Criminal Law, Corporate & Commercial, Civil Procedure, Arbitration, Banking, Labor Codes, Intellectual Property, Family Law, Environmental Law, Cyber Law & Data Protection (DPDPA), Tax (CGST/IGST), and Human Rights.
- **Bidirectional Criminal Law Conversions** — instant cross-referencing between historical codes (IPC, CrPC, IEA) and modern 2023 codes (BNS, BNSS, BSA) with full side-by-side statutory text and amendment status tags (Retained, Change, Deleted, New Section, New Sub-Section).
- **Token-Efficient Statute Resolution (`resolve_act`)** — intelligent legal taxonomy engine that instantly resolves topics (e.g. "environment", "hindu", "cheque", "marriage", "corporate") to exact Act codes without dumping all 81 acts, saving ~95% of prompt tokens.
- **Robust hybrid keyword search** — exact title matches rank #1, partial title matches rank #2, and body text matches rank #3 (via SQLite FTS5 with BM25), with intelligent query tokenization that gracefully handles citations, non-adjacent keywords, and punctuation.
- **Safe pagination** — large Acts (like Companies Act's 517 sections or BNS's 358 sections) are automatically chunked into manageable pages, preventing AI context window overflow.
- **Historical-law awareness** — every response involving IPC, CrPC, or the Indian Evidence Act automatically flags the Act as repealed and identifies the modern replacement (BNS, BNSS, or BSA).
- **Zero embeddings, sub-millisecond execution** — ultra-fast FTS5 search with indexed lookups, keeping the server lean, responsive (<1ms lookups), and free to host.

---

## 📚 Key Acts Covered (81 Acts Total)

| Domain | Key Statutes & Act Codes |
|---|---|
| **Criminal Law (New 2023 Codes)** | **BNS** (Bharatiya Nyaya Sanhita, 2023), **BNSS** (Bharatiya Nagarik Suraksha Sanhita, 2023), **BSA** (Bharatiya Sakshya Adhiniyam, 2023) |
| **Criminal Law (Historical Codes)** | **IPC** (Indian Penal Code, 1860), **CRPC** (Code of Criminal Procedure, 1973), **IEA** (Indian Evidence Act, 1872) |
| **Constitutional Law** | **COI** (Constitution of India, 2026 Edition: Articles 1–395, Preamble, 12 Schedules, 3 Appendices) |
| **Commercial & Corporate** | **CA** (Companies Act, 2013), **IBC** (Insolvency and Bankruptcy Code, 2016), **COMMERCIAL_COURTS** (Commercial Courts Act, 2015), **COMPETITION** (Competition Act, 2002), **RERA** (Real Estate Act, 2016), **SEBI/SARFAESI** |
| **Civil & Contracts** | **CPC** (Code of Civil Procedure, 1908), **ICA** (Indian Contract Act, 1872), **SRA** (Specific Relief Act, 1963), **ACA** (Arbitration & Conciliation Act, 1996), **TPA** (Transfer of Property Act, 1882), **LA** (Limitation Act, 1963) |
| **Banking & Finance** | **BRA** (Banking Regulation Act, 1949), **RBI** (Reserve Bank of India Act, 1934), **NIA** (Negotiable Instruments Act, 1881), **FEMA** (Foreign Exchange Management Act, 1999), **PMLA** (Prevention of Money Laundering Act, 2002) |
| **Labor Codes** | **COW** (Code on Wages, 2019), **CSS** (Code on Social Security, 2020), **IRC** (Industrial Relations Code, 2020), **OSH** (Occupational Safety, Health and Working Conditions Code, 2020) |
| **Technology & Data** | **DPDPA** (Digital Personal Data Protection Act, 2023), **IT_ACT** (Information Technology Act, 2000), **AADHAAR** (Aadhaar Act, 2016) |
| **Intellectual Property** | **COPYRIGHT** (Copyright Act, 1957), **PATENTS** (Patents Act, 1970), **TRADEMARKS** (Trade Marks Act, 1999), **DESIGNS** (Designs Act, 2000), **GI** (Geographical Indications Act, 1999) |
| **Special & Social Justice** | **POCSO** (Protection of Children from Sexual Offences Act, 2012), **POSH** (Sexual Harassment at Workplace Act, 2013), **DV** (Domestic Violence Act, 2005), **SCST** (Prevention of Atrocities Act, 1989), **RTI** (Right to Information Act, 2005) |

*(Use `list_acts()` to retrieve the complete metadata for all 81 Acts).*

---

## 🛠️ Available Tools

| Tool | What it does |
|---|---|
| `resolve_act(query)` | **Token-Efficient Topic Discovery:** Resolves any legal topic, concept, or statute name into matching act codes (e.g. `'environment'` → `[EPA, NGT, AIR, WATER, WPA, VSA]`, `'hindu'` → `[HMA, HSA, HAMA]`, `'marriage'` → `[HMA, SMA, FCA, PCMA]`, `'company'` → `[CA, IBC, COMMERCIAL_COURTS]`, `'cheque'` → `[NIA]`) without downloading all 81 acts. |
| `list_acts()` | Lists all 81 Acts with full name, year, status, and concise descriptions |
| `get_act_info(act_code)` | Full name, year, and status of any of the 81 Acts |
| `get_section(act_code, section_number)` | Exact statutory text of any section across all 81 Acts (or Constitution article) |
| `list_sections(act_code)` | Every section number + title in an Act, without full text — for browsing |
| `get_chapter(act_code, chapter_number)` | Every section in one chapter (or Constitution Part), in order |
| `get_section_range(act_code, start, end)` | All sections in a numeric range, inclusive |
| `get_full_act(act_code, page?)` | The entire Act, paginated automatically (50 sections/page) |
| `search_keyword(query, act_code?)` | Robust ranked keyword search across all 81 Acts (exact title #1, partial title #2, BM25 #3) |
| `convert_section(act_code, section_number, include_text?)` | Cross-references criminal laws (IPC ↔ BNS, CrPC ↔ BNSS, IEA ↔ BSA) with side-by-side text |
| `get_constitution_schedule(schedule_number)` | Full text and tables of any of the 12 Constitution Schedules (1 to 12) |
| `list_constitution_schedules()` | Numbers and titles of all 12 Constitution Schedules |
| `get_constitution_appendix(appendix_number)` | Full text of any of the 3 Constitution Appendices (I, II, III) |
| `list_constitution_appendices()` | Numbers and titles of all 3 Constitution Appendices |

---

## 🔌 Connect to the live server

**Server URL:**
```
https://gsms-b-indian-legal-mcp.hf.space/gradio_api/mcp/
```

### Claude Desktop

Open **Settings → Developer → Edit Config**, and add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "Indian Legal MCP": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://gsms-b-indian-legal-mcp.hf.space/gradio_api/mcp/"
      ]
    }
  }
}
```

Restart Claude Desktop — the tools will appear under the MCP/tools icon in the chat window.

### Other MCP clients (Cursor, Cline, Windsurf, Claude Code, etc.)

For your MCP client’s setup instructions, use the following server URL:

[https://gsms-b-indian-legal-mcp.hf.space/gradio_api/mcp/](https://gsms-b-indian-legal-mcp.hf.space/gradio_api/mcp/)

---

## 🖥️ Run it yourself / develop locally

```bash
git clone https://github.com/GSMS-B/indian-legal-mcp.git
cd indian-legal-mcp
pip install -r requirements.txt
python normalize.py   # builds legal.db from the raw JSON in data/raw/
python app.py          # starts the Gradio app with MCP enabled
```

The app will print a local URL — open it in a browser to test each tool by hand, or connect a local MCP client to the printed `/gradio_api/mcp/` endpoint.

---

## 🙏 Credits & data sources

This project would not have been possible without the excellent datasets compiled by **[GSMS-B](https://github.com/GSMS-B)** and **[Civictech India](https://github.com/civictech-India)** ("For the People & By the people"):

- **[Indian-Legal-Sections (BNS, BNSS, BSA)](https://huggingface.co/datasets/GSMS-B/indian-legal-sections-bns-bnss-bsa-2023)** — The text for the modern criminal codes (**BNS**, **BNSS**, and **BSA**) was independently compiled and structured for this project by GSMS-B on Hugging Face.
- **[Indian-Law-Penal-Code-Json](https://github.com/civictech-India/Indian-Law-Penal-Code-Json)** — Structured JSON used as the foundational data source for this project's historical Act coverage, including **IPC**, **CRPC**, **IEA**, **CPC**, **MVA**, and **NIA**.
- **[constitution-of-india](https://github.com/civictech-India/constitution-of-india)** — The source dataset used for the **Constitution of India (COI)**.

Huge thanks to Civictech India for making their data freely and openly available. Please check out and star their repositories if you find this project useful.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details. The underlying legal texts themselves are public government documents; the credited source datasets carry their own respective licenses, viewable in their original repositories linked above.

---

<div align="center">

Built by **[GSMS-B](https://github.com/GSMS-B)** · If this project helped you, consider giving it a ⭐

</div>
