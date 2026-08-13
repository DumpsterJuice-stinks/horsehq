-- Fantasy Quarter Horse Stable — initial schema
--
-- Design notes:
--   * IDs are UUIDs (pgcrypto's gen_random_uuid()) so horses/races ingested from
--     external chart feeds can be assigned client-side without a round trip.
--   * Enumerated values (horse sex, league status, scoring rule types, ...) use
--     CHECK constraints instead of native ENUM types — new race grades/statuses
--     show up often in scraped chart data, and altering a CHECK is a one-line
--     migration where altering a Postgres ENUM requires more ceremony.
--   * Real-world entities (horses, tracks, meets, races, results) are kept
--     separate from fantasy entities (leagues, teams, rosters, scoring) so the
--     same race-chart ingestion pipeline can feed multiple leagues/seasons.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------------
-- Users & auth
-- ---------------------------------------------------------------------------

CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         TEXT NOT NULL UNIQUE,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Real-world racing data (ingested from chart feeds)
-- ---------------------------------------------------------------------------

CREATE TABLE horses (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL,
    registration_number TEXT UNIQUE,
    sex                 TEXT NOT NULL CHECK (sex IN ('colt', 'filly', 'gelding', 'mare', 'stallion')),
    foal_year           SMALLINT NOT NULL,
    sire                TEXT,
    dam                 TEXT,
    trainer             TEXT,
    active              BOOLEAN NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_horses_name ON horses (name);

CREATE TABLE tracks (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name     TEXT NOT NULL UNIQUE,
    location TEXT
);

-- A "meet" is a season at a track (e.g. "2026 Ruidoso Downs Summer Meet").
-- Leagues track exactly one meet, mirroring how a fantasy football league
-- tracks exactly one NFL season.
CREATE TABLE meets (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    track_id   UUID NOT NULL REFERENCES tracks (id),
    name       TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date   DATE NOT NULL,
    CHECK (end_date >= start_date)
);

CREATE INDEX idx_meets_track ON meets (track_id);

CREATE TABLE races (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meet_id         UUID NOT NULL REFERENCES meets (id),
    name            TEXT,
    race_date       DATE NOT NULL,
    race_number     SMALLINT,
    distance_yards  SMALLINT NOT NULL,
    grade           TEXT, -- e.g. 'Grade 1', 'Listed', 'Derby', 'Futurity', 'Trial', 'Allowance', 'Maiden'
    is_stakes       BOOLEAN NOT NULL DEFAULT false,
    purse_cents     BIGINT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (meet_id, race_date, race_number)
);

CREATE INDEX idx_races_meet_date ON races (meet_id, race_date);

CREATE TABLE race_entries (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    race_id           UUID NOT NULL REFERENCES races (id),
    horse_id          UUID NOT NULL REFERENCES horses (id),
    post_position      SMALLINT,
    jockey            TEXT,
    morning_line_odds TEXT,
    UNIQUE (race_id, horse_id)
);

CREATE INDEX idx_race_entries_horse ON race_entries (horse_id);

CREATE TABLE race_results (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    race_entry_id         UUID NOT NULL UNIQUE REFERENCES race_entries (id),
    finish_position       SMALLINT, -- NULL when scratched
    official_time_seconds NUMERIC(6, 3),
    speed_index           SMALLINT,
    margin                TEXT,
    broke_track_record    BOOLEAN NOT NULL DEFAULT false,
    disqualified          BOOLEAN NOT NULL DEFAULT false,
    scratched             BOOLEAN NOT NULL DEFAULT false,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Roster position reference data
-- ---------------------------------------------------------------------------

-- Fantasy roster slots don't map 1:1 to a single horse attribute (a horse can
-- legitimately be draft-eligible for more than one slot type), so this is a
-- flat reference table rather than a computed column on `horses`. Which slots
-- a given league actually uses is configured per-league below.
CREATE TABLE roster_positions (
    id          SMALLINT PRIMARY KEY,
    code        TEXT NOT NULL UNIQUE, -- 'SPRINT_220_350','CLASSIC_400_440','DISTANCE_870','TWO_YO','THREE_YO_UP','BENCH'
    label       TEXT NOT NULL,
    description TEXT,
    sort_order  SMALLINT NOT NULL
);

-- ---------------------------------------------------------------------------
-- Scoring rulesets (shareable/reusable across leagues)
-- ---------------------------------------------------------------------------

CREATE TABLE scoring_rulesets (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name               TEXT NOT NULL,
    is_system_default  BOOLEAN NOT NULL DEFAULT false,
    created_by_user_id UUID REFERENCES users (id),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE scoring_rule_items (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scoring_ruleset_id UUID NOT NULL REFERENCES scoring_rulesets (id) ON DELETE CASCADE,
    rule_type          TEXT NOT NULL CHECK (rule_type IN (
        'WIN', 'PLACE', 'SHOW', 'SI_BONUS_PER_POINT', 'SI_BONUS_THRESHOLD',
        'TRACK_RECORD_BONUS', 'STAKES_MULTIPLIER'
    )),
    points             NUMERIC(6, 2) NOT NULL,
    UNIQUE (scoring_ruleset_id, rule_type)
);

-- ---------------------------------------------------------------------------
-- Leagues, teams, rosters
-- ---------------------------------------------------------------------------

CREATE TABLE leagues (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                 TEXT NOT NULL,
    commissioner_user_id UUID NOT NULL REFERENCES users (id),
    meet_id              UUID NOT NULL REFERENCES meets (id),
    scoring_ruleset_id   UUID NOT NULL REFERENCES scoring_rulesets (id),
    draft_type           TEXT NOT NULL DEFAULT 'snake' CHECK (draft_type IN ('snake', 'auction')),
    max_teams            SMALLINT NOT NULL DEFAULT 8,
    waiver_type          TEXT NOT NULL DEFAULT 'rolling_priority' CHECK (waiver_type IN ('rolling_priority', 'faab')),
    status               TEXT NOT NULL DEFAULT 'draft_pending' CHECK (
        status IN ('draft_pending', 'drafting', 'in_season', 'completed')
    ),
    entry_fee_cents      INTEGER NOT NULL DEFAULT 0,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_leagues_meet ON leagues (meet_id);

-- How many of each roster slot a given league carries, e.g. 2x SPRINT_220_350,
-- 1x DISTANCE_870, 3x BENCH.
CREATE TABLE league_roster_requirements (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    league_id          UUID NOT NULL REFERENCES leagues (id) ON DELETE CASCADE,
    roster_position_id SMALLINT NOT NULL REFERENCES roster_positions (id),
    slot_count         SMALLINT NOT NULL DEFAULT 1 CHECK (slot_count > 0),
    UNIQUE (league_id, roster_position_id)
);

CREATE TABLE teams (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    league_id      UUID NOT NULL REFERENCES leagues (id) ON DELETE CASCADE,
    owner_user_id  UUID NOT NULL REFERENCES users (id),
    name           TEXT NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (league_id, owner_user_id)
);

-- One row per physical roster slot on a team (e.g. "Bench #2"), so a slot can
-- be empty, filled, or swapped without deleting/recreating rows.
--
-- `league_id` is denormalized from `teams.league_id` (kept in sync by the
-- trigger below) purely so the cross-team "one owner per league" constraint
-- further down can be expressed as a plain unique index: a plain
-- UNIQUE(team_id, horse_id) would only stop one team from double-rostering a
-- horse, not stop a *different* team in the same league from also drafting it.
CREATE TABLE roster_slots (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id            UUID NOT NULL REFERENCES teams (id) ON DELETE CASCADE,
    league_id          UUID NOT NULL REFERENCES leagues (id),
    roster_position_id SMALLINT NOT NULL REFERENCES roster_positions (id),
    slot_index         SMALLINT NOT NULL DEFAULT 1, -- distinguishes e.g. Bench #1 vs Bench #2
    horse_id           UUID REFERENCES horses (id),
    acquired_via       TEXT CHECK (acquired_via IN ('draft', 'waiver', 'trade', 'free_agent')),
    acquired_at        TIMESTAMPTZ,
    UNIQUE (team_id, roster_position_id, slot_index)
);

CREATE INDEX idx_roster_slots_horse ON roster_slots (horse_id);

CREATE FUNCTION sync_roster_slot_league_id() RETURNS TRIGGER AS $$
BEGIN
    SELECT league_id INTO NEW.league_id FROM teams WHERE id = NEW.team_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_roster_slots_sync_league_id
    BEFORE INSERT OR UPDATE OF team_id ON roster_slots
    FOR EACH ROW EXECUTE FUNCTION sync_roster_slot_league_id();

-- A horse may only be rostered by one team within a league at a time.
CREATE UNIQUE INDEX idx_roster_slots_one_owner_per_league
    ON roster_slots (league_id, horse_id)
    WHERE horse_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- Draft
-- ---------------------------------------------------------------------------

CREATE TABLE draft_picks (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    league_id    UUID NOT NULL REFERENCES leagues (id) ON DELETE CASCADE,
    team_id      UUID NOT NULL REFERENCES teams (id),
    horse_id     UUID NOT NULL REFERENCES horses (id),
    round        SMALLINT NOT NULL,
    pick_number  SMALLINT NOT NULL, -- overall pick number within the draft
    picked_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (league_id, horse_id),
    UNIQUE (league_id, pick_number)
);

-- ---------------------------------------------------------------------------
-- Waiver wire
-- ---------------------------------------------------------------------------

CREATE TABLE waiver_claims (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    league_id      UUID NOT NULL REFERENCES leagues (id) ON DELETE CASCADE,
    team_id        UUID NOT NULL REFERENCES teams (id),
    add_horse_id   UUID NOT NULL REFERENCES horses (id),
    drop_horse_id  UUID REFERENCES horses (id),
    priority       SMALLINT,
    status         TEXT NOT NULL DEFAULT 'pending' CHECK (
        status IN ('pending', 'approved', 'rejected', 'cancelled')
    ),
    submitted_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    processed_at   TIMESTAMPTZ
);

CREATE INDEX idx_waiver_claims_league_status ON waiver_claims (league_id, status);

-- ---------------------------------------------------------------------------
-- Scoring engine output
-- ---------------------------------------------------------------------------

-- One row per (team, horse, race): the fantasy points a rostered horse earned
-- a team for a specific real-world race, written by the scoring engine worker
-- after each chart is ingested. `breakdown` keeps the line-item math (win
-- bonus, SI bonus, stakes multiplier, ...) for display/audit without having
-- to recompute it from the ruleset later.
CREATE TABLE fantasy_points (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    league_id      UUID NOT NULL REFERENCES leagues (id) ON DELETE CASCADE,
    team_id        UUID NOT NULL REFERENCES teams (id),
    horse_id       UUID NOT NULL REFERENCES horses (id),
    race_id        UUID NOT NULL REFERENCES races (id),
    roster_slot_id UUID REFERENCES roster_slots (id),
    points         NUMERIC(8, 2) NOT NULL,
    breakdown      JSONB NOT NULL DEFAULT '{}'::JSONB,
    computed_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (team_id, horse_id, race_id)
);

CREATE INDEX idx_fantasy_points_league_team ON fantasy_points (league_id, team_id);
