---
name: family-and-personal-law
description: Personal law research workflow for matrimonial disputes, divorce, child custody, intestate succession, and maintenance across religious and secular legal regimes in India.
---

# 👨‍👩‍👧 Family, Matrimonial & Personal Law Workflow

## Scope: Which Act Answers What?
| Family / Personal Subject | Applicable Statute | Key MCP Tools |
|---|---|---|
| Hindu Marriage, Restitution & Divorce | `HMA` (Hindu Marriage Act, 1955) | `get_section` (Sec 9, 13, 13B) |
| Hindu Intestate Succession & Coparcenary | `HSA` (Hindu Succession Act, 1956) | `get_section` (Sec 6, 8, 14, 15) |
| Hindu Adoption & Maintenance | `HAMA` (Hindu Adoptions & Maintenance)| `get_section` (Sec 6-12, 18-20) |
| Secular / Civil Marriage & Divorce | `SMA` (Special Marriage Act, 1954) | `get_section` (Sec 27, 28) |
| General & Christian/Parsi Succession | `ISA` (Indian Succession Act, 1925) | `get_section` (Wills, Probates) |
| Family Courts Conciliation & Jurisdiction | `FCA` (Family Courts Act, 1984) | `get_section` |
| Guardianship of Minor Person & Property | `GWA` (Guardians and Wards Act, 1890) | `get_section` (Sec 7, 17, 25) |
| Muslim Women Protection on Divorce | `MWPRDA`, 1986 | `get_section` (Sec 3, 4) |
| Triple Talaq (Talaq-e-Biddat) Prohibition | `MWPRMA`, 2019 | `get_section` (Sec 3, 4) |
| Child Marriage Prohibition & Annulment | `PCMA`, 2006 | `get_section` |

## 5-Step Execution Workflow
1. **Determine Religious Affiliation & Form of Marriage:**
   - Both parties Hindu/Buddhist/Jain/Sikh: Governed by `HMA` (marriage/divorce) and `HSA` (succession).
   - Inter-faith or civil registration: Governed by `SMA` (Special Marriage Act).
   - Muslim parties: Matrimonial divorce maintenance under `MWPRDA`; Talaq-e-Biddat under `MWPRMA`.
   - General testamentary wills and Christian/Parsi succession: Governed by `ISA`.
2. **Locate Specific Grounds for Relief:**
   - Divorce grounds: Mutual consent (`HMA` Sec 13B / `SMA` Sec 28), cruelty, adultery, desertion (`HMA` Sec 13).
   - Maintenance: `HMA` Sec 24 (interim) & Sec 25 (permanent); `HAMA` Sec 18; `MWPRDA` Sec 3.
3. **Verify Child Custody & Welfare Principle:**
   - Check `GWA` Section 17: The paramount consideration is the welfare of the minor.
4. **Assess Property Rights & Female Coparcenary:**
   - Under `HSA` Section 6 (post-2005 amendment), daughters possess equal coparcenary rights by birth.
5. **Synthesize Guidance:**
   - Quote exact section wording and establish statutory preconditions.
