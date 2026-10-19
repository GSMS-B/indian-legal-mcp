---
name: corporate-securities-insurance
description: Legal workflow for corporate governance, Companies Act compliance, LLP formation, capital markets regulations (SEBI & SCRA), competition law, and insurance law.
---

# 🏢 Corporate, Securities & Insurance Law Workflow

## Scope: Which Act Answers What?
| Corporate / Market Area | Applicable Statute | Key MCP Tools |
|---|---|---|
| Companies Incorporation, Directors, CSR | `CA` (Companies Act, 2013) | `get_section`, `get_chapter` |
| Limited Liability Partnerships | `LLP` Act, 2008 | `get_section` |
| Traditional Partnerships | `IPA` (Indian Partnership Act) | `get_section` |
| Capital Markets & Insider Trading | `SEBI` Act, 1992 | `get_section` |
| Stock Exchanges, Listing & Derivatives | `SCRA`, 1956 | `get_section` |
| Anti-Trust, Cartels & Combinations | `COMPETITION` Act, 2002 | `get_section` |
| Commercial Courts & Fast-Track Suits | `COMMERCIAL_COURTS` Act | `get_section` |
| Insurance Business, Solvency & Claims | `INSURANCE` Act, 1938 | `get_section` |
| Insurance Regulatory Authority | `IRDAI` Act, 1999 | `get_section` |

## 5-Step Execution Workflow
1. **Determine Corporate Entity Structure:**
   - Private/Public Company: Governed by `CA` (517 sections).
   - LLP: Governed by `LLP` (88 sections).
   - Partnership Firm: Governed by `IPA` (74 sections).
2. **Identify Regulatory Body & Forum:**
   - Corporate disputes & schemes: National Company Law Tribunal (NCLT) / NCLAT (`CA`).
   - Securities violations: SEBI Adjudicating Officer / Securities Appellate Tribunal (SAT).
   - Anti-competitive agreements / abuse of dominance: Competition Commission of India (CCI).
   - Insurance grievances: Insurance Ombudsman / IRDAI.
3. **Inspect Relevant Chapters & Sections:**
   - For Companies Act: Use `get_chapter("CA", "XI")` for Directors, `get_chapter("CA", "IX")` for Accounts & CSR.
   - For SEBI: Check Section 11 (powers of board), Section 12A (insider trading prohibitions), Section 15HA (penalties for fraudulent trade).
   - For SCRA: Check Section 13-18 (contracts in securities) and Section 21-22 (listing requirements).
4. **Verify Mandatory Thresholds:**
   - Commercial Courts: Specified Value threshold of ₹3 Lakhs under Section 2(1)(i).
   - Corporate CSR: Net worth ₹500 Cr, Turnover ₹1000 Cr, or Net Profit ₹5 Cr under Section 135.
5. **Synthesize Findings:**
   - Deliver clear citations with direct statutory quotes.
