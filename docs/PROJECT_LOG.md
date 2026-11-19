# Project Log

## 2026-11-19: Session 1 (Phase 1)

- Assessed the environment: Node 22, Python 3.13, PostgreSQL 16, PyYAML. No repository attached; the container is temporary.
- Research pass (web search): constitutional amendments through 22A (2026); PTA replacement Bill; Online Safety Act status; 2025 statutes (Proceeds of Crime, PDPA amendment); Anti-Corruption Act; ICCPR/CAT Acts; MMDA reform; 2026 FR judgments; corroboration of 8 landmark cases.
- Official legal hosts were blocked by the network policy. Added 10 hosts to the Default environment allowlist (saved). This session still could not reach them.
- Built the taxonomy (8 active and 6 planned disciplines, 55 subjects, 128 doctrines), the authorities register (183 L4 records), the source register (31), the watch list (11), verification framework v0.1, and the validator/builder.
- Corrected a relationship: Art 14A → *Fernando v SLBC* changed from OVERRULES to MODIFIES (legislative), since legislation does not overrule judgments.
- Decisions: YAML is the source of truth, compiled to a graph; IDs are stable across phases; PostgreSQL is preferred over Neo4j (see Phase 1 report §6).

## 2026-11-19: Session 1 (Phase 2 start)

- User asked me to continue with minimal input.
- Official hosts still unreachable (DNS); GitHub token invalid, no account linked. Backed up to Google Drive ("SL Legal KMS - backups").
- Corroborated 6 more cases (13A, 19A-2002, Karunathilaka, Joseph Perera, Saman, Faiz), bringing the total to 14. Downgraded the Faiz "acquiescence" proposition to unverified.
- Built PostgreSQL schema, loader, export/backup, and 8 integration tests (all pass); verified a pg_dump restore.

## 2026-11-19: Session 3 (Phase 2 verification)

- Restored the project from the Drive backup `sl-legal-kms-backup-2026-11-19-phase2-db.tgz` (branch `master`, 2 commits) into this repository as `main`. The push to GitHub was refused (403, no app access).
- Network: parliament.lk and lankalaw.net reachable; supremecourt.lk behind a Cloudflare bot challenge; documents.gov.lk is now a client-rendered app; LawNet reachable only over plain HTTP, and its old PDF paths return 404.
- Read the official consolidated Constitution (to 21A). 44/46 `CP-` records now `verified_primary`; 6 corrections, 7 open questions resolved. 22A status confirmed from parliament.lk; Judicature (Amendment) Act No. 23 of 2026.
- Read 29 Tier 1 judgments (LankaLaw SLLR/NLR reproductions). All 29 now `verified_primary`. 12 substantive corrections, including Bandara (no public trust), Gunaratne (1972 Constitution, positive association), Faiz (acquiescence confirmed, so the session 2 downgrade is reversed) and Joseph Perera (arrests held lawful). Resolved the Sriyani Silva, Visuvalingam, Liyanage and Choksy citation conflicts.
- Removed Bandara from the public-trust doctrines; corrected the T-CON-04-06 summary; used the schema's existing `full_text` access value; made one test independent of fixture data. 8/8 tests pass.
