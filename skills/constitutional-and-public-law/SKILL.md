---
name: constitutional-and-public-law
description: Master legal workflow for constitutional interpretation, Fundamental Rights, judicial review, legislative distribution of powers, election law, RTI, and public administration in India.
---

# 🏛️ Constitutional Law & Public Administration Workflow

## Scope: Which Act Answers What?
| Constitutional / Public Law Field | Applicable Statute | Key MCP Tools |
|---|---|---|
| Constitution of India (Articles 1–395) | `COI` (2026 Edition) | `get_section` (Section 0=Preamble, 1-395) |
| Constitutional Schedules (1–12) | `COI` Schedules | `get_constitution_schedule` |
| Legislative Lists (Union/State/Concurrent) | `COI` Seventh Schedule | `get_constitution_schedule("Seventh")` |
| Appendices (Presidential Orders, J&K) | `COI` Appendices | `get_constitution_appendix` |
| Right to Information (RTI) | `RTI` Act, 2005 | `get_section`, `search_keyword` |
| Human Rights (NHRC & State Commissions) | `PHRA`, 1993 | `get_section` |
| Civil Rights & Anti-Untouchability | `PCRA`, 1955 | `get_section` |
| Election Petitions & Disqualifications | `RPA`, 1951 | `get_section`, `search_keyword` |
| Free Legal Aid & Lok Adalats | `LSAA`, 1987 | `get_section` |
| Administrative Tribunals (CAT/SAT) | `ATA`, 1985 | `get_section` |
| Contempt of Courts | `CONTEMPT_COURTS`, 1971 | `get_section` |
| Right to Free and Compulsory Education | `RTE`, 2009 | `get_section` |
| Rights of Persons with Disabilities | `RPWDA`, 2016 | `get_section` |

## 5-Step Execution Workflow
1. **Identify the Fundamental Right or Constitutional Provision:**
   - Equality & Non-Discrimination: Articles 14, 15, 16.
   - Freedoms (Speech, Assembly, Association, Movement): Article 19(1)(a)-(g) subject to reasonable restrictions under 19(2)-(6).
   - Life, Liberty & Privacy: Article 21.
   - Preamble: Retrieve via `get_section("COI", "0")`.
2. **Determine the Judicial Review Forum:**
   - Supreme Court Writ Jurisdiction: Article 32.
   - High Court Writ Jurisdiction: Article 226.
3. **Verify Federal Legislative Competence:**
   - When determining whether Parliament or State Legislature has authority, call `get_constitution_schedule("Seventh")` to check List I (Union), List II (State), or List III (Concurrent).
4. **Evaluate Public Transparency & Administrative Remedies:**
   - For information requests: Check `RTI` Section 6 (application) and Section 8 (statutory exemptions from disclosure).
   - For civil servant disputes: Check `ATA` Section 14 (jurisdiction of Central Administrative Tribunal).
5. **Synthesize Citations & Provide Exact Provisions:**
   - Quote verbatim constitutional and statutory text.
