WITH raw_data AS (
    SELECT 
        injury_id,
        player_name,
        injury_date,
        season,
        team,
        notes,
        games_missed_estimate
    FROM {{ source('bronze', 'raw_injuries') }}
)

SELECT
    injury_id,
    player_name,
    injury_date,
    season,
    team,
    notes,
    
    -- Categorização da Lesão (Sobrecarga Tecidual vs. Trauma de Contato)
    CASE 
        WHEN LOWER(notes) LIKE '%strain%' 
          OR LOWER(notes) LIKE '%sore%' 
          OR LOWER(notes) LIKE '%tendinitis%' 
          OR LOWER(notes) LIKE '%calf%' 
          OR LOWER(notes) LIKE '%hamstring%' 
          OR LOWER(notes) LIKE '%groin%' 
          OR LOWER(notes) LIKE '%rest%' 
          OR LOWER(notes) LIKE '%load management%'
        THEN 'Overuse / Soft Tissue'
        
        WHEN LOWER(notes) LIKE '%fracture%' 
          OR LOWER(notes) LIKE '%surgery%' 
          OR LOWER(notes) LIKE '%sprain%' 
          OR LOWER(notes) LIKE '%concussion%' 
          OR LOWER(notes) LIKE '%torn%'
        THEN 'Trauma / Contact'
        
        ELSE 'Uncategorized / Other'
    END AS injury_category,
    
    COALESCE(games_missed_estimate, 1) AS games_missed
FROM raw_data
