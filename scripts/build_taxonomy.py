#!/usr/bin/env python3
"""Validate the Phase-1 taxonomy and build machine-readable and human-readable outputs.

Inputs : data/taxonomy/*.yaml, data/sources/source_register.yaml
Outputs: data/build/taxonomy.json   (nodes + typed edges, ready for DB import in Phase 2/3)
         docs/TAXONOMY.md           (generated, do not hand-edit)
Exit code 1 if any validation error is found.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TAX = ROOT / "data" / "taxonomy"
OUT_JSON = ROOT / "data" / "build" / "taxonomy.json"
OUT_MD = ROOT / "docs" / "TAXONOMY.md"

VERIFICATION = {"verified_primary", "corroborated", "unverified", "requires_investigation"}
REL_TYPES = {"ESTABLISHES", "INTERPRETS", "APPLIES", "REGULATES", "DERIVES_FROM", "LIMITS",
             "QUALIFIES", "DISTINGUISHES", "OVERRULES", "MODIFIES", "CITES", "INFLUENCES",
             "RELATED_TO", "CONTRADICTS", "DEVELOPS", "REAFFIRMS", "PART_OF", "HAS_BASIS",
             "KEY_AUTHORITY"}
REL_BASIS = {"judicial", "legislative", "academic", "suggested", "structural"}
ID_PATTERNS = {
    "discipline": r"^D-[A-Z]{3}$",
    "subject": r"^S-[A-Z]{3}-(\d{2}|PLAN)$",
    "doctrine": r"^T-[A-Z]{3}-\d{2}-\d{2}$",
    "constitutional_provision": r"^CP-[A-Z0-9-]+$",
    "amendment": r"^AMD-\d{2}$",
    "legislation": r"^(ACT|BILL)-[A-Z0-9-]+$",
    "treaty": r"^TRT-[A-Z0-9-]+$",
    "case": r"^CASE-[A-Z0-9-]+$",
    "institution": r"^INST-[A-Z0-9-]+$",
}

errors: list[str] = []
warnings: list[str] = []
nodes: dict[str, dict] = {}
edges: list[dict] = []


def add_node(node_id: str, ntype: str, data: dict, where: str) -> None:
    if node_id in nodes:
        errors.append(f"duplicate id {node_id} ({where})")
        return
    if not re.match(ID_PATTERNS[ntype], node_id):
        errors.append(f"id {node_id} does not match pattern for {ntype} ({where})")
    nodes[node_id] = {"id": node_id, "type": ntype, **data}


def add_edge(src: str, dst, default_type: str, default_basis: str, where: str) -> None:
    if isinstance(dst, dict):
        e = {"from": src, "to": dst.get("to"), "type": dst.get("type", default_type),
             "basis": dst.get("basis", default_basis), "note": dst.get("note")}
    else:
        e = {"from": src, "to": dst, "type": default_type, "basis": default_basis, "note": None}
    if e["type"] not in REL_TYPES:
        errors.append(f"{where}: unknown relationship type {e['type']}")
    if e["basis"] not in REL_BASIS:
        errors.append(f"{where}: unknown relationship basis {e['basis']}")
    e["where"] = where
    edges.append(e)


def load_sources() -> set[str]:
    reg = yaml.safe_load((ROOT / "data/sources/source_register.yaml").read_text())
    ids = [s["id"] for s in reg["sources"]]
    for i, c in Counter(ids).items():
        if c > 1:
            errors.append(f"duplicate source id {i}")
    for s in reg["sources"]:
        for f in ("title", "url", "source_class", "accessed_via", "accessed"):
            if not s.get(f):
                errors.append(f"source {s.get('id')} missing {f}")
    return set(ids)


def load_authorities(source_ids: set[str]) -> None:
    a = yaml.safe_load((TAX / "authorities.yaml").read_text())
    kinds = {"constitutional_provisions": "constitutional_provision", "amendments": "amendment",
             "legislation": "legislation", "treaties": "treaty", "cases": "case",
             "institutions": "institution"}
    for key, ntype in kinds.items():
        for rec in a.get(key, []):
            rid = rec["id"]
            data = {k: v for k, v in rec.items() if k != "id"}
            data.setdefault("name", rec.get("title") or rec.get("name"))
            add_node(rid, ntype, data, f"authorities.{key}")
            if ntype != "institution":
                vs = rec.get("verification_status")
                if vs not in VERIFICATION:
                    errors.append(f"{rid}: bad verification_status {vs!r}")
                if vs in {"corroborated", "verified_primary"} and not rec.get("sources"):
                    errors.append(f"{rid}: status {vs} requires at least one source")
            for s in rec.get("sources", []) or []:
                if s not in source_ids:
                    errors.append(f"{rid}: unknown source {s}")
            for b in rec.get("basis", []) or []:
                add_edge(rid, b, "HAS_BASIS", "legislative", rid)


def load_disciplines() -> list[dict]:
    disciplines = []
    for f in sorted(TAX.glob("[0-9]*.yaml")):
        doc = yaml.safe_load(f.read_text())
        blocks = doc["planned"] if "planned" in doc else [doc]
        for blk in blocks:
            d = blk["discipline"]
            add_node(d["id"], "discipline", {k: v for k, v in d.items() if k != "id"}, f.name)
            subs = blk.get("subjects", [])
            for s in subs:
                sid = s["id"]
                sdata = {k: v for k, v in s.items() if k not in ("id", "doctrines")}
                sdata["parent"] = d["id"]
                add_node(sid, "subject", sdata, f.name)
                add_edge(sid, d["id"], "PART_OF", "structural", sid)
                if d.get("status") == "active" and s.get("tier") not in (1, 2, 3):
                    errors.append(f"{sid}: active subject needs tier 1-3")
                if d.get("status") == "active" and not s.get("tier_basis"):
                    errors.append(f"{sid}: missing tier_basis")
                for ref in s.get("legislative_basis", []) or []:
                    add_edge(sid, ref, "HAS_BASIS", "legislative", sid)
                for ref in s.get("key_authorities", []) or []:
                    add_edge(sid, ref, "KEY_AUTHORITY", "judicial", sid)
                for ref in s.get("connections", []) or []:
                    add_edge(sid, ref, "RELATED_TO", "suggested", sid)
                for t in s.get("doctrines", []) or []:
                    tid = t["id"]
                    if not tid.startswith("T-" + sid[2:]):
                        errors.append(f"{tid}: doctrine id does not match parent {sid}")
                    tdata = {k: v for k, v in t.items() if k != "id"}
                    tdata["parent"] = sid
                    add_node(tid, "doctrine", tdata, f.name)
                    add_edge(tid, sid, "PART_OF", "structural", tid)
                    for ref in t.get("basis", []) or []:
                        add_edge(tid, ref, "HAS_BASIS", "legislative", tid)
                    for ref in t.get("authorities", []) or []:
                        add_edge(tid, ref, "KEY_AUTHORITY", "judicial", tid)
                    for ref in t.get("related", []) or []:
                        add_edge(tid, ref, "RELATED_TO", "suggested", tid)
            disciplines.append(blk)
    return disciplines


def check_edges() -> None:
    seen = set()
    for e in edges:
        if e["to"] not in nodes:
            errors.append(f"{e['where']}: reference to unknown id {e['to']}")
        if e["from"] == e["to"]:
            errors.append(f"{e['where']}: self-reference")
        key = (e["from"], e["to"], e["type"])
        if key in seen:
            warnings.append(f"duplicate edge {key}")
        seen.add(key)


def render_markdown(disciplines: list[dict]) -> str:
    def label(i: str) -> str:
        n = nodes.get(i, {})
        nm = n.get("name") or n.get("title") or i
        vs = n.get("verification_status")
        flag = {"corroborated": " ✓", "verified_primary": " ✓✓", "unverified": " (unverified)",
                "requires_investigation": " (⚠ investigate)"}.get(vs, "")
        return f"`{i}` {nm}{flag}"

    L = ["# Sri Lankan Legal Master Taxonomy (generated)", "",
         f"_Generated by `scripts/build_taxonomy.py` on {date.today().isoformat()}. Do not edit by hand; "
         "edit `data/taxonomy/*.yaml` and rebuild._", "",
         "Levels: **L1** discipline → **L2** subject → **L3** doctrine/issue → **L4** authorities "
         "(constitutional provisions, statutes, cases) → **L5** connections.", "",
         "Verification flags on L4 items: ✓✓ verified from primary text · ✓ corroborated · "
         "(unverified) from researcher knowledge, not yet checked · (⚠ investigate) conflicting/in flux.", ""]
    L.append("## Contents\n")
    for blk in disciplines:
        d = blk["discipline"]
        L.append(f"- **{d['id']} {d['name']}** ({d['status']})")
    L.append("")
    for blk in disciplines:
        d = blk["discipline"]
        L += [f"## {d['id']} — {d['name']}", "", f"_Status: {d['status']}._ {d.get('description', '').strip()}", ""]
        for s in blk.get("subjects", []):
            if d["status"] != "active":
                continue
            L += [f"### {s['id']} — {s['name']}", "",
                  f"**Tier {s['tier']}** — {s['tier_basis']}", ""]
            p = s.get("profile", {})
            for k, t in (("meaning", "What it means"), ("significance", "Why it matters"),
                         ("history", "Historical origins"), ("foundations", "Doctrinal foundations"),
                         ("practice", "Practical application")):
                if p.get(k):
                    L.append(f"- **{t}:** {p[k].strip()}")
            if s.get("legislative_basis"):
                L.append("- **Legislative basis:** " + "; ".join(label(x) for x in s["legislative_basis"]))
            if s.get("key_authorities"):
                L.append("- **Key authorities:** " + "; ".join(label(x) for x in s["key_authorities"]))
            if s.get("connections"):
                L.append("- **Connected subjects:** " + ", ".join(label(x) for x in s["connections"]))
            if s.get("open_questions"):
                L.append("- **Open questions:**")
                L += [f"  - {q}" for q in s["open_questions"]]
            L.append("")
            if s.get("doctrines"):
                L.append("| L3 doctrine | Summary | L4 basis / authorities | L5 related |")
                L.append("|---|---|---|---|")
                for t in s["doctrines"]:
                    refs = [*(t.get("basis") or []), *(t.get("authorities") or [])]
                    rel = []
                    for r in t.get("related") or []:
                        if isinstance(r, dict):
                            rel.append(f"{r['to']} ({r.get('type', 'RELATED_TO')}, {r.get('basis', 'suggested')})")
                        else:
                            rel.append(r)
                    L.append(f"| `{t['id']}` {t['name']} | {t['summary']} | "
                             f"{'<br>'.join(label(x) for x in refs) or '—'} | {', '.join(rel) or '—'} |")
                L.append("")
    return "\n".join(L) + "\n"


def main() -> int:
    source_ids = load_sources()
    load_authorities(source_ids)
    disciplines = load_disciplines()
    check_edges()
    watch = yaml.safe_load((ROOT / "data/watch/developments.yaml").read_text())["developments"]
    for d in watch:
        for ref in d.get("affects", []):
            if ref not in nodes:
                errors.append(f"{d['id']}: affects unknown id {ref}")
        for s in d.get("sources", []):
            if s not in source_ids:
                errors.append(f"{d['id']}: unknown source {s}")
        if d.get("verification_status") not in VERIFICATION:
            errors.append(f"{d['id']}: bad verification_status")

    by_type = Counter(n["type"] for n in nodes.values())
    ver = defaultdict(Counter)
    for n in nodes.values():
        if n.get("verification_status"):
            ver[n["type"]][n["verification_status"]] += 1
    tiers = Counter(n.get("tier") for n in nodes.values() if n["type"] == "subject" and n.get("tier"))
    stats = {"nodes_by_type": dict(by_type), "edges": len(edges),
             "edges_by_type": dict(Counter(e["type"] for e in edges)),
             "verification_by_type": {k: dict(v) for k, v in ver.items()},
             "subjects_by_tier": {f"tier_{k}": v for k, v in sorted(tiers.items())},
             "sources": len(source_ids), "watch_items": len(watch)}

    for w in warnings:
        print("WARN ", w)
    if errors:
        for e in errors:
            print("ERROR", e)
        print(f"\n{len(errors)} error(s); outputs not written.")
        return 1

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"generated": date.today().isoformat(), "stats": stats,
                                    "nodes": list(nodes.values()),
                                    "edges": [{k: v for k, v in e.items() if k != "where"} for e in edges]},
                                   indent=2, ensure_ascii=False))
    OUT_MD.write_text(render_markdown(disciplines))
    print(json.dumps(stats, indent=2))
    print(f"OK: wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
