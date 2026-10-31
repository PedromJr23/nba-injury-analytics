WITH raw_tracking AS (
    SELECT
        game_id,
        player_id,
        player_name,
        game_date,
        season,
        distance_miles,
        avg_speed_mph,
        fast_break_points,
        touches
    FROM "nba_injuries"."bronze"."raw_player_tracking"
)

SELECT
    game_id,
    player_id,
    player_name,
    game_date,
    season,
    distance_miles,
    avg_speed_mph,
    
    -- Estimativa de Carga Mecânica (Distância x Velocidade Médio)
    ROUND(distance_miles * avg_speed_mph, 2) AS mechanical_workload_score,
    fast_break_points,
    touches
FROM raw_tracking