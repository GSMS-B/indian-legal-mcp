---
name: criminal-law
description: Specialized legal workflow for Indian criminal law research, covering the 2024 criminal codes overhaul (BNS, BNSS, BSA vs IPC, CrPC, IEA) and specialized penal statutes.
---

# 🚨 Criminal Law & Sanhitas Transition Workflow

## Scope: Which Act Answers What?
| Domain Need | Applicable Statutes | Core MCP Tools |
|---|---|---|
| Substantive Offences | BNS (post-01/07/2024), IPC (pre-01/07/2024) | `get_section`, `convert_section` |
| Police Procedure & Bail | BNSS (post-01/07/2024), CRPC (pre-01/07/2024) | `get_section`, `convert_section` |
| Evidence & Electronics | BSA (post-01/07/2024), IEA (pre-01/07/2024) | `get_section`, `convert_section` |
| Child Sexual Offences | POCSO | `get_section`, `search_keyword` |
| Narcotics & Drugs | NDPS | `get_section`, `search_keyword` |
| Money Laundering | PMLA | `get_section`, `search_keyword` |
| Terror & Security | UAPA | `get_section`, `search_keyword` |
| Public Corruption | PCA | `get_section`, `search_keyword` |
| SC/ST Protection | SCST | `get_section`, `search_keyword` |
| Illicit Firearms | ARMS | `get_section`, `search_keyword` |
| Dowry Harassment | DPA | `get_section`, `search_keyword` |

## 5-Step Execution Workflow
1. **Determine Date of Offence:**
   - If offence was committed **before 1 July 2024**: Substantive offence falls under `IPC`, procedure under `CRPC`, evidence under `IEA`.
   - If offence was committed **on or after 1 July 2024**: Substantive offence falls under `BNS`, procedure under `BNSS`, evidence under `BSA`.
2. **Resolve Section or Concept:**
   - If section is known in old code (e.g. IPC 302 or IPC 420), call `convert_section("IPC", "302")` to retrieve BNS Section 103 and compare statutory wording.
   - If querying a topic (e.g. "snatching", "mob lynching", "cheating"), call `search_keyword(query="...", act_code="BNS")`.
3. **Verify Procedure & Custody/Bail:**
   - Check corresponding procedural section in `BNSS` using `get_section`.
   - Always check `reference/special_statutes.md` to see if a special statute overrides general bail rules (e.g. Section 37 NDPS twin conditions).
4. **Inspect Evidence Admissibility:**
   - For electronic records / digital evidence, retrieve Section 61/63 of `BSA` (replaces old 65B IEA).
5. **Synthesize & Cite:**
   - Quote both old and new sections if historical comparison is relevant. Always include statutory citation and disclaimer.

## Critical Traps to Avoid
- ⚠️ **Trap 1:** Never apply BNS retrospectively to an incident that occurred before July 1, 2024 (violates Article 20(1) Constitution of India - protection against ex-post facto laws).
- ⚠️ **Trap 2:** Special statutes (NDPS, POCSO, PMLA, UAPA) possess overriding non-obstante clauses. General BNSS bail provisions yield to special statutory bars.
- ⚠️ **Trap 3:** Electronic evidence certification under BSA Section 63 has modified schedule formats compared to old Section 65B of IEA.
