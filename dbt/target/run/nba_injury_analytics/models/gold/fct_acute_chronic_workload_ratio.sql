
    

    create  table
      "nba_injuries"."main_gold"."fct_acute_chronic_workload_ratio__dbt_tmp"
  
    
    as (
      ﻿WITH workload AS (
    SELECT * FROM "nba_injuries"."main_silver"."stg_player_workload"
),

injuries AS (
    SELECT * FROM "nba_injuries"."main_silver"."stg_injuries"
)

SELECT
    i.injury_id,
    i.player_name,
    i.injury_date,
    i.season,
    i.injury_category,
    i.notes,
    
    w.acute_load_minutes_7d,
    w.chronic_load_minutes_28d,
    
    -- Razão Carga Aguda : Carga Crônica (ACWR)
    -- ACWR > 1.5 indica pico de sobrecarga
    ROUND(
        w.acute_load_minutes_7d / NULLIF(w.chronic_load_minutes_28d / 4.0, 0), 
        2
    ) AS acwr_ratio,
    
    w.is_back_to_back
FROM injuries i
LEFT JOIN workload w 
    ON i.player_name = w.player_name 
   AND i.injury_date = w.game_date
    );
    
  