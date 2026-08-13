-- Reference data every league can draw on: the five roster positions
-- described in the product pitch, and a "League Default" scoring ruleset
-- implementing the points table from the pitch (Win/Place/Show, Speed Index
-- bonus, track record bonus, stakes multiplier).

INSERT INTO roster_positions (id, code, label, description, sort_order) VALUES
    (1, 'SPRINT_220_350',  '220–350 Yards',    'The pure sprinters',                     1),
    (2, 'CLASSIC_400_440', '400–440 Yards',    'The classic derby/futurity distance',    2),
    (3, 'DISTANCE_870',    '870 Yards',        'The distance hookers',                   3),
    (4, 'TWO_YO',          '2-Year-Olds',      'The futurity stars',                     4),
    (5, 'THREE_YO_UP',     '3-Year-Olds & Up', 'The maturity veterans',                  5),
    (6, 'BENCH',           'Bench',            'Reserve slot, does not score',           6);

WITH default_ruleset AS (
    INSERT INTO scoring_rulesets (name, is_system_default)
    VALUES ('League Default', true)
    RETURNING id
)
INSERT INTO scoring_rule_items (scoring_ruleset_id, rule_type, points)
SELECT id, rule_type, points
FROM default_ruleset, (VALUES
    ('WIN',                  25.0),
    ('PLACE',                15.0),
    ('SHOW',                 10.0),
    ('SI_BONUS_PER_POINT',    1.0), -- +1 fantasy point per Speed Index point over the threshold
    ('SI_BONUS_THRESHOLD',   95.0), -- SI points above this earn the per-point bonus
    ('TRACK_RECORD_BONUS',   15.0),
    ('STAKES_MULTIPLIER',     1.5)  -- applied to a race's total earned points when races.is_stakes = true
) AS rules(rule_type, points);
