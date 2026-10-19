---
name: banking-finance-recovery
description: Strategic procedural workflow for debt recovery, dishonour of cheques, SARFAESI enforcement, corporate insolvency (IBC), and financial regulatory compliance in India.
---

# 🏦 Banking, Debt Recovery & Insolvency Workflow

## Scope: Which Act Answers What?
| Financial / Recovery Need | Applicable Statute | Key MCP Tools |
|---|---|---|
| Cheque Bounce / Dishonour | `NIA` (Negotiable Instruments Act) | `get_section` (Section 138-142) |
| Non-Court Mortgage Enforcement | `SARFAESI` Act | `get_section` (Section 13, 14, 17) |
| Bank Debt Recovery Tribunal (DRT) | `RDBA` (Recovery of Debts Act) | `get_section` (Section 19) |
| Corporate Insolvency & Bankruptcy | `IBC` (Insolvency & Bankruptcy Code)| `get_section` (Section 7, 9, 10, 14) |
| Commercial Banking Governance | `BRA` (Banking Regulation Act) | `get_section` |
| RBI Powers & Monetary Policy | `RBI` Act | `get_section` |
| Forex & Cross-Border Transactions | `FEMA` | `get_section` |
| Digital Payments, UPI & Wallets | `PSSA` (Payment & Settlement Systems)| `get_section` |
| NGO & Foreign Funding Regulation | `FCRA` | `get_section` |
| Chit Funds | `CHIT` Act | `get_section` |

## 5-Step Execution Workflow
1. **Identify the Type of Creditor & Debt:**
   - If debt involves a bounced cheque: Check `NIA` Section 138 (statutory notice within 30 days of dishonour memo).
   - If creditor is a secured Bank/FI: Evaluate whether `SARFAESI` (Section 13 notice) or `RDBA` DRT suit is faster.
   - If corporate debtor defaults on ₹1 Crore or more: Evaluate Section 7 (Financial Creditor) or Section 9 (Operational Creditor) petition under `IBC`.
2. **Review Multi-Forum Thresholds & Traps:**
   - Consult `reference/recovery_routes.md` for monetary thresholds (DRT requires ₹20 Lakhs+; IBC requires ₹1 Crore+).
3. **Verify Security Enforcement & Notice Timelines:**
   - For SARFAESI: Section 13(2) gives debtor 60 days; Section 13(4) allows possession; Section 17 allows debtor to approach DRT.
4. **Examine Statutory Moratoriums:**
   - Under `IBC` Section 14, declaration of moratorium immediately stays all SARFAESI, DRT, and civil court proceedings against corporate debtor.
5. **Synthesize Guidance & Quote Provisions:**
   - Quote exact section text and procedural timelines.
