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

# ⚖️ Indian Legal MCP Server (v3.0)
### High-Performance Model Context Protocol Server for Indian Law & Jurisprudence

<p align="center">
  <b>Structured, authoritative access to 102 Indian Acts & Codes (12,174 sections) for AI assistants, LLM agents, and legal researchers.</b>
</p>

<!-- Badges -->
[![MCP Version](https://img.shields.io/badge/MCP%20Version-3.0.0-blue.svg?style=for-the-badge&logo=probot)](https://github.com/GSMS-B/indian-legal-mcp)
[![Database Size](https://img.shields.io/badge/Coverage-102%20Acts%20%7C%2012%2C174%20Sections-emerald.svg?style=for-the-badge&logo=sqlite)](https://github.com/GSMS-B/indian-legal-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-amber.svg?style=for-the-badge)](LICENSE)
[![HF Space](https://img.shields.io/badge/%F0%9F%A4%97%20Space-Indian%20Legal%20MCP-red.svg?style=for-the-badge)](https://huggingface.co/spaces/GSMS-B/indian-legal-mcp)
[![FastMCP](https://img.shields.io/badge/Protocol-Streamable%20HTTP%20%2F%20FastMCP-purple.svg?style=for-the-badge)](https://modelcontextprotocol.io/)

<br>

<img src="assets/poster.png" alt="Indian Legal MCP Poster" width="100%" />

</div>

---

## ⚡ Overview

The **Indian Legal MCP Server** connects Claude, ChatGPT, Cursor, and any MCP-compliant autonomous agent directly to India's entire statutory legal system.

Built on SQLite with native **FTS5 full-text indexing**, BM25 ranking, and sub-millisecond retrieval, it provides:
- **102 Complete Indian Acts & Codes** spanning 12,174 statutory sections, articles, schedules, and appendices.
- **Modern 2023 Criminal Reform Sanhitas** (BNS, BNSS, BSA) alongside historical codes (IPC, CrPC, IEA) with **2,629 bidirectional section concordance mappings**.
- **Complete 2026 Constitution of India** (Articles 1–395, Preamble, all 12 Schedules, 3 Appendices) incorporating up to the 106th Amendment.
- **Direct Taxation & Corporate Framework**: Income-tax Act, 2025 (536 sections), Companies Act (517 sections), SEBI Act, SCRA, LLP, MSMED, IBC, and Arbitration.
- **14 Core Legal Tools** + **15 Advanced Prompt Workflows** (Beginner explanations, brief drafting, statutory comparison, and legal claim verification).

---

## 🚀 Quick Start / Client Integration

### Option 1: Remote MCP (Zero Installation)
Connect instantly to the live hosted MCP endpoint without installing Python or cloning code:

```json
{
  "mcpServers": {
    "indian-legal": {
      "type": "streamable-http",
      "url": "https://gsms-b-indian-legal-mcp.hf.space/gradio_api/mcp/"
    }
  }
}
```

### Option 2: Claude Desktop Configuration (`claude_desktop_config.json`)
Add the following entry to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "indian-legal": {
      "command": "python",
      "args": [
        "c:/Users/memor/Videos/Indian-Legal-MCP-new/indian-legal-mcp/app.py"
      ]
    }
  }
}
```

### Option 3: Cursor Integration (`.cursor/mcp.json`)
Add to `.cursor/mcp.json` in your project or global settings:

```json
{
  "mcpServers": {
    "indian-legal": {
      "url": "https://gsms-b-indian-legal-mcp.hf.space/gradio_api/mcp/"
    }
  }
}
```

---

## 🛠️ MCP Tools Reference

| Tool Name | Description | Key Arguments |
|---|---|---|
| `search_keyword` | **[Primary AI Tool]** Ultra-fast FTS5 full-text keyword search across 102 Acts with BM25 ranking. | `query` (str), `act_code` (optional) |
| `resolve_act` | Lightweight topic resolver returning matching act codes and titles. | `query` (str) |
| `get_section` | Fetches exact section/article by number with full headnote and body text. | `act_code` (str), `section_number` (str) |
| `list_acts` | Returns list of all 102 Acts, enactment year, and status. | *(None)* |
| `get_act_info` | Metadata and total section count for a specific Act. | `act_code` (str) |
| `list_sections` | Lightweight index of all section numbers and titles in an Act. | `act_code` (str) |
| `get_chapter` | Retrieves all sections within a chapter or Constitution Part. | `act_code` (str), `chapter_number` (str) |
| `get_section_range` | Fetches contiguous range of sections between start and end. | `act_code` (str), `start_section` (str), `end_section` (str) |
| `get_full_act` | Paginated retrieval of full statutory text (50 sections per page). | `act_code` (str), `page` (int) |
| `convert_section` | Bidirectional cross-walk between old and new criminal laws (e.g. IPC 302 ↔ BNS 103). | `act_code` (str), `section_number` (str), `include_text` (bool) |
| `get_constitution_schedule` | Fetches full text of any Constitution Schedule (First to Twelfth). | `schedule_number` (str) |
| `list_constitution_schedules` | Lists all 12 Constitution schedules and titles. | *(None)* |
| `get_constitution_appendix` | Fetches full text of Constitution Appendices (I, II, III). | `appendix_number` (str) |
| `list_constitution_appendices` | Lists all Constitution appendices. | *(None)* |

---

## 📚 Complete Catalogue of 102 Covered Acts (13 Domains)

| Domain | Code | Official Statute Name | Year | Total Sections |
|---|:---:|---|:---:|:---:|
| **Criminal Law & Penal Statutes** | `ARMS` | Arms Act, 1959 | 1959 | 48 |
|  | `BNS` | Bharatiya Nyaya Sanhita, 2023 | 2023 | 358 |
|  | `BNSS` | Bharatiya Nagarik Suraksha Sanhita, 2023 | 2023 | 531 |
|  | `BSA` | Bharatiya Sakshya Adhiniyam, 2023 | 2023 | 170 |
|  | `CONTEMPT_COURTS` | Contempt of Courts Act, 1971 | 1971 | 24 |
|  | `CRPC` | Code of Criminal Procedure, 1973 | 1973 | 525 |
|  | `DPA` | Dowry Prohibition Act, 1961 | 1961 | 12 |
|  | `IEA` | Indian Evidence Act, 1872 | 1872 | 184 |
|  | `IPC` | Indian Penal Code, 1860 | 1860 | 575 |
|  | `NDPS` | Narcotic Drugs and Psychotropic Substances Act, 1985 | 1985 | 127 |
|  | `PCA` | Prevention of Corruption Act, 1988 | 1988 | 35 |
|  | `PMLA` | Prevention of Money Laundering Act, 2002 | 2002 | 81 |
|  | `POCSO` | Protection of Children from Sexual Offences Act, 2012 | 2012 | 47 |
|  | `UAPA` | Unlawful Activities (Prevention) Act, 1967 | 1967 | 67 |
| **Constitutional Law & Public Administration** | `ADVOCATES` | Advocates Act, 1961 | 1961 | 85 |
|  | `ATA` | Administrative Tribunals Act, 1985 | 1985 | 41 |
|  | `COI` | Constitution of India (2026 Edition) | 1950 | 507 |
|  | `LSAA` | Legal Services Authorities Act, 1987 | 1987 | 38 |
|  | `PCRA` | Protection of Civil Rights Act, 1955 | 1955 | 23 |
|  | `PHRA` | Protection of Human Rights Act, 1993 | 1993 | 45 |
|  | `RPA` | Representation of the People Act, 1951 | 1951 | 196 |
|  | `RTI` | Right to Information Act, 2005 | 2005 | 31 |
|  | `SCST` | Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989 | 1989 | 26 |
| **Commercial, Corporate & Financial Law** | `ACA` | Arbitration and Conciliation Act, 1996 | 1996 | 92 |
|  | `CA` | Companies Act, 2013 | 2013 | 517 |
|  | `CHIT` | Chit Funds Act, 1982 | 1982 | 90 |
|  | `COMMERCIAL_COURTS` | Commercial Courts Act, 2015 | 2015 | 26 |
|  | `COMPETITION` | Competition Act, 2002 | 2002 | 95 |
|  | `CPA` | Consumer Protection Act, 2019 | 2019 | 107 |
|  | `IBC` | Insolvency and Bankruptcy Code, 2016 | 2016 | 281 |
|  | `IPA` | Indian Partnership Act, 1932 | 1932 | 74 |
|  | `LLP` | Limited Liability Partnership Act, 2008 | 2008 | 88 |
|  | `MSMED` | Micro, Small and Medium Enterprises Development Act, 2006 | 2006 | 32 |
|  | `RERA` | Real Estate (Regulation and Development) Act, 2016 | 2016 | 92 |
|  | `SCRA` | Securities Contracts (Regulation) Act, 1956 | 1956 | 78 |
|  | `SEBI` | Securities and Exchange Board of India Act, 1992 | 1992 | 92 |
|  | `SGA` | Sale of Goods Act, 1930 | 1930 | 67 |
| **Banking, Finance & Revenue** | `BRA` | Banking Regulation Act, 1949 | 1949 | 131 |
|  | `CGST` | Central Goods and Services Tax Act, 2017 | 2017 | 190 |
|  | `CUSTOMS` | Customs Act, 1962 | 1962 | 278 |
|  | `FCRA` | Foreign Contribution (Regulation) Act, 2010 | 2010 | 56 |
|  | `FEMA` | Foreign Exchange Management Act, 1999 | 1999 | 52 |
|  | `IGST` | Integrated Goods and Services Tax Act, 2017 | 2017 | 28 |
|  | `INSURANCE` | Insurance Act, 1938 | 1938 | 263 |
|  | `IRDAI` | Insurance Regulatory and Development Authority Act, 1999 | 1999 | 39 |
|  | `ITA` | Income-tax Act, 2025 | 2025 | 536 |
|  | `NIA` | Negotiable Instruments Act, 1881 | 1881 | 156 |
|  | `PBPTA` | Prohibition of Benami Property Transactions Act, 1988 | 1988 | 75 |
|  | `PSSA` | Payment and Settlement Systems Act, 2007 | 2007 | 42 |
|  | `RBI` | Reserve Bank of India Act, 1934 | 1934 | 132 |
|  | `RDBA` | Recovery of Debts and Bankruptcy Act, 1993 | 1993 | 45 |
|  | `SARFAESI` | SARFAESI Act, 2002 | 2002 | 61 |
|  | `STAMP` | Indian Stamp Act, 1899 | 1899 | 97 |
| **Civil Procedure, Contracts & Property** | `CPC` | Code of Civil Procedure, 1908 | 1908 | 171 |
|  | `EASEMENTS` | Indian Easements Act, 1882 | 1882 | 64 |
|  | `ICA` | Indian Contract Act, 1872 | 1872 | 268 |
|  | `LA` | Limitation Act, 1963 | 1963 | 32 |
|  | `MVA` | Motor Vehicles Act, 1988 | 1988 | 256 |
|  | `REGISTRATION` | Registration Act, 1908 | 1908 | 96 |
|  | `RFCTLARR` | Right to Fair Compensation & Transparency in Land Acquisition (RFCTLARR) Act, 2013 | 2013 | 114 |
|  | `SRA` | Specific Relief Act, 1963 | 1963 | 48 |
|  | `TPA` | Transfer of Property Act, 1882 | 1882 | 148 |
| **Unified Labor Codes** | `CALPRA` | Child and Adolescent Labour (Prohibition and Regulation) Act, 1986 | 1986 | 29 |
|  | `COW` | Code on Wages, 2019 | 2019 | 69 |
|  | `CSS` | Code on Social Security, 2020 | 2020 | 164 |
|  | `IRC` | Industrial Relations Code, 2020 | 2020 | 100 |
|  | `OSH` | Occupational Safety, Health and Working Conditions Code, 2020 | 2020 | 143 |
| **Cyber, Technology, Telecom & Identity** | `AADHAAR` | Aadhaar (Targeted Delivery of Financial and Other Subsidies) Act, 2016 | 2016 | 69 |
|  | `DPDPA` | Digital Personal Data Protection Act, 2023 | 2023 | 41 |
|  | `IT_ACT` | Information Technology Act, 2000 | 2000 | 125 |
|  | `TELECOM` | Telecommunications Act, 2023 | 2023 | 62 |
| **Intellectual Property Rights (IPR)** | `COPYRIGHT` | Copyright Act, 1957 | 1957 | 105 |
|  | `DESIGNS` | Designs Act, 2000 | 2000 | 48 |
|  | `GI` | Geographical Indications of Goods (Registration and Protection) Act, 1999 | 1999 | 89 |
|  | `PATENTS` | Patents Act, 1970 | 1970 | 175 |
|  | `TRADEMARKS` | Trade Marks Act, 1999 | 1999 | 169 |
| **Family & Personal Laws** | `FCA` | Family Courts Act, 1984 | 1984 | 23 |
|  | `GWA` | Guardians and Wards Act, 1890 | 1890 | 55 |
|  | `HAMA` | Hindu Adoptions and Maintenance Act, 1956 | 1956 | 30 |
|  | `HMA` | Hindu Marriage Act, 1955 | 1955 | 37 |
|  | `HSA` | Hindu Succession Act, 1956 | 1956 | 31 |
|  | `ISA` | Indian Succession Act, 1925 | 1925 | 392 |
|  | `MWPRDA` | Muslim Women (Protection of Rights on Divorce) Act, 1986 | 1986 | 7 |
|  | `MWPRMA` | Muslim Women (Protection of Rights on Marriage) Act, 2019 | 2019 | 8 |
|  | `PCMA` | Prohibition of Child Marriage Act, 2006 | 2006 | 21 |
|  | `SMA` | Special Marriage Act, 1954 | 1954 | 57 |
| **Environmental & Green Law** | `AIR` | Air (Prevention and Control of Pollution) Act, 1981 | 1981 | 62 |
|  | `EPA` | Environment (Protection) Act, 1986 | 1986 | 37 |
|  | `NGT` | National Green Tribunal Act, 2010 | 2010 | 39 |
|  | `VSA` | Van (Sanrakshan Evam Samvardhan) Adhiniyam, 1980 | 1980 | 10 |
|  | `WATER` | Water (Prevention and Control of Pollution) Act, 1974 | 1974 | 75 |
|  | `WPA` | Wild Life (Protection) Act, 1972 | 1972 | 162 |
| **Public Health, Healthcare & Food Safety** | `DCA` | Drugs and Cosmetics Act, 1940 | 1940 | 88 |
|  | `FSSA` | Food Safety and Standards Act, 2006 | 2006 | 101 |
|  | `MHA` | Mental Healthcare Act, 2017 | 2017 | 126 |
| **Social Protection, Education & Human Welfare** | `DV` | Protection of Women from Domestic Violence Act, 2005 | 2005 | 37 |
|  | `JJ` | Juvenile Justice (Care and Protection of Children) Act, 2015 | 2015 | 112 |
|  | `MWPSC` | Maintenance and Welfare of Parents and Senior Citizens Act, 2007 | 2007 | 32 |
|  | `POSH` | Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013 | 2013 | 30 |
|  | `RPWDA` | Rights of Persons with Disabilities Act, 2016 | 2016 | 102 |
|  | `RTE` | Right of Children to Free and Compulsory Education Act, 2009 | 2009 | 39 |
| **Energy, Infrastructure & Public Utilities** | `EA` | Electricity Act, 2003 | 2003 | 188 |

---

## ⚖️ Legal Disclaimer

> **Important Notice:** The Indian Legal MCP server is designed for legal research, compliance reference, educational analysis, and AI assistant grounding. It does **not** constitute formal legal advice. Neither the authors nor GSMS-B assume liability for actions taken based on this software. For live litigation or contractual advisory, always consult a qualified advocate and verify provisions against the official Gazette of India (indiacode.nic.in).

## 👤 Author & Maintainer

Engineered with pride by **GSMS-B**.

For issues, pull requests, and updates, visit the [GitHub Repository](https://github.com/GSMS-B/indian-legal-mcp).