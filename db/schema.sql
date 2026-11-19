-- Sri Lankan Legal KMS - PostgreSQL schema (Phase 2)
-- Design: one generic graph (nodes + typed edges) for navigation and search, plus typed detail
-- tables for entities that need structured fields (cases, legislation). Every change to a node,
-- case record or legislation record is preserved in change_history (triggers below).
-- The YAML under data/ is the version-controlled source of truth; scripts/load_db.py rebuilds
-- this database from it, and scripts/export_db.py writes database-originated changes back out.

BEGIN;

DROP SCHEMA IF EXISTS kms CASCADE;
CREATE SCHEMA kms;
SET search_path = kms;

CREATE TYPE verification AS ENUM ('verified_primary', 'corroborated', 'unverified', 'requires_investigation');
CREATE TYPE rel_basis   AS ENUM ('judicial', 'legislative', 'academic', 'suggested', 'structural');

-- ---------------------------------------------------------------- sources
CREATE TABLE sources (
    id            text PRIMARY KEY CHECK (id ~ '^SRC-\d{4}$'),
    title         text NOT NULL,
    url           text NOT NULL,
    source_class  text NOT NULL CHECK (source_class IN
                  ('primary_official','primary_reproduced','secondary_scholarly','secondary_news','ngo_ig')),
    accessed_via  text NOT NULL CHECK (accessed_via IN ('search_index','full_text','print')),
    accessed      date NOT NULL,
    notes         text
);

-- ---------------------------------------------------------------- nodes (every entity)
CREATE TABLE nodes (
    id                  text PRIMARY KEY,
    node_type           text NOT NULL CHECK (node_type IN
                        ('discipline','subject','doctrine','constitutional_provision','amendment',
                         'legislation','treaty','case','institution','academic_publication',
                         'research_question','lesson','principle')),
    name                text NOT NULL,
    description         text,
    parent_id           text REFERENCES nodes(id) DEFERRABLE INITIALLY DEFERRED,
    tier                smallint CHECK (tier BETWEEN 1 AND 3),
    status              text,                      -- discipline active/planned; legislation in_force etc.
    verification_status verification,
    attrs               jsonb NOT NULL DEFAULT '{}',  -- profile, open_questions, notes ...
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now(),
    search              tsvector GENERATED ALWAYS AS (
                          setweight(to_tsvector('english', coalesce(name,'')), 'A') ||
                          setweight(to_tsvector('english', coalesce(description,'')), 'B') ||
                          setweight(jsonb_to_tsvector('english', attrs, '["string"]'), 'C')) STORED
);
CREATE INDEX nodes_type_idx   ON nodes(node_type);
CREATE INDEX nodes_parent_idx ON nodes(parent_id);
CREATE INDEX nodes_search_idx ON nodes USING gin(search);

CREATE TABLE node_sources (
    node_id   text REFERENCES nodes(id) ON DELETE CASCADE,
    source_id text REFERENCES sources(id),
    PRIMARY KEY (node_id, source_id)
);

-- A record may only claim corroborated/verified_primary if it cites a source.
CREATE FUNCTION check_verification_has_source() RETURNS trigger AS $$
BEGIN
  IF NEW.verification_status IN ('corroborated','verified_primary')
     AND NOT EXISTS (SELECT 1 FROM node_sources WHERE node_id = NEW.id) THEN
    RAISE EXCEPTION 'node % cannot be % without a source in node_sources', NEW.id, NEW.verification_status;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
CREATE CONSTRAINT TRIGGER nodes_verification_source
  AFTER INSERT OR UPDATE OF verification_status ON nodes
  DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_verification_has_source();

-- ---------------------------------------------------------------- edges (typed relationships)
CREATE TABLE edges (
    id         bigserial PRIMARY KEY,
    from_id    text NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    to_id      text NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    rel_type   text NOT NULL CHECK (rel_type IN
               ('ESTABLISHES','INTERPRETS','APPLIES','REGULATES','DERIVES_FROM','LIMITS','QUALIFIES',
                'DISTINGUISHES','OVERRULES','MODIFIES','CITES','INFLUENCES','RELATED_TO','CONTRADICTS',
                'DEVELOPS','REAFFIRMS','PART_OF','HAS_BASIS','KEY_AUTHORITY','FOLLOWS','COVERS')),
    basis      rel_basis NOT NULL,
    note       text,
    source_ids text[] NOT NULL DEFAULT '{}',
    discovered_on date NOT NULL DEFAULT current_date,   -- feeds "Connections discovered today"
    lesson_id  text REFERENCES nodes(id),                -- lesson that introduced the link, if any
    CHECK (from_id <> to_id),
    UNIQUE (from_id, to_id, rel_type)
);
CREATE INDEX edges_from_idx ON edges(from_id);
CREATE INDEX edges_to_idx   ON edges(to_id);

-- ---------------------------------------------------------------- case law (brief s.6, 16 fields)
CREATE TABLE case_records (
    node_id            text PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    full_name          text NOT NULL,                 -- 1
    citation           text,                          -- 2
    court              text,                          -- 3
    year               smallint,                      -- 4
    application_no     text,
    decided_on         date,
    bench              text[],
    material_facts     text,                          -- 5
    legal_issues       text[],                        -- 6
    decision           text,                          -- 7
    ratio              text,                          -- 8
    obiter             text[],                        -- 9
    principles         text[],                        -- 10
    subsequent_treatment text,                        -- 11 (11-14 also as edges FOLLOWS/DISTINGUISHES/OVERRULES/MODIFIES)
    authority_weight   text CHECK (authority_weight IN
                       ('binding_sc','binding_pc_historical','persuasive_lk','persuasive_comparative')),
    field_status       jsonb NOT NULL DEFAULT '{}'    -- per-field verification, e.g. {"ratio":"unverified"}
);
-- 15 (legislation) and 16 (doctrines) are edges HAS_BASIS / ESTABLISHES / APPLIES.

-- ---------------------------------------------------------------- legislation (brief s.5, 10 fields)
CREATE TABLE legislation_records (
    node_id          text PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    official_title   text NOT NULL,                   -- 1
    year             smallint,                        -- 2
    act_number       text,                            -- 3
    key_provisions   jsonb NOT NULL DEFAULT '[]',     -- 4  [{section, summary, status}]
    purpose          text,                            -- 5
    significance     text,                            -- 6
    -- 7 relationships: edges
    amendment_history jsonb NOT NULL DEFAULT '[]',    -- 8  [{act, year, effect}]
    repeal_status    text,                            -- 9
    current_status   text,                            -- 10
    status_as_of     date
);

-- ---------------------------------------------------------------- learning system
CREATE TABLE lessons (
    node_id      text PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    lesson_date  date NOT NULL UNIQUE,
    lesson_kind  text NOT NULL CHECK (lesson_kind IN ('new_topic','continuation','revision','development_update','weekly_review','monthly_review')),
    topic_id     text REFERENCES nodes(id),
    body_md      text NOT NULL,
    read_at      timestamptz
);

CREATE TABLE research_questions (
    node_id      text PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    question     text NOT NULL,
    category     text,
    status       text NOT NULL DEFAULT 'not_started' CHECK (status IN
                 ('not_started','under_investigation','answered','requires_verification','further_research_required')),
    answer_md    text,
    raised_in    text REFERENCES nodes(id)
);

CREATE TABLE learning_progress (
    topic_id      text PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    state         text NOT NULL DEFAULT 'not_started' CHECK (state IN ('not_started','in_progress','completed','revise')),
    first_studied date,
    last_studied  date,
    times_revised int NOT NULL DEFAULT 0,
    confidence    smallint CHECK (confidence BETWEEN 1 AND 5)
);

CREATE TABLE developments (
    id               text PRIMARY KEY CHECK (id ~ '^DEV-\d{4}-\d{3}$'),
    dev_date         date NOT NULL,
    kind             text NOT NULL,
    title            text NOT NULL,
    affects          text[] NOT NULL DEFAULT '{}',
    source_ids       text[] NOT NULL DEFAULT '{}',
    settled_effect   text NOT NULL,
    verification_status verification NOT NULL,
    follow_up        text
);

-- ---------------------------------------------------------------- history (brief s.18: preserve changes)
CREATE TABLE change_history (
    id          bigserial PRIMARY KEY,
    table_name  text NOT NULL,
    row_id      text NOT NULL,
    op          text NOT NULL,
    changed_at  timestamptz NOT NULL DEFAULT now(),
    old_row     jsonb,
    new_row     jsonb
);
CREATE INDEX change_history_row_idx ON change_history(table_name, row_id);

CREATE FUNCTION log_change() RETURNS trigger AS $$
DECLARE rid text;
BEGIN
  rid := coalesce(to_jsonb(NEW)->>'id', to_jsonb(NEW)->>'node_id', to_jsonb(OLD)->>'id', to_jsonb(OLD)->>'node_id');
  IF TG_OP = 'UPDATE' AND to_jsonb(OLD) - 'updated_at' - 'search' = to_jsonb(NEW) - 'updated_at' - 'search' THEN
    RETURN NEW;  -- no material change
  END IF;
  INSERT INTO change_history(table_name, row_id, op, old_row, new_row)
  VALUES (TG_TABLE_NAME, rid, TG_OP,
          CASE WHEN TG_OP <> 'INSERT' THEN to_jsonb(OLD) - 'search' END,
          CASE WHEN TG_OP <> 'DELETE' THEN to_jsonb(NEW) - 'search' END);
  IF TG_OP = 'UPDATE' AND TG_TABLE_NAME = 'nodes' THEN NEW.updated_at := now(); END IF;
  RETURN coalesce(NEW, OLD);
END $$ LANGUAGE plpgsql;

CREATE TRIGGER nodes_history BEFORE UPDATE OR DELETE ON nodes FOR EACH ROW EXECUTE FUNCTION log_change();
CREATE TRIGGER case_history  AFTER UPDATE OR DELETE ON case_records FOR EACH ROW EXECUTE FUNCTION log_change();
CREATE TRIGGER leg_history   AFTER UPDATE OR DELETE ON legislation_records FOR EACH ROW EXECUTE FUNCTION log_change();
CREATE TRIGGER rq_history    AFTER UPDATE OR DELETE ON research_questions FOR EACH ROW EXECUTE FUNCTION log_change();

-- ---------------------------------------------------------------- convenience views
CREATE VIEW v_stats AS
SELECT
  (SELECT count(*) FROM nodes WHERE node_type IN ('subject','doctrine'))                    AS total_topics,
  (SELECT count(*) FROM learning_progress WHERE state = 'completed')                         AS topics_completed,
  (SELECT count(*) FROM nodes WHERE node_type = 'case')                                      AS cases_indexed,
  (SELECT count(*) FROM nodes WHERE node_type IN ('legislation','constitutional_provision','amendment','treaty')) AS legislation_indexed,
  (SELECT count(*) FROM nodes WHERE node_type IN ('doctrine','principle'))                   AS principles_documented,
  (SELECT count(*) FROM edges WHERE rel_type NOT IN ('PART_OF'))                             AS graph_connections,
  (SELECT count(*) FROM research_questions WHERE status <> 'answered')                       AS open_research_questions;

CREATE VIEW v_verification AS
SELECT node_type, verification_status, count(*) FROM nodes
WHERE verification_status IS NOT NULL GROUP BY 1,2 ORDER BY 1,2;

COMMIT;
