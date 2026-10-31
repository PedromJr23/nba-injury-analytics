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
    
    print("📊 Gerando análises financeiras, de jogos perdidos e locais do corpo por Era...")
    
    # 1. Análise Financeira e de Gravidade por Categoria de Lesão e Era (Agrupado via era_group)
    df_injury_impact = con.execute("""
        SELECT 
            CASE 
                WHEN season < 2000 THEN 'Era Tradicional (1980-1999)'
                ELSE 'Era Modern Space (2010-2024)'
            END AS era_group,
            injury_category,
            COUNT(*) AS total_cases,
            ROUND(AVG(COALESCE(games_missed, 5)), 1) AS avg_games_missed,
            -- Custo estimado por jogo perdido ($75k/jogo era moderna vs $20k/jogo tradicional)
            ROUND(COUNT(*) * AVG(COALESCE(games_missed, 5)) * 
                CASE 
                    WHEN (CASE WHEN season < 2000 THEN 'Era Tradicional (1980-1999)' ELSE 'Era Modern Space (2010-2024)' END) = 'Era Tradicional (1980-1999)' 
                    THEN 20000 
                    ELSE 75000 
                END / 1000000.0, 2) AS estimated_cost_millions
        FROM main_silver.stg_injuries
        WHERE injury_category IS NOT NULL
        GROUP BY 1, 2
        ORDER BY era_group, total_cases DESC
    """).df()
    
    con.close()
    
    # --- GRÁFICO 1: Comparativo de Ocorrências por Local do Corpo ---
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=df_injury_impact, 
        x='total_cases', 
        y='injury_category', 
        hue='era_group', 
        palette='magma'
    )
    plt.title('Mudança Biomecânica: Ocorrências por Local do Corpo (1980-1999 vs 2010-2024)', fontsize=14, pad=15)
    plt.xlabel('Total de Ocorrências Registradas', fontsize=11)
    plt.ylabel('Local / Categoria da Lesão', fontsize=11)
    plt.legend(title='Era')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top_injuries_by_era.png"), dpi=300)
    plt.close()

    # --- GRÁFICO 2: Custo Financeiro Estimado por Categoria na Era Moderna ($ Milhões) ---
    plt.figure(figsize=(10, 5))
    modern_df = df_injury_impact[df_injury_impact['era_group'] == 'Era Modern Space (2010-2024)'].sort_values('estimated_cost_millions', ascending=False).head(8)
    sns.barplot(
        data=modern_df,
        x='estimated_cost_millions',
        y='injury_category',
        palette='Reds_r'
    )
    plt.title('Impacto Financeiro Estimado por Tipo de Lesão na Era Moderna (em $ Milhões)', fontsize=13, pad=12)
    plt.xlabel('Custo Estimado em Salários de Jogadores Afastados ($ Milhões)', fontsize=11)
    plt.ylabel('Local da Lesão', fontsize=11)
    plt.tight_layout()
    cost_plot_path = os.path.join(OUTPUT_DIR, "injury_financial_cost.png")
    plt.savefig(cost_plot_path, dpi=300)
    plt.close()
    
    print(f"✅ Gráficos gerados com sucesso em: {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_plots_and_tables()
