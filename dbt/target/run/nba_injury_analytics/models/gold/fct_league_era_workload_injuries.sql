
    

    create  table
      "nba_injuries"."main_gold"."fct_league_era_workload_injuries__dbt_tmp"
  
    
    as (
      ﻿WITH season_workload AS (
    SELECT
        season,
        ROUND(AVG(pace), 2) AS avg_league_pace,
        ROUND(AVG(fg3a), 2) AS avg_league_fg3a,
        SUM(is_back_to_back) AS total_back_to_backs
    FROM "nba_injuries"."main_silver"."stg_player_workload"
    GROUP BY season
),

season_injuries AS (
    SELECT
        season,
        COUNT(injury_id) AS total_injuries,
        COUNT(CASE WHEN injury_category = 'Overuse / Soft Tissue' THEN 1 END) AS overuse_injuries,
        COUNT(CASE WHEN injury_category = 'Trauma / Contact' THEN 1 END) AS trauma_injuries
    FROM "nba_injuries"."main_silver"."stg_injuries"
    GROUP BY season
)

SELECT
    w.season,
    w.avg_league_pace,
    w.avg_league_fg3a,
    w.total_back_to_backs,
    COALESCE(i.total_injuries, 0) AS total_injuries,
    COALESCE(i.overuse_injuries, 0) AS overuse_injuries,
    COALESCE(i.trauma_injuries, 0) AS trauma_injuries,
    
    -- Proporção de lesões por sobrecarga tecidual em relação ao total
    ROUND(
        COALESCE(i.overuse_injuries, 0)::DOUBLE / NULLIF(COALESCE(i.total_injuries, 0), 0) * 100, 
        2
    ) AS overuse_injury_pct
FROM season_workload w
LEFT JOIN season_injuries i ON w.season = i.season
ORDER BY w.season ASC
    );
    
  