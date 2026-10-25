-- ResearchForge canonical schema (PostgreSQL 16). Source of truth for Alembic baseline migration.
-- Conventions: uuid PKs, timestamptz, snake_case, soft-delete via deleted_at on tenant tables.
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS citext;

-- ===== Identity & tenancy =====
CREATE TABLE users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email citext UNIQUE NOT NULL,
  display_name text,
  locale text NOT NULL DEFAULT 'en',
  created_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz
);
CREATE TABLE projects (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid NOT NULL REFERENCES users(id),
  title text NOT NULL,
  description text,
  created_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz
);
CREATE TYPE project_role AS ENUM ('owner','reviewer','viewer');
CREATE TABLE project_members (
  project_id uuid REFERENCES projects(id) ON DELETE CASCADE,
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  role project_role NOT NULL,
  PRIMARY KEY (project_id, user_id)
);

-- ===== Shared public metadata =====
CREATE TABLE works (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  doi text UNIQUE,                       -- normalized: lowercase, no URL prefix
  openalex_id text UNIQUE,
  pmid text UNIQUE,
  title text NOT NULL,
  title_norm text GENERATED ALWAYS AS (lower(regexp_replace(title,'[^a-zA-Z0-9]+',' ','g'))) STORED,
  abstract text,
  year int,
  work_type text,                        -- article, review, preprint, ...
  language text,
  venue_id uuid,                         -- -> journals.id (nullable)
  venue_name text,
  is_oa boolean,
  oa_url text,
  cited_by_count int,
  retracted boolean NOT NULL DEFAULT false,
  retraction_checked_at timestamptz,
  raw jsonb,                             -- minimal raw payload per source (size-capped)
  provenance jsonb NOT NULL DEFAULT '{}',-- {field: {source, fetched_at}}
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX works_title_trgm ON works USING gin (title_norm gin_trgm_ops);
CREATE INDEX works_year ON works (year);
CREATE INDEX works_fts ON works USING gin (to_tsvector('simple', coalesce(title,'')||' '||coalesce(abstract,'')));

CREATE TABLE authors (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  openalex_id text UNIQUE, orcid text UNIQUE, display_name text NOT NULL
);
CREATE TABLE work_authors (
  work_id uuid REFERENCES works(id) ON DELETE CASCADE,
  author_id uuid REFERENCES authors(id),
  position int NOT NULL, raw_name text,
  PRIMARY KEY (work_id, position)
);
CREATE TABLE work_citations (               -- citing -> cited
  citing_work_id uuid REFERENCES works(id) ON DELETE CASCADE,
  cited_work_id  uuid REFERENCES works(id) ON DELETE CASCADE,
  PRIMARY KEY (citing_work_id, cited_work_id)
);

-- ===== Journals (shared) =====
CREATE TABLE journals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  openalex_id text UNIQUE, issn_l text, issns text[],
  title text NOT NULL, publisher text, country text,
  scope_text text, languages text[],
  is_oa boolean, in_doaj boolean, apc_usd numeric, apc_note text,
  scopus_quartile text,        -- Q1..Q4 or NULL (only if licence allows storing)
  sinta_rank text,             -- S1..S6 or NULL (verify terms)
  guidelines_url text,
  profile_embedding vector(1024),
  data_as_of date NOT NULL,    -- freshness label shown to users
  provenance jsonb NOT NULL DEFAULT '{}'
);
ALTER TABLE works ADD CONSTRAINT works_venue_fk FOREIGN KEY (venue_id) REFERENCES journals(id);

-- ===== Library (tenant) =====
CREATE TABLE library_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  work_id uuid NOT NULL REFERENCES works(id),
  added_by uuid REFERENCES users(id),
  import_batch_id uuid,
  user_notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  UNIQUE (project_id, work_id)
);
CREATE TABLE collections (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  parent_id uuid REFERENCES collections(id), name text NOT NULL
);
CREATE TABLE collection_items (
  collection_id uuid REFERENCES collections(id) ON DELETE CASCADE,
  library_item_id uuid REFERENCES library_items(id) ON DELETE CASCADE,
  PRIMARY KEY (collection_id, library_item_id)
);
CREATE TABLE tags (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, name text NOT NULL, UNIQUE(project_id,name));
CREATE TABLE library_item_tags (library_item_id uuid REFERENCES library_items(id) ON DELETE CASCADE, tag_id uuid REFERENCES tags(id) ON DELETE CASCADE, PRIMARY KEY(library_item_id, tag_id));
CREATE TABLE import_batches (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  format text NOT NULL, filename text, source_label text,   -- e.g. "PubMed search 2026-10-24"
  stats jsonb NOT NULL DEFAULT '{}', report jsonb NOT NULL DEFAULT '[]',
  created_by uuid REFERENCES users(id), created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE user_files (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  library_item_id uuid REFERENCES library_items(id) ON DELETE SET NULL,
  storage_key text NOT NULL, mime text NOT NULL, bytes bigint NOT NULL, sha256 text NOT NULL,
  text_extracted boolean NOT NULL DEFAULT false, uploaded_by uuid REFERENCES users(id),
  created_at timestamptz NOT NULL DEFAULT now(), deleted_at timestamptz
);
CREATE TABLE dedup_candidates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  work_a uuid NOT NULL REFERENCES works(id), work_b uuid NOT NULL REFERENCES works(id),
  score real NOT NULL, status text NOT NULL DEFAULT 'pending',  -- pending|merged|kept_separate
  decided_by uuid REFERENCES users(id), decided_at timestamptz,
  merge_snapshot jsonb                                          -- enables undo
);

-- ===== Screening (tenant, append-only decisions) =====
CREATE TABLE review_protocols (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  version int NOT NULL, question text NOT NULL, framework text,   -- PICO|PEO|SPIDER|custom
  inclusion jsonb NOT NULL, exclusion jsonb NOT NULL,
  databases jsonb, date_from date, date_to date, blind_mode boolean NOT NULL DEFAULT true,
  created_by uuid REFERENCES users(id), created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (project_id, version)
);
CREATE TYPE screening_stage AS ENUM ('title_abstract','full_text');
CREATE TYPE screening_verdict AS ENUM ('include','exclude','maybe');
CREATE TABLE exclusion_reasons (
  id serial PRIMARY KEY, project_id uuid REFERENCES projects(id) ON DELETE CASCADE, -- NULL = global default
  code text NOT NULL, label text NOT NULL
);
CREATE TABLE screening_decisions (            -- APPEND ONLY (no UPDATE/DELETE grants)
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  library_item_id uuid NOT NULL REFERENCES library_items(id),
  stage screening_stage NOT NULL, reviewer_id uuid NOT NULL REFERENCES users(id),
  verdict screening_verdict NOT NULL, reason_id int REFERENCES exclusion_reasons(id),
  note text, protocol_version int NOT NULL,
  ai_suggestion_id uuid,                     -- links suggestion shown (if any)
  supersedes_id uuid REFERENCES screening_decisions(id),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX sd_lookup ON screening_decisions (project_id, stage, library_item_id);
CREATE TABLE screening_resolutions (          -- conflict resolution, append-only
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  library_item_id uuid NOT NULL REFERENCES library_items(id), stage screening_stage NOT NULL,
  resolver_id uuid NOT NULL REFERENCES users(id), verdict screening_verdict NOT NULL,
  reason_id int REFERENCES exclusion_reasons(id), created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE ai_suggestions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  library_item_id uuid NOT NULL REFERENCES library_items(id), stage screening_stage NOT NULL,
  suggested_verdict screening_verdict NOT NULL, rationale text NOT NULL, criteria_matched jsonb,
  model text NOT NULL, prompt_hash text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);

-- ===== Retrieval & synthesis =====
CREATE TABLE chunks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scope text NOT NULL,                       -- 'public_work' | 'user_file'
  work_id uuid REFERENCES works(id) ON DELETE CASCADE,
  user_file_id uuid REFERENCES user_files(id) ON DELETE CASCADE,
  project_id uuid REFERENCES projects(id) ON DELETE CASCADE,   -- required when scope='user_file'
  ordinal int NOT NULL, text text NOT NULL, section text,
  embedding vector(1024), embedding_model text NOT NULL,
  CHECK ((scope='public_work' AND work_id IS NOT NULL) OR (scope='user_file' AND user_file_id IS NOT NULL AND project_id IS NOT NULL))
);
CREATE INDEX chunks_vec ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX chunks_fts ON chunks USING gin (to_tsvector('simple', text));
CREATE TABLE extractions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  library_item_id uuid NOT NULL REFERENCES library_items(id),
  fields jsonb NOT NULL,                     -- {population, design, intervention, outcome, finding, limitations}
  evidence jsonb NOT NULL,                   -- {field: [chunk_id,...]}
  edited_by_user boolean NOT NULL DEFAULT false, model text, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE synthesis_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES users(id), question text NOT NULL,
  status text NOT NULL,                      -- queued|running|done|refused|failed
  retrieval_config jsonb NOT NULL, model text NOT NULL, prompt_hashes jsonb NOT NULL,
  answer_md text, claims jsonb,              -- [{id,text,citations:[chunk_id],verified:bool,verdict}]
  refusal_reason text, cost_usd numeric(10,4), tokens_in int, tokens_out int,
  created_at timestamptz NOT NULL DEFAULT now(), finished_at timestamptz
);
CREATE TABLE synthesis_run_chunks (run_id uuid REFERENCES synthesis_runs(id) ON DELETE CASCADE, chunk_id uuid REFERENCES chunks(id), rank int, score real, PRIMARY KEY(run_id, chunk_id));

-- ===== Integrity =====
CREATE TABLE ai_usage_log (                  -- feeds disclosure statement
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES users(id),
  feature text NOT NULL, stage text NOT NULL,         -- e.g. synthesis / literature_review
  model text NOT NULL, purpose text NOT NULL, human_reviewed boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE reference_checks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  input_ref text NOT NULL, resolved_work_id uuid REFERENCES works(id),
  status text NOT NULL,                      -- verified|doi_unresolved|metadata_mismatch|retracted|not_found
  detail jsonb, checked_at timestamptz NOT NULL DEFAULT now()
);

-- ===== Platform =====
CREATE TABLE jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), kind text NOT NULL, dedupe_key text UNIQUE,
  project_id uuid REFERENCES projects(id), status text NOT NULL, payload jsonb, result jsonb,
  attempts int NOT NULL DEFAULT 0, created_at timestamptz NOT NULL DEFAULT now(), finished_at timestamptz
);
CREATE TABLE usage_quota (user_id uuid REFERENCES users(id), week date, credits_used int NOT NULL DEFAULT 0, PRIMARY KEY(user_id, week));
CREATE TABLE audit_events (
  id bigserial PRIMARY KEY, project_id uuid, user_id uuid, action text NOT NULL,
  entity text, entity_id text, meta jsonb, ip inet, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE source_cache (key text PRIMARY KEY, source text NOT NULL, payload jsonb NOT NULL, fetched_at timestamptz NOT NULL, ttl_seconds int NOT NULL);

-- ===== v0.2: Literature mapping & positioning (MAP bundle) =====
ALTER TABLE user_files ADD COLUMN retention_mode text NOT NULL DEFAULT 'retain'
  CHECK (retention_mode IN ('retain','extract_only'));   -- LIB-017: extract_only deletes original after extraction

CREATE TABLE map_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  kind text NOT NULL CHECK (kind IN ('topic_map','lineage')),
  scope jsonb NOT NULL,                    -- {type:'library_subset'|'search', ids:[...], query?}
  params jsonb NOT NULL,                   -- seed, algorithm versions, thresholds, weights
  embedding_model text NOT NULL, code_version text NOT NULL,
  status text NOT NULL, record_count int, excluded jsonb,   -- excluded: [{work_id, reason}]
  created_by uuid REFERENCES users(id), created_at timestamptz NOT NULL DEFAULT now(), finished_at timestamptz
);
CREATE TABLE map_clusters (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id uuid NOT NULL REFERENCES map_runs(id) ON DELETE CASCADE,
  label text NOT NULL, label_source text NOT NULL CHECK (label_source IN ('keywords','llm_constrained')),
  keywords text[] NOT NULL, size int NOT NULL, is_other boolean NOT NULL DEFAULT false,
  centroid vector(1024), language_mix jsonb
);
CREATE TABLE map_cluster_members (
  cluster_id uuid REFERENCES map_clusters(id) ON DELETE CASCADE,
  work_id uuid REFERENCES works(id), membership_score real,
  PRIMARY KEY (cluster_id, work_id)
);
CREATE TABLE lineage_nodes (
  run_id uuid REFERENCES map_runs(id) ON DELETE CASCADE,
  work_id uuid REFERENCES works(id),
  family_id uuid REFERENCES map_clusters(id),             -- family = cluster of a lineage run; NULL => Unplaced
  role text NOT NULL CHECK (role IN ('root','placed','needs_review','unplaced')),
  parent_work_id uuid REFERENCES works(id),
  confidence real, confidence_band text CHECK (confidence_band IN ('high','medium','low')),
  evidence jsonb NOT NULL,                                 -- {cit,sem,kw,chr,shared_concepts[],reason_codes[]}
  user_override jsonb,                                     -- {by,at,previous:{parent,family}} (NULL = machine result)
  missing_flags text[] NOT NULL DEFAULT '{}',
  PRIMARY KEY (run_id, work_id)
);
CREATE TABLE lineage_edges (
  run_id uuid REFERENCES map_runs(id) ON DELETE CASCADE,
  parent_work_id uuid REFERENCES works(id), child_work_id uuid REFERENCES works(id),
  score real NOT NULL, evidence jsonb NOT NULL,
  PRIMARY KEY (run_id, parent_work_id, child_work_id)
);
CREATE TABLE positioning_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  lineage_run_id uuid NOT NULL REFERENCES map_runs(id),
  manuscript_hash text NOT NULL,                           -- never the text unless retain_text
  manuscript_text text,                                    -- NULL unless user opted in
  retain_text boolean NOT NULL DEFAULT false,
  closest_family_id uuid REFERENCES map_clusters(id), results jsonb NOT NULL,  -- parents, components, concepts
  created_by uuid REFERENCES users(id), created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (retain_text OR manuscript_text IS NULL)
);
CREATE TABLE gap_signals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id uuid NOT NULL REFERENCES map_runs(id) ON DELETE CASCADE,
  kind text NOT NULL CHECK (kind IN ('unresolved_condition','future_work','lineage_gap','data_quality')),
  work_id uuid REFERENCES works(id), chunk_id uuid REFERENCES chunks(id),
  excerpt text CHECK (excerpt IS NULL OR char_length(excerpt) <= 300),
  frequency int NOT NULL DEFAULT 1, extractor_version text NOT NULL, confidence real,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX lineage_nodes_family ON lineage_nodes (run_id, family_id);
