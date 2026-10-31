import duckdb
import os

# 1. Garantir que a pasta do Data Warehouse existe
os.makedirs("warehouse", exist_ok=True)

# 2. Conectar ao DuckDB (cria o arquivo se não existir)
db_path = "warehouse/nba_injuries.duckdb"
con = duckdb.connect(db_path)

# 3. Criar os Schemas da Arquitetura Medallion
con.execute("CREATE SCHEMA IF NOT EXISTS bronze;")
con.execute("CREATE SCHEMA IF NOT EXISTS silver;")
con.execute("CREATE SCHEMA IF NOT EXISTS gold;")

print("✅ Schemas Bronze, Silver e Gold criados com sucesso.")

# --- 4. DDL: CAMADA BRONZE (RAW TABLES) ---

# A) Histórico Bruto de Lesões (1980–2024)
con.execute("""
CREATE TABLE IF NOT EXISTS bronze.raw_injuries (
    injury_id VARCHAR,
    player_name VARCHAR,
    injury_date DATE,
    season INT,
    team VARCHAR,
    injury_type VARCHAR,          -- Ex: Calf Strain, Knee Surgery, Rest
    notes VARCHAR,                -- Descrição médica/noticiário
    games_missed_estimate INT,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# B) Game Logs, Minutagem e Pace Brutos (1980–2024)
con.execute("""
CREATE TABLE IF NOT EXISTS bronze.raw_game_logs (
    game_id VARCHAR,
    player_id INT,
    player_name VARCHAR,
    game_date DATE,
    season INT,
    team VARCHAR,
    opponent VARCHAR,
    is_home BOOLEAN,
    minutes_played DOUBLE,
    pace DOUBLE,                  -- Ritmo de jogo (possessões/48m)
    fg3a INT,                     -- Tentativas de 3 pontos (Espaçamento)
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# C) Player Tracking Óptico Bruto (2013–2024)
con.execute("""
CREATE TABLE IF NOT EXISTS bronze.raw_player_tracking (
    game_id VARCHAR,
    player_id INT,
    player_name VARCHAR,
    game_date DATE,
    season INT,
    distance_miles DOUBLE,        -- Distância percorrida em quadra
    avg_speed_mph DOUBLE,         -- Velocidade média
    fast_break_points INT,
    touches INT,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# D) Calendário e Viagens Brutos (1980–2024)
con.execute("""
CREATE TABLE IF NOT EXISTS bronze.raw_schedule (
    game_id VARCHAR,
    game_date DATE,
    season INT,
    home_team VARCHAR,
    away_team VARCHAR,
    rest_days_home INT,           -- Dias de descanso pré-jogo
    rest_days_away INT,
    is_back_to_back BOOLEAN,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

print("✅ Estrutura DDL das tabelas Bronze criada com sucesso no DuckDB!")
con.close()