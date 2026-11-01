import duckdb
import pandas as pd
import numpy as np

DB_PATH = "warehouse/nba_injuries.duckdb"

def calculate_joint_risk_score():
    print("=" * 70)
    print("🏀 MODELO PREDITIVO DE FATORES CONJUNTOS DE RISCO DE LESÃO (CALIBRADO)")
    print("=" * 70)
    
    con = duckdb.connect(DB_PATH)
    
    query = """
        SELECT 
            w.player_name,
            w.game_date,
            w.minutes_played,
            w.pace,
            w.fg3a,
            w.acute_load_minutes_7d,
            w.chronic_load_minutes_28d,
            ROUND(w.acute_load_minutes_7d / NULLIF(w.chronic_load_minutes_28d / 4.0, 0), 2) AS acwr_ratio,
            w.is_back_to_back
        FROM main_silver.stg_player_workload w
        ORDER BY w.player_name, w.game_date
    """
    df = con.execute(query).df()
    con.close()
    
    df['acwr_ratio'] = df['acwr_ratio'].fillna(1.0)
    
    # 1. Componente ACWR (Peso 40%): Trava em 1.0 quando ACWR >= 2.0
    df['score_acwr'] = np.clip(df['acwr_ratio'] / 2.0, 0, 1.0)
    
    # 2. Componente Espacial (Peso 30%): Pace > 99.0 e fg3a > 6.0
    df['score_spatial'] = np.where((df['pace'] > 99.0) & (df['fg3a'] > 6.0), 1.0, 0.3)
    
    # 3. Componente de Calendario (Peso 20%): Back-to-Back
    df['score_calendar'] = np.where(df['is_back_to_back'] == 1, 1.0, 0.1)
    
    # 4. Componente de Minutagem (Peso 10%): Minutos > 34
    df['score_exposure'] = np.clip(df['minutes_played'] / 36.0, 0, 1.0)
    
    # Calculation do Score Ponderado (0 a 100)
    df['joint_risk_score_pct'] = (
        (df['score_acwr'] * 0.40) +
        (df['score_spatial'] * 0.30) +
        (df['score_calendar'] * 0.20) +
        (df['score_exposure'] * 0.10)
    ) * 100
    
    # Faixas de Corte Calibradas para Uso Prático
    conditions = [
        (df['joint_risk_score_pct'] >= 85),
        (df['joint_risk_score_pct'] >= 60) & (df['joint_risk_score_pct'] < 85),
        (df['joint_risk_score_pct'] < 60)
    ]
    choices = ['🔴 Risco Critico (Acao: Poupar / Reduzir Minutos)', '🟡 Risco Moderado (Acao: Monitorar)', '🟢 Risco Baixo (Liberado)']
    df['nivel_risco'] = np.select(conditions, choices, default='🟢 Risco Baixo (Liberado)')
    
    print("\n📊 DISTRIBUIÇÃO DO RISCO CONJUNTO PREVISTO NA BASE:")
    print(df['nivel_risco'].value_counts())
    
    print("\n⚠️ TOP 10 CASOS COM MAIOR RISCO MULTIVARIADO ACUMULADO:")
    top_risks = df[['player_name', 'game_date', 'acwr_ratio', 'pace', 'is_back_to_back', 'joint_risk_score_pct', 'nivel_risco']]\
        .sort_values(by='joint_risk_score_pct', ascending=False).head(10)
    print(top_risks.to_string(index=False))

if __name__ == "__main__":
    calculate_joint_risk_score()
