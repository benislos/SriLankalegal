# Phase 1 Report: Legal Landscape and Master Taxonomy

**Date:** 19 November 2026 · **Phase status:** complete as a *structural* foundation. Not yet a verified one (see §4).

## 1. What has been completed

| Item | Location | Notes |
|---|---|---|
| Master taxonomy, Levels 1–5 | `data/taxonomy/0*.yaml` → `docs/TAXONOMY.md` | 8 active disciplines, 6 planned; 55 subjects; 128 doctrines |
| Level 4 authorities register | `data/taxonomy/authorities.yaml` | 46 constitutional provisions, 8 amendments, 54 statutes/Bills, 9 treaties, 41 cases, 25 institutions |
| Source register | `data/sources/source_register.yaml` | 31 sources, each with class and access method |
| Development watch (first entries) | `data/watch/developments.yaml` | 11 items from 2025–26 |
| Verification framework v0.1 | `docs/VERIFICATION_FRAMEWORK.md` | Draft of Deliverable 10; already applied to every record |
| Validator and builder | `scripts/build_taxonomy.py` | Checks IDs, references, enums and source requirements. Emits `data/build/taxonomy.json` (graph-ready nodes and 974 typed edges) and the Markdown taxonomy |

**Design decision.** The taxonomy is authored as YAML and compiled into a node/edge graph from the start. The same IDs (`D-`, `S-`, `T-`, `CP-`, `ACT-`, `CASE-`, …) will become the primary keys in the Phase 2 database and the node IDs in the Phase 3 graph, so nothing has to be rebuilt later. The planned disciplines (criminal, commercial, land, labour, family/personal, international) already have IDs, so they plug in without restructuring.

### Areas added beyond the brief's list
- **D-FND Legal System, Sources and Method**: legal pluralism, court hierarchy and precedent, statutory and constitutional interpretation. Public law can't be learned coherently without it.
- **Constitutional Council and independent commissions** (S-CON-09); **language, religion and citizenship** (S-CON-11); **parliamentary privilege and delegated legislation** (S-CON-06); **contempt of court** (T-CON-05-03); **commissions of inquiry and the Ombudsman** (S-ADM-08); **Art 16 saving of existing law** (T-CON-04-02). This last one explains why colonial-era statutes and personal laws escape fundamental-rights challenge.

### Preliminary prioritisation (final ranking and sequence in Phase 5)
- **Tier 1, essential foundations (16 subjects):** sources of law; courts and precedent; interpretation; constitutional history; sovereignty, supremacy and amendment; separation of powers and executive; fundamental rights and remedies; judiciary and independence; foundations of review; writs; grounds of review; natural justice; reception of international law; arrest, detention and bail; counter-terrorism law; sources of private law.
- **Tier 2 (23)** and **Tier 3 (10)**: see `docs/TAXONOMY.md`. Each tier assignment has a written basis in the data (`tier_basis`).

## 2. Current-law findings from this research pass (as of 19 Nov 2026)

1. **22nd Amendment (2026)** passed 25 Sep 2026 by 158–63. It raises the retirement age of Supreme Court judges from 65 to 67 and Court of Appeal judges from 63 to 65. The Supreme Court determined that a two-thirds majority was enough and no referendum was needed. A companion Judicature (Amendment) Act changes lower-court retirement ages. The amendment is contested on judicial-independence grounds. *(corroborated)*
2. **PTA is still in force.** The Protection of the State from Terrorism Bill (gazetted 22 Sep, tabled 6 Oct 2026) would repeal it. A Supreme Court determination reportedly requires amendments, but that comes from a single outlet. *(Bill corroborated; determination requires investigation)*
3. **Online Safety Act No. 9 of 2024** remains unamended so far as can be found, despite the 2025 amendment committee, public consultation and a private member's repeal Bill. *(corroborated)*
4. **PDPA** amended by Act No. 22 of 2025. **Proceeds of Crime Act No. 5 of 2025** is in force. **Anti-Corruption Act 2023** amended in 2023, with a further amending Bill gazetted in 2026. *(corroborated)*
5. **No new-constitution process** is visible yet. The government now signals that the future of the Provincial Councils will be decided in a new constitution, and PC elections remain unheld. *(secondary analysis)*
6. **2026 fundamental-rights judgments to read in Phase 2:** the immunoglobulin procurement case (ministerial personal liability) and the Seagull Property Developers case (reportedly extends Art 126 to private actors). Neither may change doctrine records until read.

## 3. What has been verified

| Status | Constitutional provisions | Amendments | Legislation | Treaties | Cases |
|---|---|---|---|---|---|
| verified_primary | 0 | 0 | 0 | 0 | 0 |
| corroborated | 10 | 2 | 16 | 2 | 8 |
| unverified | 33 | 6 | 37 | 7 | 30 |
| requires_investigation | 3 | 0 | 1 | 0 | 3 |

Corroborated cases: *Liyanage v The Queen*, *Sriyani Silva v Iddamalgoda*, *Bulankulama* (Eppawela), *Premachandra v Jayawickrema*, *Bandara v Premachandra*, *Vasudeva Nanayakkara v Choksy*, *Singarasa v AG*, *Sampanthan v AG* (2018 dissolution case).

**Plainly:** most of the Level 4 layer is a researched, well-informed list of the authorities that *should* anchor each topic. It is not yet a checked one. The labels say so on every record, and the build script blocks anyone from upgrading a status without adding a source.

## 4. What requires further investigation

- **Citation conflicts:** *Sriyani Silva* (`[2003] 1` vs `[2003] 2` Sri LR); *Liyanage* date (1965/1966); *Visuvalingam v Liyanage* citation.
- **Changed provisions:** the current text of Art 35 (presidential immunity proviso after 20A/21A), Arts 120–124 (petition window and urgent Bills), the Art 83 entrenched list, and the Constitutional Council's composition after 21A.
- **Primary authorities still to find** (open questions in the taxonomy): leading cases on writ bars (delay, alternative remedy); substantive legitimate expectation; proportionality; duty to give reasons; the 2013 Standing Order 78A determination and Court of Appeal writ in the Bandaranayake impeachment; the 2023 economic-crisis FR judgment; the 2024 Supreme Court determination on the Online Safety Bill; the 2008 ICCPR advisory opinion; the final-judgment vs order test in civil appeals.
- **Statute details:** Contempt Act 2024 (title and number), Judicature (Amendment) Act 2026 number, CCPA (Amendment) Act No. 7 of 2025 content, treaty ratification dates.

## 5. Technical limitations

1. **Official sites are unreachable from this container.** supremecourt.lk, lawnet.gov.lk, documents.gov.lk, parliament.lk and lankalaw.net failed to resolve. I added these hosts to the environment's network allowlist and the change was saved, but this session still could not reach them: the web-fetch tool still failed DNS, and a direct check was blocked by the session's permission settings. **Full primary-text verification therefore did not happen in Phase 1.** It should work in a fresh session. If it doesn't, check the environment's network settings.
2. **Search summaries, not documents.** Corroboration relied on search-engine records of official files and on secondary reporting.
3. **Persistence.** This container is temporary. The project is committed to a local git repository but **not pushed anywhere**, because no GitHub repository is attached to this session. Work will be lost when the container is reclaimed unless a repository is provided.

## 6. Environment assessment (for the Phase 4 stack decision)

Available here: Node 22, Python 3.13, PostgreSQL 16 (installed, not running), PyYAML. Recommended stack, chosen for low infrastructure:
- **PostgreSQL** with `nodes`, `edges`, entity tables and `tsvector` full-text search. A separate Neo4j server isn't needed at this scale (hundreds to low thousands of nodes); recursive CTEs cover path discovery.
- **React (Vite) + Cytoscape.js** for the graph, **Recharts** for analytics, and a small Node/Express (or FastAPI) API.
- **Daily briefs** can be automated with a recurring cloud scheduled task that runs a fresh session each morning, writes the brief into the repository, updates the graph and pushes. That depends on the repository and network issues above being resolved.

## 7. Next steps (Phase 2: case law, legislation and doctrine databases)

1. Resolve persistence: attach or create a GitHub repository and push.
2. Re-test access to official hosts. Verify the Tier 1 authorities first: the Constitution text for every `CP-` record, then the roughly 25 Tier 1 cases.
3. Build full case records (all 16 fields in the brief, §6) for verified cases, and full statute records (all 10 fields, §5).
4. Fill the open-question gaps listed in §4, starting with writ procedure and legitimate expectation, which are needed early in the curriculum.
5. Define the PostgreSQL schema from `data/build/taxonomy.json` and load it. That is the bridge into Phase 3.
