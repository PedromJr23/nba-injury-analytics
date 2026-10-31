WITH base_game_logs AS (
    SELECT
        game_id,
        player_id,
        player_name,
        game_date,
        season,
        team,
        opponent,
        is_home,
        minutes_played,
        pace,
        fg3a
    FROM "nba_injuries"."bronze"."raw_game_logs"
)

SELECT
    game_id,
    player_id,
    player_name,
    game_date,
    season,
    team,
    opponent,
    is_home,
    minutes_played,
    pace,
    fg3a,
    
    -- Carga Aguda: Minutos jogados nos últimos 7 dias
    SUM(minutes_played) OVER (
        PARTITION BY player_id 
        ORDER BY game_date 
        RANGE BETWEEN INTERVAL '6 DAYS' PRECEDING AND CURRENT ROW
    ) AS acute_load_minutes_7d,
    
    -- Carga Crônica: Média móvel de minutos nos últimos 28 dias
    AVG(minutes_played) OVER (
        PARTITION BY player_id 
        ORDER BY game_date 
        RANGE BETWEEN INTERVAL '27 DAYS' PRECEDING AND CURRENT ROW
    ) * 4 AS chronic_load_minutes_28d,
    
    -- Flag de Back-to-Back (jogo em dias consecutivos)
    CASE 
        WHEN LAG(game_date, 1) OVER (PARTITION BY player_id ORDER BY game_date) = game_date - INTERVAL '1 DAY'
        THEN 1 ELSE 0 
    END AS is_back_to_back
FROM base_game_logs