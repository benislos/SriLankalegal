# Sri Lankan Legal Intelligence and Knowledge Management System

A long-term research, education and knowledge-graph project mapping Sri Lankan law, beginning with public law.

## Status

| Phase | Scope | Status |
|---|---|---|
| 1 | Legal landscape and master taxonomy | **Done (structural)**: see `docs/PHASE_1_REPORT.md` |
| 2 | Case law, legislation and doctrine databases | **In progress**: database built and tested; 44/46 provisions and 29/41 cases verified against primary text (`docs/PHASE_2_PROGRESS.md`) |
| 3 | Knowledge graph and relationship architecture | Not started |
| 4 | Functional dashboard | Not started |
| 5 | Curriculum and daily briefing protocol | Not started |
| 6 | Daily workflow and development monitoring | Not started |
| 7 | System testing | Not started |

## Layout

```
data/taxonomy/        source of truth: YAML taxonomy (L1–L3 + L5 links) and authorities register (L4)
data/sources/         source register; every claim traces to an SRC-#### id
data/watch/           jurisprudential development watch
data/build/           generated: taxonomy.json (graph nodes + typed edges)
docs/                 reports, generated TAXONOMY.md, verification framework, project log
scripts/              build and validation tooling
```

## Build

```bash
python3 scripts/build_taxonomy.py
```

This validates every ID, reference, relationship type and verification label, then regenerates `data/build/taxonomy.json` and `docs/TAXONOMY.md`. It exits non-zero on any error. Run it after every data edit.

## Integrity rules (summary)

Every authority carries a `verification_status`: `verified_primary`, `corroborated`, `unverified`, or `requires_investigation`. Unverified material is never quoted or pinpoint-cited. See `docs/VERIFICATION_FRAMEWORK.md`.

## Database (Phase 2)

```bash
python3 scripts/load_db.py        # rebuild PostgreSQL from data/ (runs the taxonomy build first)
python3 -m pytest -q tests/       # integration tests
python3 scripts/export_db.py      # JSON + CSV + Markdown + pg_dump into exports/<date>/
```
