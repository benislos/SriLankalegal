"""Integration tests for the Phase 2 database. Run: python3 -m pytest -q tests/ (after load_db.py)."""
import os

import psycopg
import pytest

DSN = os.environ.get("KMS_DSN", "postgresql://kms:kms@localhost/sl_legal_kms")


@pytest.fixture
def cur():
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as c:
            c.execute("SET search_path = kms")
            yield c
        conn.rollback()  # every test leaves the DB unchanged


def test_full_text_search_finds_public_trust(cur):
    cur.execute("SELECT id FROM nodes WHERE search @@ websearch_to_tsquery('english','public trust') ")
    ids = {r[0] for r in cur.fetchall()}
    assert {"T-ADM-01-03", "CASE-BULANKULAMA-2000"} <= ids


def test_navigate_provision_to_cases_to_doctrines(cur):
    # Art 126 -> doctrines resting on it -> cases cited for those doctrines
    cur.execute("""SELECT DISTINCT c.to_id FROM edges b JOIN edges c ON c.from_id=b.from_id
                   WHERE b.to_id='CP-ART-126' AND b.rel_type='HAS_BASIS' AND c.rel_type='KEY_AUTHORITY'""")
    cases = {r[0] for r in cur.fetchall()}
    assert "CASE-SRIYANI-SILVA-2003" in cases


def test_case_connects_to_multiple_doctrines(cur):
    cur.execute("SELECT count(DISTINCT from_id) FROM edges WHERE to_id='CASE-BULANKULAMA-2000' AND rel_type='KEY_AUTHORITY'")
    assert cur.fetchone()[0] >= 3


def test_indirect_connection_discovery(cur):
    # Two-hop path between a constitutional doctrine and an environmental doctrine
    cur.execute("""WITH RECURSIVE walk(node, depth, path) AS (
                     SELECT 'T-CON-03-04'::text, 0, ARRAY['T-CON-03-04']
                     UNION ALL
                     SELECT CASE WHEN e.from_id=w.node THEN e.to_id ELSE e.from_id END, w.depth+1,
                            w.path || CASE WHEN e.from_id=w.node THEN e.to_id ELSE e.from_id END
                     FROM walk w JOIN edges e ON (e.from_id=w.node OR e.to_id=w.node) AND e.rel_type <> 'PART_OF'
                     WHERE w.depth < 3)
                   SELECT min(depth) FROM walk WHERE node='T-EMR-02-01'""")
    assert cur.fetchone()[0] is not None


def test_history_is_preserved(cur):
    cur.execute("UPDATE nodes SET description='edited for test' WHERE id='T-CON-04-11'")
    cur.execute("SELECT op, old_row->>'description' FROM change_history WHERE row_id='T-CON-04-11'")
    op, old = cur.fetchone()
    assert op == "UPDATE" and old and old != "edited for test"


def test_cannot_mark_verified_without_source(cur):
    # Pick any case node that still has no source (fixtures change as records are verified).
    cur.execute("""SELECT n.id FROM nodes n WHERE n.id LIKE 'CASE-%'
                   AND NOT EXISTS (SELECT 1 FROM node_sources s WHERE s.node_id = n.id) LIMIT 1""")
    row = cur.fetchone()
    assert row, "no unsourced case node left to test against"
    cur.execute("UPDATE nodes SET verification_status='verified_primary' WHERE id=%s", (row[0],))
    with pytest.raises(psycopg.errors.RaiseException):
        cur.execute("SET CONSTRAINTS ALL IMMEDIATE")


def test_no_duplicate_edges(cur):
    with pytest.raises(psycopg.errors.UniqueViolation):
        cur.execute("""INSERT INTO edges(from_id,to_id,rel_type,basis)
                       SELECT from_id,to_id,rel_type,basis FROM edges LIMIT 1""")


def test_research_tracker_seeded(cur):
    cur.execute("SELECT count(*), count(*) FILTER (WHERE status='requires_verification') FROM research_questions")
    total, rv = cur.fetchone()
    assert total > 40 and rv > 0
