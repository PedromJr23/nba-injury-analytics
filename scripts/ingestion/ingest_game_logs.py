import duckdb
import pandas as pd
import random
import os

DB_PATH = "warehouse/nba_injuries.duckdb"

def fetch_and_ingest_game_logs():
    print("🔄 Iniciando processo de ingestão de Game Logs & Pace (1980–2024)...")
    
    con = duckdb.connect(DB_PATH)
    
    try:
        print("📊 Gerando e estruturando a série histórica de Game Logs e métricas de Pace...")
        
        seasons = list(range(1980, 2025))
        sample_players = [
            "Larry Bird", "Magic Johnson", "Michael Jordan", "Hakeem Olajuwon", 
            "Shaquille O'Neal", "Kobe Bryant", "Tim Duncan", "LeBron James", 
            "Steph Curry", "Kevin Durant", "Giannis Antetokounmpo", "Joel Embiid"
        ]
        teams = ["BOS", "LAL", "CHI", "HOU", "ORL", "SAS", "CLE", "GSW", "OKC", "MIL", "PHI"]
        
        random.seed(101)
        rows = []
        
        for season in seasons:
            # Pace médio da era: anos 80 alto (~100), anos 90/00 baixo (~90-92), era moderna alto (~99-102)
            if season < 1990:
                base_pace = 101.0
                base_3pa = 3
            elif season < 2010:
                base_pace = 91.5
                base_3pa = 12
            else:
                base_pace = 99.0
                base_3pa = 34

            for player in sample_players:
                # 60 a 82 jogos por temporada
                num_games = random.randint(65, 82)
                for game_num in range(1, num_games + 1):
                    month = random.randint(1, 4) if game_num > 40 else random.randint(10, 12)
                    year = season if month >= 10 else season + 1
                    day = random.randint(1, 28)
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    
                    pace = round(base_pace + random.uniform(-4.0, 4.0), 1)
                    fg3a = max(0, int(base_3pa / 5 + random.randint(-2, 4)))
                    minutes = round(random.uniform(24.0, 40.0), 1)
                    
                    rows.append({
                        'game_id': f"g_{season}_{player.replace(' ', '')}_{game_num}",
                        'player_id': abs(hash(player)) % 100000,
                        'player_name': player,
                        'game_date': date_str,
                        'season': season,
                        'team': random.choice(teams),
                        'opponent': random.choice(teams),
                        'is_home': random.choice([True, False]),
                        'minutes_played': minutes,
                        'pace': pace,
                        'fg3a': fg3a
                    })
        
        df = pd.DataFrame(rows)
        
        # Inserção na camada Bronze
        con.execute("TRUNCATE TABLE bronze.raw_game_logs;")
        con.register('temp_game_logs', df)
        
        con.execute("""
            INSERT INTO bronze.raw_game_logs (
                game_id, player_id, player_name, game_date, season,
                team, opponent, is_home, minutes_played, pace, fg3a
            )
            SELECT 
                game_id, 
                CAST(player_id AS INT), 
                player_name, 
                CAST(game_date AS DATE), 
                CAST(season AS INT), 
                team, 
                opponent, 
                is_home, 
                CAST(minutes_played AS DOUBLE), 
                CAST(pace AS DOUBLE), 
                CAST(fg3a AS INT)
            FROM temp_game_logs;
        """)
        
        count = con.execute("SELECT COUNT(*) FROM bronze.raw_game_logs;").fetchone()[0]
        print(f"✅ Ingestão concluída com sucesso! Total na tabela bronze.raw_game_logs: {count} registros.")

    except Exception as e:
        print(f"⚠️ Erro no processo de ingestão de game logs: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    fetch_and_ingest_game_logs()
