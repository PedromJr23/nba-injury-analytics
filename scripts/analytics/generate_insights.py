import duckdb
import pandas as pd

DB_PATH = "warehouse/nba_injuries.duckdb"

def analyze_gold_metrics():
    con = duckdb.connect(DB_PATH)
    
    print("=" * 65)
    print("🏀 NBA INJURY & LOAD ANALYTICS — RELATÓRIO DE INSIGHTS (GOLD LAYER)")
    print("=" * 65)
    
    # 1. Correlação Longitudinal por Era (1980–2024)
    print("\n📈 1. EVOLUÇÃO POR ERA: PACE, FG3A E FAIXA DE LESÕES POR SOBRECARGA")
    print("-" * 65)
    
    df_eras = con.execute("""
        SELECT 
            CASE 
                WHEN season < 1990 THEN '1980s (Physical Contact Era)'
                WHEN season < 2000 THEN '1990s (Defensive Hand-Check Era)'
                WHEN season < 2010 THEN '2000s (Isolations & Mid-Range)'
                WHEN season < 2020 THEN '2010s (Pace & Space Explosion)'
                ELSE '2020s (High-Intensity & Spatial Load)'
            END AS era,
            COUNT(season) AS seasons_count,
            ROUND(AVG(avg_league_pace), 1) AS avg_pace,
            ROUND(AVG(avg_league_fg3a), 1) AS avg_3pa,
            SUM(total_injuries) AS total_injuries,
            SUM(overuse_injuries) AS total_overuse_injuries,
            ROUND(AVG(overuse_injury_pct), 1) AS avg_overuse_pct
        FROM main_gold.fct_league_era_workload_injuries
        GROUP BY 1
        ORDER BY MIN(season) ASC
    """).df()
    
    print(df_eras.to_string(index=False))
    
    # 2. Análise da Razão ACWR (Acute:Chronic Workload Ratio)
    print("\n\n⚠️ 2. ANÁLISE DE PICO DE SOBRECARGA (ACWR > 1.5 NO MOMENTO DA LESÃO)")
    print("-" * 65)
    
    df_acwr = con.execute("""
        SELECT 
            COUNT(*) AS total_injuries_analyzed,
            COUNT(CASE WHEN acwr_ratio > 1.5 THEN 1 END) AS high_risk_acwr_count,
            ROUND(COUNT(CASE WHEN acwr_ratio > 1.5 THEN 1 END)::DOUBLE / COUNT(*) * 100, 1) AS high_risk_pct,
            ROUND(AVG(acwr_ratio), 2) AS avg_acwr_ratio
        FROM main_gold.fct_acute_chronic_workload_ratio
        WHERE acwr_ratio IS NOT NULL
    """).df()
    
    print(df_acwr.to_string(index=False))
    print("=" * 65)
    
    con.close()

if __name__ == "__main__":
    analyze_gold_metrics()
