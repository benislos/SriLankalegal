# Phase 2 Progress: Case Law, Legislation and Doctrine Databases

**Status: in progress (19 Nov 2026).** The database infrastructure is complete and tested. Content verification is partly blocked (see Blockers).

## Done
- **PostgreSQL schema** (`db/schema.sql`)
  - A generic graph (`nodes`, `edges` with 21 relationship types and a basis on every edge).
  - Typed tables: `case_records` (all 16 fields in brief §6, with per-field verification), `legislation_records` (all 10 fields in brief §5), `lessons`, `research_questions` (the 5 statuses in the brief), `learning_progress`, `developments`.
  - `change_history`: triggers record every edit to a node, case, statute or research question.
  - Integrity rules enforced in the database:
    - nothing can be marked corroborated or verified without a source;
    - no duplicate relationships;
    - no self-links;
    - IDs must match the required format.
  - Full-text search (weighted `tsvector`).
- **Loader** (`scripts/load_db.py`): rebuilds the database from the YAML in a single transaction. **Export** (`scripts/export_db.py`): JSON, CSV per table, Markdown indexes, plus a `pg_dump` backup.
- **Tests** (`tests/test_db.py`), 8 passing:
  - search;
  - provision → doctrine → case navigation;
  - one case linked to several doctrines;
  - indirect (multi-hop) connection discovery;
  - history preserved;
  - the verification rule enforced;
  - no duplicate edges;
  - research tracker seeded.
  - Separately, a restore from `pg_dump` was checked: 434 nodes and 1,033 edges came back.
- **Research:** 6 more cases corroborated, bringing the total to 14 of 41. Full case records now exist for 14 cases in `data/cases/case_records.yaml`.
- **Correction:** the "state acquiescence" proposition previously attached to *Faiz v AG* is now marked unverified. Search records confirm the case and its arrest findings, not that proposition.
- **54 research questions** seeded from the taxonomy's open questions.

## Remaining in Phase 2
1. Read the primary text of the Tier 1 cases and the Constitution, and upgrade records to `verified_primary` (blocked, see below).
2. Fill in `legislation_records` fields 4–10 for the roughly 20 Tier 1 statutes (amendment history, key sections, status as of date).
3. Add leading authorities for the open gaps: writ bars, legitimate expectation, proportionality, reasons, Article 12 equality tests, the 2023 economic-crisis case, and the 2024 Online Safety Bill determination.

## Blockers
- **Official legal sites are still unreachable** from this session, even after the allowlist change. A new session should pick the change up.
- **GitHub isn't connected**, so nothing has been pushed. Backups are going to Google Drive instead (folder "SL Legal KMS - backups").

## Rebuilding the database in a new container
```bash
pg_ctlcluster 16 main start
su postgres -c "psql -c \"CREATE ROLE kms LOGIN PASSWORD 'kms' CREATEDB;\"" && su postgres -c "createdb -O kms sl_legal_kms"
pip install "psycopg[binary]" pytest pyyaml
python3 scripts/load_db.py && python3 -m pytest -q tests/
```
