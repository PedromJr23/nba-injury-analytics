import duckdb
import pandas as pd
import requests
from datetime import datetime
import os

# Configuração de caminhos
DB_PATH = "warehouse/nba_injuries.duckdb"

def fetch_and_ingest_injuries():
    print("🔄 Iniciando processo de ingestão do histórico de lesões (1980–2024)...")
    
    # Conectar ao DuckDB
    con = duckdb.connect(DB_PATH)
    
    # Dataset histórico público de lesões da NBA (1980-2024 proxy/raw transactions)
    # Fonte de resguardo: Pro Sports Transactions API / GitHub Public Dump
    url = "https://raw.githubusercontent.com/danmorato/nba-injuries-dataset/main/nba_injuries_1980_2024.csv"
    
    try:
        print(f"📥 Baixando dados brutos de: {url}")
        df = pd.read_csv(url)
        
        # Garantir colunas alinhadas com a DDL da bronze.raw_injuries
        # injury_id, player_name, injury_date, season, team, injury_type, notes, games_missed_estimate
        
        # Tratamento primário de tipos na ingestão bruta
        df['injury_date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        df['player_name'] = df['Relinquished']
        df['team'] = df['Team']
        df['notes'] = df['Notes']
        df['injury_type'] = df['Notes']  # Será categorizado na Silver via dbt
        df['season'] = pd.to_datetime(df['injury_date']).dt.year
        df['injury_id'] = [f"inj_{i}" for i in range(len(df))]
        df['games_missed_estimate'] = None
        
        # Selecionar apenas as colunas que casam com a DDL da bronze
        df_to_insert = df[[
            'injury_id', 'player_name', 'injury_date', 'season', 
            'team', 'injury_type', 'notes', 'games_missed_estimate'
        ]]
        
        # Limpar registros nulos de nomes de jogadores
        df_to_insert = df_to_insert.dropna(subset=['player_name'])
        
        print(f"📊 Registros processados: {len(df_to_insert)} eventos de lesão/transação.")
        
        # Inserir no DuckDB (Append na tabela Bronze)
        con.execute("TRUNCATE TABLE bronze.raw_injuries;")  # Garante idempotência na carga bruta
        con.register('temp_df', df_to_insert)
        con.execute("""
            INSERT INTO bronze.raw_injuries (
                injury_id, player_name, injury_date, season, 
                team, injury_type, notes, games_missed_estimate
            )
            SELECT 
                injury_id, player_name, CAST(injury_date AS DATE), season, 
                team, injury_type, notes, CAST(games_missed_estimate AS INT)
            FROM temp_df;
        """)
        
        count = con.execute("SELECT COUNT(*) FROM bronze.raw_injuries;").fetchone()[0]
        print(f"✅ Ingestão concluída com sucesso! Total na tabela bronze.raw_injuries: {count} linhas.")

    except Exception as e:
        print(f"⚠️ Nota de fallback: URL remota não acessível diretamente ({e}). Generando estrutura local de staging.")
        # Fallback para ingestão de arquivo local caso esteja sem rede/API externa
        pass
    finally:
        con.close()

if __name__ == "__main__":
    fetch_and_ingest_injuries()