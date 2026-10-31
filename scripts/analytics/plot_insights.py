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
    
    print("📊 Gerando tabelas e gráficos estatísticos a partir da camada Gold...")
    
    # 1. Dados de Era
    df_eras = con.execute("""
        SELECT 
            season,
            avg_league_pace,
            avg_league_fg3a,
            total_injuries,
            overuse_injuries,
            overuse_injury_pct
        FROM main_gold.fct_league_era_workload_injuries
        ORDER BY season ASC
    """).df()
    
    # 2. Dados de ACWR
    df_acwr = con.execute("""
        SELECT 
            acwr_ratio,
            injury_category,
            is_back_to_back
        FROM main_gold.fct_acute_chronic_workload_ratio
        WHERE acwr_ratio IS NOT NULL
    """).df()
    
    con.close()
    
    # --- GRÁFICO 1: Evolução Longitudinal do Pace & Espaçamento vs. Volume de Lesões ---
    fig, ax1 = plt.subplots(figsize=(12, 6))

    color = 'tab:blue'
    ax1.set_xlabel('Temporada (Season)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total de Lesões por Sobrecarga (Overuse)', color=color, fontsize=12, fontweight='bold')
    ax1.plot(df_eras['season'], df_eras['overuse_injuries'], color=color, linewidth=2.5, label='Lesões por Sobrecarga')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  
    color = 'tab:red'
    ax2.set_ylabel('Ritmo Médio de Jogo (Pace)', color=color, fontsize=12, fontweight='bold')
    ax2.plot(df_eras['season'], df_eras['avg_league_pace'], color=color, linewidth=2, linestyle='--', label='Pace Médio')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('NBA (1980–2024): Evolução do Ritmo de Jogo (Pace) vs. Incidência de Lesões Musculares', fontsize=14, pad=15)
    fig.tight_layout()
    plot1_path = os.path.join(OUTPUT_DIR, "pace_vs_overuse_injuries.png")
    plt.savefig(plot1_path, dpi=300)
    plt.close()
    print(f"✅ Gráfico 1 salvo em: {plot1_path}")

    # --- GRÁFICO 2: Distribuição do ACWR no momento da lesão ---
    plt.figure(figsize=(10, 5))
    sns.histplot(df_acwr['acwr_ratio'], bins=25, kde=True, color='purple')
    plt.axvline(1.5, color='red', linestyle='--', linewidth=2, label='Limiar de Risco (ACWR = 1.5)')
    plt.title('Distribuição da Razão Aguda:Crônica (ACWR) no Momento da Lesão', fontsize=13, pad=12)
    plt.xlabel('ACWR (Acute:Chronic Workload Ratio)', fontsize=11)
    plt.ylabel('Frequência de Ocorrências', fontsize=11)
    plt.legend()
    plt.tight_layout()
    plot2_path = os.path.join(OUTPUT_DIR, "acwr_distribution.png")
    plt.savefig(plot2_path, dpi=300)
    plt.close()
    print(f"✅ Gráfico 2 salvo em: {plot2_path}")

    print("\n📌 TABELA ANALÍTICA RESUMIDA POR DECADA:")
    print("-" * 60)
    summary_table = df_eras.groupby((df_eras['season'] // 10) * 10).agg({
        'avg_league_pace': 'mean',
        'avg_league_fg3a': 'mean',
        'total_injuries': 'sum',
        'overuse_injuries': 'sum',
        'overuse_injury_pct': 'mean'
    }).round(1)
    print(summary_table.to_string())
    print("-" * 60)

if __name__ == "__main__":
    generate_plots_and_tables()
