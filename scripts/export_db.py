#!/usr/bin/env python3
"""Export the database to JSON, CSV and Markdown, and take a pg_dump backup.

Usage: python3 scripts/export_db.py [outdir]      (default: exports/<date>)
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parent.parent
DSN = os.environ.get("KMS_DSN", "postgresql://kms:kms@localhost/sl_legal_kms")
TABLES = ["sources", "nodes", "node_sources", "edges", "case_records", "legislation_records",
          "research_questions", "learning_progress", "developments", "lessons", "change_history"]


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "exports" / date.today().isoformat()
    (out / "csv").mkdir(parents=True, exist_ok=True)
    dump = {}
    with psycopg.connect(DSN, row_factory=dict_row) as conn, conn.cursor() as cur:
        for t in TABLES:
            cur.execute(f"SELECT * FROM kms.{t}")
            rows = cur.fetchall()
            for r in rows:
                r.pop("search", None)
            dump[t] = rows
            with open(out / "csv" / f"{t}.csv", "w", newline="") as f:
                if rows:
                    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                    w.writeheader()
                    for r in rows:
                        w.writerow({k: json.dumps(v, default=str) if isinstance(v, (dict, list)) else v
                                    for k, v in r.items()})
        (out / "kms.json").write_text(json.dumps(dump, indent=1, default=str, ensure_ascii=False))

        # Markdown: case law index
        cur.execute("""SELECT n.id, c.full_name, c.citation, c.court, c.year, n.verification_status::text vs,
                              c.ratio FROM kms.case_records c JOIN kms.nodes n ON n.id=c.node_id
                       UNION ALL
                       SELECT n.id, n.name, n.attrs->>'citation', n.attrs->>'court', (n.attrs->>'year')::int,
                              n.verification_status::text, n.description
                       FROM kms.nodes n WHERE n.node_type='case'
                         AND NOT EXISTS (SELECT 1 FROM kms.case_records c WHERE c.node_id=n.id)
                       ORDER BY year""")
        md = ["# Case Law Index (export)", "", "| Year | Case | Citation | Court | Status | Ratio / point |",
              "|---|---|---|---|---|---|"]
        for r in cur.fetchall():
            md.append(f"| {r['year']} | {r['full_name']} | {r['citation'] or ''} | {r['court'] or ''} | "
                      f"{r['vs']} | {(r['ratio'] or '').replace('|', '/')} |")
        cur.execute("""SELECT q.node_id, q.question, q.status, q.raised_in FROM kms.research_questions q
                       ORDER BY q.node_id""")
        md += ["", "# Research Questions", "", "| ID | Question | Status | Raised in |", "|---|---|---|---|"]
        md += [f"| {r['node_id']} | {r['question']} | {r['status']} | {r['raised_in']} |" for r in cur.fetchall()]
        (out / "kms.md").write_text("\n".join(md) + "\n")

    dump_file = out / "sl_legal_kms.pgdump"
    rc = subprocess.run(["pg_dump", "-Fc", "-f", str(dump_file), DSN]).returncode
    print(f"exported to {out} (pg_dump rc={rc})")
    return rc


if __name__ == "__main__":
    sys.exit(main())
