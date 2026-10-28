-- ResearchForge schema DELTA v0.4 (apply after 03-data-model.sql). Postgres 16, pgvector >= 0.7.
-- Purpose: access model (17), truthful AI accounting, scale (16), journal integrity.

-- ===== Access model =====
ALTER TABLE users ADD COLUMN is_system_admin boolean NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','disabled','invited'));
ALTER TABLE users ADD COLUMN last_login_at timestamptz;

CREATE TABLE instance_settings (
  key text PRIMARY KEY,                    -- access_mode, registration, allowed_email_domains, llm_budget_usd_month ...
  value jsonb NOT NULL,
  updated_by uuid REFERENCES users(id),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE auth_magic_links (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash bytea NOT NULL UNIQUE,        -- sha256 of random token; token itself never stored
  expires_at timestamptz NOT NULL,
  used_at timestamptz,                     -- single use
  requested_ip inet,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE auth_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash bytea NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  last_seen_at timestamptz NOT NULL DEFAULT now(),
  idle_expires_at timestamptz NOT NULL,    -- default now() + 12h, slides
  abs_expires_at timestamptz NOT NULL,     -- default now() + 7d
  step_up_at timestamptz,                  -- last strong re-auth, admin actions need < 10 min
  revoked_at timestamptz,
  user_agent text, ip inet
);
CREATE INDEX auth_sessions_user ON auth_sessions (user_id) WHERE revoked_at IS NULL;
CREATE TABLE webauthn_credentials (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  credential_id bytea NOT NULL UNIQUE, public_key bytea NOT NULL,
  sign_count bigint NOT NULL DEFAULT 0, transports text[], label text,
  created_at timestamptz NOT NULL DEFAULT now(), last_used_at timestamptz
);
CREATE TABLE recovery_codes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  code_hash bytea NOT NULL, used_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE invitations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(id) ON DELETE CASCADE,   -- NULL = instance-level invite
  email citext NOT NULL, role project_role,
  token_hash bytea NOT NULL UNIQUE,
  expires_at timestamptz NOT NULL, accepted_at timestamptz, revoked_at timestamptz,
  created_by uuid NOT NULL REFERENCES users(id), created_at timestamptz NOT NULL DEFAULT now()
);

-- ===== Truthful AI accounting (ETH-016) =====
ALTER TABLE ai_usage_log ADD COLUMN mode text NOT NULL DEFAULT 'llm' CHECK (mode IN ('llm','rule_based'));
ALTER TABLE ai_usage_log ADD COLUMN provider text;
ALTER TABLE ai_usage_log ADD COLUMN request_id text;
ALTER TABLE ai_usage_log ADD CONSTRAINT ai_usage_log_real_model CHECK (mode = 'rule_based' OR (provider IS NOT NULL AND model <> ''));
CREATE TABLE llm_usage_events (
  id uuid DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL, project_id uuid,
  feature text NOT NULL, task text NOT NULL,
  provider text NOT NULL, model text NOT NULL,
  tokens_in int NOT NULL, tokens_out int NOT NULL,
  cost_usd numeric(12,6) NOT NULL, request_id text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);               -- monthly partitions created by a maintenance job
CREATE INDEX llm_usage_user_time ON llm_usage_events (user_id, created_at DESC);

-- ===== Audit and events at scale =====
ALTER TABLE audit_events ADD COLUMN actor_is_admin boolean NOT NULL DEFAULT false;
ALTER TABLE audit_events ADD COLUMN request_id text;
CREATE INDEX audit_events_time ON audit_events (created_at DESC);
CREATE INDEX audit_events_actor ON audit_events (user_id, created_at DESC);

-- ===== Journal integrity (JRN-013): articles reference real works, never embedded JSON =====
ALTER TABLE journals ADD COLUMN source_record_id text;
ALTER TABLE journals ADD COLUMN fetched_at timestamptz;
CREATE TABLE journal_articles (
  journal_id uuid NOT NULL REFERENCES journals(id) ON DELETE CASCADE,
  work_id uuid NOT NULL REFERENCES works(id) ON DELETE CASCADE,
  PRIMARY KEY (journal_id, work_id)
);
CREATE INDEX journal_articles_work ON journal_articles (work_id);

-- ===== Source mirror and cache (ADR-011) =====
CREATE TABLE source_mirror_state (
  source text PRIMARY KEY,                  -- 'openalex_snapshot'
  snapshot_date date, scope jsonb,          -- e.g. {"years":[2015,2026],"types":["article","review"]}
  loaded_rows bigint, loaded_at timestamptz
);

-- ===== Retention =====
CREATE TABLE retention_policies (
  entity text PRIMARY KEY, keep_days int NOT NULL, hard_delete_after_days int, updated_at timestamptz NOT NULL DEFAULT now()
);

-- ===== Vector storage at scale (apply when pgvector >= 0.7) =====
-- ALTER TABLE chunks ADD COLUMN embedding_h halfvec(1024);
-- CREATE INDEX chunks_vec_h ON chunks USING hnsw (embedding_h halfvec_cosine_ops) WITH (m = 16, ef_construction = 64);
-- Backfill in batches, switch reads, then drop the full-precision column in a later migration (expand/contract).

-- ===== Row-level security template for tenant tables (ENG-008, QAS-009) =====
-- ALTER TABLE library_items ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY tenant_isolation ON library_items
--   USING (project_id IN (SELECT project_id FROM project_members WHERE user_id = current_setting('app.user_id')::uuid));
-- Set `SET LOCAL app.user_id = '<uuid>'` at the start of each request transaction. Apply to every table with project_id.
