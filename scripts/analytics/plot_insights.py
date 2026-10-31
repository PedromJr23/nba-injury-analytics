import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

DB_PATH = "warehouse/nba_injuries.duckdb"
OUTPUT_DIR = "reports/figures"

def generate_plots_and_tables():
    con = duckdb.connect(DB_PATH)
    sns.set_theme(style="whitegrid")
    
    print("📊 Gerando análises e comparações topográficas de lesões por Era...")
    
    # 1. Top 10 Tipos/Locais de Lesão por Era
    df_top_injuries = con.execute("""
        WITH era_injuries AS (
            SELECT 
                CASE 
                    WHEN season < 2000 THEN 'Era Tradicional (1980-1999)'
                    ELSE 'Era Modern Space (2010-2024)'
                END AS era_group,
                injury_category,
                COUNT(*) AS total_cases
            FROM main_silver.stg_injuries
            WHERE injury_category IS NOT NULL
            GROUP BY 1, 2
        )
        SELECT era_group, injury_category, total_cases
        FROM era_injuries
        ORDER BY era_group, total_cases DESC
    """).df()
    
    # 2. Dados Gerais da Gold
    df_eras = con.execute("SELECT * FROM main_gold.fct_league_era_workload_injuries ORDER BY season ASC").df()
    df_acwr = con.execute("SELECT * FROM main_gold.fct_acute_chronic_workload_ratio WHERE acwr_ratio IS NOT NULL").df()
    
    con.close()
    
    # --- GRÁFICO 1: Comparativo Top Locais/Tipos de Lesão (Tradicional vs Moderna) ---
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=df_top_injuries, 
        x='total_cases', 
        y='injury_category', 
        hue='era_group', 
        palette='magma'
    )
    plt.title('Mudança Biomecânica: Top Categoria de Lesões (1980-1999 vs 2010-2024)', fontsize=14, pad=15)
    plt.xlabel('Total de Ocorrências Registradas', fontsize=11)
    plt.ylabel('Categoria / Local da Lesão', fontsize=11)
    plt.legend(title='Era')
    plt.tight_layout()
    
    top10_path = os.path.join(OUTPUT_DIR, "top_injuries_by_era.png")
    plt.savefig(top10_path, dpi=300)
    plt.close()
    print(f"✅ Gráfico do Top Lesões salvo em: {top10_path}")

    # Print do Relatório no Terminal
    print("\n📌 COMPARATIVO: TOP LOCAIS/TIPOS DE LESÃO POR ERA")
    print("=" * 65)
    for era in df_top_injuries['era_group'].unique():
        print(f"\n🔹 {era.upper()}:")
        sub_df = df_top_injuries[df_top_injuries['era_group'] == era].head(10)
        print(sub_df[['injury_category', 'total_cases']].to_string(index=False))
    print("=" * 65)

if __name__ == "__main__":
    generate_plots_and_tables()
