---
title: Indian Legal MCP
emoji: ⚖️
colorFrom: orange
colorTo: gray
sdk: gradio
sdk_version: 5.32.0
app_file: app.py
pinned: false
license: mit
---

<div align="center">

<img src="banner.png" alt="Indian Legal MCP banner" width="100%" />

# ⚖️ Indian Legal MCP

**Structured, sourced access to 10 major Indian legal texts — built for AI agents.**

![Python 3.10+](https://img.shields.io/badge/python-3.10+-orange.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-orange)](https://huggingface.co/spaces/GSMS-B/indian-legal-mcp)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Ready-gray.svg)](https://modelcontextprotocol.io/)
![Status](https://img.shields.io/badge/status-v1-success.svg)

[Live Server](#-connect-to-the-live-server) • [Tools](#-available-tools) • [Acts Covered](#-acts-covered) • [Credits](#-credits--data-sources) • [License](#-license)

<br>

<img src="poster.png" alt="Indian Legal MCP Poster" width="100%" />

</div>

---

## 📖 What is this?

**Indian Legal MCP** is a [Model Context Protocol](https://modelcontextprotocol.io/) server that gives AI assistants — Claude, ChatGPT, or any other MCP-compatible client — exact, structured access to the text of 10 major Indian Acts, instead of relying on the model's memory (and risking hallucination on section numbers, punishments, or repealed law).

Connect it once, and any AI agent using it can pull the real text of a section, browse a chapter, search by keyword, or check whether a law is still in force — all sourced directly from the underlying Act text, not guessed.

> **Disclaimer:** This is not legal advice. Always verify anything that matters against the official Gazette at [indiacode.nic.in](https://www.indiacode.nic.in). Historical Acts (IPC, CrPC, Indian Evidence Act) are clearly marked as repealed in every response — they remain useful for matters predating 1 July 2024, but no longer apply to new cases.

---

## ✨ Features

- **10 major Indian Acts** in one consistent, queryable structure
- **Smart keyword search** — exact title matches rank first, partial title matches next, body-text matches last (BM25-style relevance), so the most relevant section always surfaces first
- **Safe pagination** — large Acts (like BNS's 358 sections) are automatically chunked into manageable pages, so a single query never overflows an AI's context window
- **Historical-law awareness** — every response involving IPC, CrPC, or the Indian Evidence Act automatically notes that the Act is repealed and names the current replacement (BNS, BNSS, or BSA respectively)
- **No embeddings, no ML model running** — plain, fast, full-text search under the hood, which keeps this server free to host and quick to respond
- **Zero setup for the AI side** — connect once, and the AI decides on its own when a question calls for a lookup

---

## 📚 Acts covered

| Act | Full name | Status |
|---|---|---|
| **BNS** | Bharatiya Nyaya Sanhita, 2023 | ✅ Current |
| **BNSS** | Bharatiya Nagarik Suraksha Sanhita, 2023 | ✅ Current |
| **BSA** | Bharatiya Sakshya Adhiniyam, 2023 | ✅ Current |
| **COI** | Constitution of India | ✅ Current |
| **CPC** | Code of Civil Procedure, 1908 | ✅ Current |
| **MVA** | Motor Vehicles Act, 1988 | ✅ Current |
| **NIA** | Negotiable Instruments Act, 1881 | ✅ Current |
| **IPC** | Indian Penal Code, 1860 | 🕰️ Repealed → replaced by BNS |
| **CRPC** | Code of Criminal Procedure, 1973 | 🕰️ Repealed → replaced by BNSS |
| **IEA** | Indian Evidence Act, 1872 | 🕰️ Repealed → replaced by BSA |

---

## 🛠️ Available tools

| Tool | What it does |
|---|---|
| `list_acts()` | Lists all 10 Acts, with their current/repealed status |
| `get_act_info(act_code)` | Full name, year, and status of one Act |
| `get_section(act_code, section_number)` | Exact text of one section or Constitution article |
| `list_sections(act_code)` | Every section number + title in an Act, without full text — for browsing |
| `get_chapter(act_code, chapter_number)` | Every section in one chapter, in order |
| `get_section_range(act_code, start, end)` | All sections in a numeric range, inclusive |
| `get_full_act(act_code)` | The entire Act, paginated automatically for large Acts |
| `search_keyword(query, act_code?)` | Ranked keyword search, across one Act or all 10 |

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
    "indian-legal-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-proxy",
        "https://gsms-b-indian-legal-mcp.hf.space/gradio_api/mcp/"
      ]
    }
  }
}
```

Restart Claude Desktop — the tools will appear under the MCP/tools icon in the chat window.

### Other MCP clients (ChatGPT, etc.)

Use the same server URL above wherever your client asks for an MCP server endpoint. If your client connects over SSE directly (no local proxy needed), point it straight at the URL — `mcp-proxy` above is only needed for clients (like Claude Desktop) that expect a local stdio bridge.

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
