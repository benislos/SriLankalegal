# Research Integrity and Source Verification Framework

*Status: v0.1 (drafted in Phase 1 because every record created from now on must carry these labels; finalised as Deliverable 10 in Phase 7).*

## 1. Two separate questions

Every legal record answers two different questions, and the system tracks them separately:

| Question | Field | Applies to |
|---|---|---|
| **How reliable is the source?** | `source_class` | each entry in `data/sources/source_register.yaml` |
| **How far have we checked this record?** | `verification_status` | each case, provision, statute, treaty, development |

A record can come from a reliable source and still be unverified if we have only seen a search snippet of it.

## 2. Source classes

| `source_class` | Meaning | Maps to the project brief's classes |
|---|---|---|
| `primary_official` | Official Act, Bill, Gazette, Hansard, or a judgment on a court or state site | Verified primary authority (once read) |
| `primary_reproduced` | Judgment or Act text reproduced by a non-official host (LawNet SLLR scans, ADB, UMN) | Verified primary authority (once read and checked against the report) |
| `secondary_scholarly` | Journals, theses, books, think-tank or academic analysis | Verified secondary commentary |
| `secondary_news` | Newspapers, legal news sites, blogs | Secondary commentary (low weight) |
| `ngo_ig` | NGO and intergovernmental reports (ICJ, Amnesty, UN bodies) | Secondary commentary or advocacy |
| *(comparative cases)* | Foreign judgments | Persuasive comparative authority (case field `authority_weight: persuasive_comparative`) |

`accessed_via` records how we actually saw the source: `search_index` (snippet only), `full_text` (whole document read), or `print` (the printed report).

## 3. Verification status

| `verification_status` | Rule | May be relied on in a lesson? |
|---|---|---|
| `verified_primary` | Full official or reproduced text read; each recorded detail (citation, date, holding, section) checked against it | Yes |
| `corroborated` | Existence, citation and core point supported by a primary-host record seen in a search index **or** by two or more independent secondary sources. Text not read. | Yes, but labelled as corroborated, with no direct quotations |
| `unverified` | Taken from researcher knowledge and not yet checked in this project | Only as "to be confirmed". Never quote it, never give a pinpoint. |
| `requires_investigation` | Conflicting citations, single-source reports, or a position still changing | No, except as an open question |

**Hard rules**

1. **No quotations** from a judgment or statute unless it is `verified_primary`.
2. **No pinpoint citations** (page or paragraph) unless `verified_primary`.
3. **Subsequent judicial treatment** (followed, distinguished, overruled) is a separate claim and must be verified on its own. Verifying a case does not verify what later courts did with it.
4. **Current-law claims** (in force, amended, repealed) carry an `as_of` date and must be re-checked against the Gazette, the Ministry of Justice legislative updates, or Parliament before being presented as operative.
5. **New judgments are not settled law.** A development goes into `data/watch/developments.yaml` with `settled_effect: pending`, and doctrine records change only after the judgment has been read and its significance assessed.
6. **Relationships carry a basis**: `judicial`, `legislative`, `academic`, `suggested` (a conceptual link proposed for investigation), or `structural` (part of the taxonomy hierarchy). A `suggested` link must never be shown as an established legal relationship.
7. **Status only goes up with evidence**: moving a record to `corroborated` or `verified_primary` requires adding a source ID. The build script refuses a corroborated or verified record that has no sources.

## 4. Citation conventions

- Sri Lanka Law Reports: `[2003] 2 Sri LR 63`. New Law Reports: `(1965) 68 NLR 265`.
- Unreported Supreme Court: `SC (FR) Application No. 471/2000, decided 8 Aug 2003`.
- Statutes: `Right to Information Act, No. 12 of 2016`, sections as `s. 5(1)(a)`.
- Constitution: `Art 126(2)`. State which amendment introduced or changed the provision where relevant.
- Where citations conflict between sources (e.g. Sriyani Silva, `[2003] 1` vs `[2003] 2 Sri LR`), record every variant in `notes` and keep the status at `corroborated` or below until the printed report is checked.

## 5. Preferred source order

1. supremecourt.lk and courtofappeal.lk judgments; documents.gov.lk Acts, Bills and Gazettes; parliament.lk Hansard and the consolidated Constitution
2. LawNet SLLR/NLR scans; srilankalaw.lk revised statutes; ADB, UMN and HURIGHTS reproductions
3. Academic analysis (Sri Lanka Journal of International Law, CPA, Verité, university repositories)
4. News and NGO reporting, used only to detect developments and debates

## 6. Known weaknesses at v0.1

- In session 1, official hosts could not be fetched directly from the build container (see the Phase 1 report), so no record was `verified_primary`. **Session 3 (19 Nov 2026)** read the official consolidated Constitution and 29 Tier 1 law reports in full: 44 provisions and 29 cases are now `verified_primary` (`accessed_via: full_text`).
- Law-report texts come from LankaLaw reproductions with OCR text layers. OCR errors in names, numbers and pinpoints are possible, so pinpoints should be checked against the page images before being quoted.
- A `CP-` record's `verified_primary` status is as of the consolidated text date (`as_of`). Later amendments (e.g. 22A, 2026) must be checked separately.
- Search-engine summaries were used for corroboration. They can paraphrase inaccurately, which is why such records are capped at `corroborated`.
