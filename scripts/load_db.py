#!/usr/bin/env python3
"""Rebuild the PostgreSQL database from the version-controlled data files.

Usage: python3 scripts/load_db.py            (DSN from $KMS_DSN or the default local dev DSN)
Steps: apply db/schema.sql -> sources -> nodes -> node_sources -> edges -> case/legislation records
       -> research questions (from taxonomy open_questions) -> developments.
Runs in one transaction; any integrity failure (e.g. a 'corroborated' record without a source)
aborts the whole load.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import psycopg
import yaml
from psycopg.types.json import Jsonb

ROOT = Path(__file__).resolve().parent.parent
DSN = os.environ.get("KMS_DSN", "postgresql://kms:kms@localhost/sl_legal_kms")

DETAIL_KEYS = {"id", "type", "name", "title", "description", "parent", "tier", "status",
               "verification_status", "sources"}


def main() -> int:
    # Always rebuild the compiled graph first so the DB and YAML cannot drift.
    if subprocess.run([sys.executable, str(ROOT / "scripts/build_taxonomy.py")],
                      capture_output=True).returncode:
        print("build_taxonomy.py failed - fix data errors first")
        return 1
    graph = json.loads((ROOT / "data/build/taxonomy.json").read_text())
    sources = yaml.safe_load((ROOT / "data/sources/source_register.yaml").read_text())["sources"]
    devs = yaml.safe_load((ROOT / "data/watch/developments.yaml").read_text())["developments"]
    cases = yaml.safe_load((ROOT / "data/cases/case_records.yaml").read_text())["records"]
    node_ids = {n["id"] for n in graph["nodes"]}

    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        cur.execute((ROOT / "db/schema.sql").read_text())
        cur.execute("SET search_path = kms")

        for s in sources:
            cur.execute("INSERT INTO sources VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (s["id"], s["title"], s["url"], s["source_class"], s["accessed_via"],
                         s["accessed"], s.get("notes")))

        for n in graph["nodes"]:
            desc = n.get("description") or n.get("summary") or n.get("point")
            if isinstance(desc, str):
                desc = desc.strip()
            attrs = {k: v for k, v in n.items() if k not in DETAIL_KEYS}
            cur.execute(
                "INSERT INTO nodes(id,node_type,name,description,parent_id,tier,status,verification_status,attrs)"
                " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (n["id"], n["type"], n.get("name") or n.get("title"), desc, n.get("parent"),
                 n.get("tier"), n.get("status"), n.get("verification_status"), Jsonb(attrs)))
            for s in n.get("sources") or []:
                cur.execute("INSERT INTO node_sources VALUES (%s,%s)", (n["id"], s))

        for e in graph["edges"]:
            cur.execute("INSERT INTO edges(from_id,to_id,rel_type,basis,note) VALUES (%s,%s,%s,%s,%s)"
                        " ON CONFLICT DO NOTHING", (e["from"], e["to"], e["type"], e["basis"], e.get("note")))

        # Case detail records + treatment edges
        by_id = {n["id"]: n for n in graph["nodes"]}
        for r in cases:
            cid = r["id"]
            if cid not in node_ids:
                raise SystemExit(f"case record {cid} has no authorities.yaml node")
            n = by_id[cid]
            p = lambda v: None if v in (None, "pending") else v  # noqa: E731
            cur.execute(
                "INSERT INTO case_records(node_id,full_name,citation,court,year,application_no,decided_on,bench,"
                "material_facts,legal_issues,decision,ratio,obiter,principles,subsequent_treatment,"
                "authority_weight,field_status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (cid, n["name"], n.get("citation"), n.get("court"), n.get("year"), p(r.get("application_no")),
                 r.get("decided_on"), r.get("bench") or None, p(r.get("material_facts")),
                 r.get("legal_issues") or None, p(r.get("decision")), p(r.get("ratio")), r.get("obiter") or None,
                 r.get("principles") or None, p(r.get("subsequent_treatment")), n.get("authority_weight"),
                 Jsonb(r.get("field_status", {}))))
            for e in r.get("edges", []):
                cur.execute("INSERT INTO edges(from_id,to_id,rel_type,basis,note,source_ids) VALUES (%s,%s,%s,%s,%s,%s)"
                            " ON CONFLICT DO NOTHING",
                            (cid, e["to"], e["type"], e["basis"], e.get("note"), e.get("sources", [])))

        # Legislation detail stubs (fields 4-10 populated as statutes are researched)
        for n in graph["nodes"]:
            if n["type"] == "legislation":
                cur.execute("INSERT INTO legislation_records(node_id,official_title,current_status,status_as_of)"
                            " VALUES (%s,%s,%s,%s)", (n["id"], n["name"], n.get("status"), graph["generated"]))

        # Research tracker seeded from taxonomy open questions
        k = 0
        for n in graph["nodes"]:
            for q in n.get("open_questions") or []:
                k += 1
                rid = f"RQ-{k:04d}"
                cur.execute("INSERT INTO nodes(id,node_type,name,description) VALUES (%s,'research_question',%s,%s)",
                            (rid, q[:120], q))
                status = "requires_verification" if "verify" in q.lower() else "not_started"
                cur.execute("INSERT INTO research_questions(node_id,question,category,status,raised_in)"
                            " VALUES (%s,%s,%s,%s,%s)", (rid, q, n["parent"], status, n["id"]))
                cur.execute("INSERT INTO edges(from_id,to_id,rel_type,basis) VALUES (%s,%s,'RELATED_TO','structural')",
                            (rid, n["id"]))

        for d in devs:
            cur.execute("INSERT INTO developments VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (d["id"], d["date"], d["kind"], d["title"], d.get("affects", []), d.get("sources", []),
                         d["settled_effect"], d["verification_status"], d.get("follow_up")))

        for subject in (n for n in graph["nodes"] if n["type"] in ("subject", "doctrine")):
            cur.execute("INSERT INTO learning_progress(topic_id) VALUES (%s)", (subject["id"],))

        conn.commit()
        cur.execute("SELECT row_to_json(s) FROM kms.v_stats s")
        print(json.dumps(cur.fetchone()[0], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
