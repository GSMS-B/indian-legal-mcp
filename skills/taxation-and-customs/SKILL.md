---
name: taxation-and-customs
description: Authoritative workflow for Indian direct and indirect tax analysis, covering Income-tax Act 2025, GST (CGST/IGST), Customs, Stamp Act, and Benami transactions.
---

# 💰 Taxation, Customs & Revenue Law Workflow

## Scope: Which Act Answers What?
| Tax & Fiscal Subject | Applicable Statute | Key MCP Tools |
|---|---|---|
| Direct Tax (Income, Corporate, Capital Gains, TDS) | `ITA` (Income-tax Act, 2025) | `get_section`, `get_chapter` |
| Intra-State GST & Supply | `CGST` Act, 2017 | `get_section`, `search_keyword` |
| Inter-State GST & Import of Goods/Services | `IGST` Act, 2017 | `get_section` |
| Import/Export Customs Duty & Anti-Smuggling | `CUSTOMS` Act, 1962 | `get_section`, `search_keyword` |
| Stamp Duty on Deeds & Instruments | `STAMP` (Indian Stamp Act, 1899) | `get_section` |
| Benami Property Confiscation & Penalties | `PBPTA` (Benami Transactions Act) | `get_section` |

## 5-Step Execution Workflow
1. **Identify the Tax Domain & Tax Year:**
   - Direct Tax: In force from April 1, 2026 under `ITA` (2025 codification, 536 sections).
   - Indirect Tax: Goods and Services Tax governed by `CGST` and `IGST`.
   - International Trade: Customs duties, valuations, and confiscation governed by `CUSTOMS`.
2. **Locate the Charging Section & Operative Chapter:**
   - For Income Tax: Use `get_chapter("ITA", "III")` for Incomes exempt from tax, `get_chapter("ITA", "X")` for Special provisions, etc.
   - For GST: Check Section 9 CGST (levy and collection), Section 16 (Input Tax Credit eligibility).
3. **Verify Valuation & Stamp Duty Enforceability:**
   - For commercial contracts: Check `STAMP` Section 35 (inadmissibility of unstamped or insufficiently stamped instruments).
4. **Check Benami Property Prohibitions:**
   - Check `PBPTA` Section 3 (prohibition of benami transactions) and Section 5 (confiscation of benami property).
5. **Synthesize Citations & Provide Exact Provisions:**
   - Quote verbatim section texts and explain statutory rate/compliance mechanisms.
