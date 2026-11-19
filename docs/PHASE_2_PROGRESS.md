# Phase 2 Progress: Case Law, Legislation and Doctrine Databases

**Status: in progress (19 Nov 2026, session 3).** The database is built and tested. The first primary-text verification pass is done: **44 of 46 constitutional provisions and 29 of 41 cases are now `verified_primary`.** Phase 1 started with none.

## Session 3: primary-text verification

### Access
| Host | Result | Used for |
|---|---|---|
| parliament.lk | Reachable | Consolidated Constitution PDF; Speaker's announcements and news on 22A |
| lankalaw.net | Reachable (WordPress media API `wp-json/wp/v2/media?search=`) | SLLR/NLR report PDFs with OCR text layer |
| lawnet.gov.lk | Reachable only over plain HTTP (TLS certificate does not match); old `wp-content` PDF paths now 404 | Not used |
| documents.gov.lk | Reachable, but now a client-rendered app; no document routes found | Not used. **Acts and Gazettes still unread** |
| supremecourt.lk | Cloudflare bot challenge (HTTP 403 from the site, not the proxy) | Not used. **Unreported judgments still unread** |

### Constitution (SRC-0038)
The official text read is the Parliament Secretariat Revised Edition 2023, as amended up to 31 Oct 2022 (to 21A). Every `CP-` title was checked against it, and every record carries `as_of: 2022-10-31`.

The **22nd Amendment (2026)** is not in any consolidated text. Its passage, certification and the SC determination were confirmed from official parliament.lk announcements (SRC-0039 to SRC-0041), but the Act text is still unread. For that reason `CP-1978` and `CP-ART-107` stay `corroborated`.

**Corrections:**
- **Art 33:** after 20A it is a single list (a)–(h) with no dissolution power. The old "33(2)(c)" was the 19A structure.
- **Art 70(1)(a):** the dissolution bar is now **2 years 6 months** (20A s.12). It was 4½ years under 19A, which is the text *Sampanthan* construed.
- **Chapter numbering:**
  - Arts 75–80 are in Chapter XI.
  - The JSC is in Chapter XVA.
  - The Court of Appeal is in Chapter XVI.
  - Chapter XVIIIA covers only the National Police Commission (Arts 155A–155N).
- **Art 61A:** the ouster is subject to Art 59 as well as Art 126.

**Open questions from Phase 1 now resolved:**
- **Art 35:** the 19A proviso allowing Art 126 applications against the AG survives 20A and 21A.
- **Art 83:** entrenches Arts 1, 2, 3, 6, 7, 8, 9, 10, 11 and 83, plus Arts 30(2) and 62(2) beyond six years.
- **Art 121:** the petition window is **14 days** (21A s.17).
- **Art 122:** urgent Bills were reinstated by 20A, limited to national security and disaster management, and are not available for constitutional amendments.
- **Constitutional Council:** 10 members after 21A, with the Speaker as Chairman.
- **22A:** passed and certified on 25 Sep 2026 (158–63). It adds a **six-year term limit for the Chief Justice** (the sitting CJ is exempted, per the SC determination) and amends Art 137 (Court of Appeal judges from 19 to 24).
- **Judicature (Amendment) Act No. 23 of 2026:**
  - HC judges retire at 63, District Judges and Magistrates at 62.
  - The maximum number of HC judges rises to 120.

### Cases (SRC-0042 to SRC-0075)
All 29 reported Sri Lankan Tier 1 cases were read from LankaLaw reproductions of the printed reports. For each one I checked the citation, bench, application number, date, outcome and headnote holdings. Twelve of the 14 full case records in `data/cases/case_records.yaml` were updated field by field (`field_status`, `text_sources`, `verification_note`). The other two (Sampanthan and Singarasa) are unreported and unread.

**Substantive corrections. These change doctrine content, so read before teaching from the old records:**

| Case | Old claim | What the text says |
|---|---|---|
| *Bandara v Premachandra* [1994] 1 Sri LR 301 | "Early articulation of the public trust doctrine" | An Art 12 / trade-union termination case with no public-trust reasoning. Removed as authority from T-CON-03-04, T-ADM-01-03 and S-ADM-01 |
| *Gunaratne v People's Bank* [1986] 1 Sri LR 338 | Art 14(1)(d) "includes freedom not to associate" | Decided under the **1972** Constitution s.18(1)(f); protects the **positive** freedom to form and join a union. T-CON-04-06 summary corrected; the negative freedom is now flagged as an open question |
| *Faiz v AG* [1995] 1 Sri LR 372 | Acquiescence proposition downgraded to unverified (session 2) | **Confirmed** from the text: private acts done with executive approval, connivance or acquiescence (including inaction where there is a duty to act) are executive action. The session 2 downgrade is reversed |
| *Joseph Perera* [1992] 1 Sri LR 199 | Reg 28 "ultra vires the PSO"; "arrests illegal" | Reg 28 was invalid for violating Arts 14(1)(a) and 12 (prior restraint, no proximate nexus). The **majority held the arrests lawful**; detention was unlawful only from 15.7.86 |
| *Dissanayake v Kaleel* [1993] 2 Sri LR 135 | Natural justice in party discipline | The majority **upheld** the expulsions and found no breach of natural justice; Fernando J dissented |
| *Fernando v SLBC* [1996] 1 Sri LR 157 | "No free-standing right to information" (as holding) | The petitioner **won**: Art 14(1)(a) is read broadly. The point about a right to information simpliciter is only a *semble* doubt |
| *Senarath v Kumaratunga* [2007] 1 Sri LR 59 | Presidential immunity after office | Immunity is not discussed. The case concerns equality, custodianship and standing; the former President paid costs personally |
| *Bulankulama* [2000] 3 Sri LR 243 | Public trust doctrine; "intergenerational equity" | Amerasinghe J found the US public trust doctrine restrictive and preferred **guardianship / shared responsibility**. The phrase "intergenerational equity" is not used |
| *EFL v UDA* [2009] 1 Sri LR 123 | Public trust | Not mentioned. Decided 23 Nov 2005 (reported 2009) |
| *Velmurugu* [1981] 1 Sri LR 406 | Dissent of Sharvananda J | Dissent was by Sharvananda **and Ratwatte JJ**; the application was dismissed 3–2 |
| *Wickrematunga v Ratwatte* | "Political considerations" | The case concerns Art 12 and arbitrariness in a CPC dealership contract (instrumentality doctrine) |
| *Ibralebbe* (PC) | "Compatible with sovereignty" | Privy Council criminal jurisdiction survived independence; special leave granted |

**Citation conflicts resolved:**
- **Sriyani Silva:** there are *two* judgments in SC 471/2000, both reported:
  - [2003] 1 Sri LR 14 (preliminary objections, 10 Dec 2002);
  - [2003] 2 Sri LR 63 (merits, 8 Aug 2003; Rs 800,000).
- **Visuvalingam v Liyanage:** there are four reported judgments. The readers' rights case is **[1984] 2 Sri LR 123** (14 Jun 1984).
- **Liyanage:** delivered 2 Dec 1965.
- **Choksy:** [2008] 1 Sri LR 134.
- **13A determination:** the clause lettering is 154G(2)(b) and (3)(b).

### Database and tests
- The loader rebuilt cleanly: 41 sources added this session, 75 in total.
- All 8 integration tests pass. `test_cannot_mark_verified_without_source` no longer depends on one hard-coded case (Gunaratne now has a source); it picks any unsourced case at runtime.
- Sources read in full use the existing `accessed_via: full_text` value. SHA-256 hashes of every PDF are recorded in the source notes.

## Remaining in Phase 2
1. **Unreported Tier 1 cases** (blocked by supremecourt.lk's bot challenge): *Sampanthan* (2018), *Singarasa* (2006), *Mundy* (2004), and the two 2026 cases (immunoglobulin procurement and Seagull). Options:
   - the user downloads them in a browser and drops the PDFs into Drive;
   - or I run on the user's own computer.
2. **22A Act text and the full SC determination** (Hansard, 22 Sep 2026). Then upgrade `CP-ART-107` and `CP-1978`.
3. **documents.gov.lk:** find the new app's API, or take Acts and Gazettes as PDFs from the user. Needed for legislation fields 4–10 on about 20 Tier 1 statutes.
4. **Foreign Tier 1 cases** (Wednesbury, GCHQ, Ridge, Anisminic, Padfield, Kesavananda): verify against BAILII / Indian Kanoon. They are out of scope for "official Sri Lankan sites".
5. **Subsequent treatment** fields remain separate claims and are still unverified (framework rule 3).
6. **Gaps:**
   - writ bars;
   - legitimate expectation;
   - proportionality;
   - reasons;
   - Art 12 tests;
   - the 2023 economic-crisis case;
   - the 2024 Online Safety Bill determination;
   - an authority on the negative freedom of association.

## Blockers
- **GitHub push refused (403):** "Claude doesn't have GitHub access to benislos/SriLankalegal". History is committed locally on `main` and `claude/keen-ptolemy-47njdn`, and backed up to Drive.
- **Hosting decision pending:** Supabase + Vercel, or the user's own computer. This determines Phase 4 and the daily brief (dashboard plus email).

## Rebuilding the database in a new container
```bash
pg_ctlcluster 16 main start
su postgres -c "psql -c \"CREATE ROLE kms LOGIN PASSWORD 'kms' CREATEDB;\"" && su postgres -c "createdb -O kms sl_legal_kms"
pip install "psycopg[binary]" pytest pyyaml
python3 scripts/load_db.py && python3 -m pytest -q tests/
```
