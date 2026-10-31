import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

DB_PATH = "warehouse/nba_injuries.duckdb"
OUTPUT_DIR = "reports/figures"

def train_advanced_hybrid_ml():
    print("=" * 70)
    print("🤖 PIPELINE AVANÇADO DE MACHINE LEARNING (HÍBRIDO + AUDITORIA DE ÁRVORES)")
    print("=" * 70)
    
    con = duckdb.connect(DB_PATH)
    
    # 1. Extração da base Bronze/Silver/Gold
    df = con.execute("""
        SELECT 
            w.minutes_played,
            w.pace,
            w.fg3a,
            w.acute_load_minutes_7d,
            w.chronic_load_minutes_28d,
            ROUND(w.acute_load_minutes_7d / NULLIF(w.chronic_load_minutes_28d / 4.0, 0), 2) AS acwr_ratio,
            w.is_back_to_back,
            CASE WHEN i.injury_id IS NOT NULL THEN 1 ELSE 0 END AS target_injury
        FROM main_silver.stg_player_workload w
        LEFT JOIN main_silver.stg_injuries i
            ON w.player_name = i.player_name 
           AND w.game_date = i.injury_date
    """).df()
    
    con.close()
    
    df['acwr_ratio'] = df['acwr_ratio'].fillna(1.0)
    
    features = [
        'minutes_played', 'pace', 'fg3a', 
        'acute_load_minutes_7d', 'chronic_load_minutes_28d', 
        'acwr_ratio', 'is_back_to_back'
    ]
    
    X = df[features]
    y = df['target_injury']
    
    # -------------------------------------------------------------------------
    # ETAPA 1: ETAPA NÃO SUPERVISIONADA (Detection of Workload Anomalies)
    # -------------------------------------------------------------------------
    print("\n🔍 1. APRENDIZADO NÃO SUPERVISIONADO: Isolation Forest para Anomalias de Carga")
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    # -1 representa outlier/anomalia de carga, 1 representa carga dentro do padrão
    df['anomaly_score'] = iso_forest.fit_predict(X)
    df['is_workload_anomaly'] = df['anomaly_score'].apply(lambda x: 1 if x == -1 else 0)
    
    print(f"✅ Anomalias de carga identificadas (não supervisionado): {df['is_workload_anomaly'].sum()} partidas.")
    
    # Adiciona a flag de anomalia como feature explicativa
    X_enhanced = X.copy()
    X_enhanced['is_workload_anomaly'] = df['is_workload_anomaly']
    
    # -------------------------------------------------------------------------
    # ETAPA 2: TREINO SUPERVISIONADO COM CONTROLE DE DESBALANÇO
    # -------------------------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X_enhanced, y, test_size=0.25, random_state=42, stratify=y
    )
    
    clf = RandomForestClassifier(
        n_estimators=100, 
        max_depth=6,             # Evita alucinação / overfitting
        class_weight='balanced', # Previne viés de classe majoritária
        random_state=42
    )
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]
    
    # -------------------------------------------------------------------------
    # ETAPA 3: MATRIZ DE CONFUSÃO & MÉTRICAS DE AVALIAÇÃO
    # -------------------------------------------------------------------------
    cm = confusion_matrix(y_test, y_pred)
    
    print("\n📊 2. MATRIZ DE CONFUSÃO E AVALIAÇÃO DE DESEMPENHO (SEM VIÉS):")
    print("-" * 70)
    print(f"Verdadeiros Negativos (Sem Lesão Corretos): {cm[0][0]}")
    print(f"Falsos Positivos (Alarme Falso):            {cm[0][1]}")
    print(f"Falsos Negativos (Lesão Não Detectada):     {cm[1][0]}  <-- Minimizado")
    print(f"Verdadeiros Positivos (Lesão Detectada):    {cm[1][1]}")
    print("-" * 70)
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")
    print("\nRelatório Detalhado de Métricas:")
    print(classification_report(y_test, y_pred, target_names=['Saudável', 'Risco de Lesão']))
    
    # Plota e Salva a Matriz de Confusão
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Previsto Saudável', 'Previsto Risco'],
                yticklabels=['Real Saudável', 'Real Lesão'])
    plt.title('Matriz de Confusão — Modelo Híbrido de Risco', fontsize=12, pad=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "confusion_matrix.png"), dpi=300)
    plt.close()
    
    # -------------------------------------------------------------------------
    # ETAPA 4: ÁRVORE DE DECISÃO AUDITÁVEL (EXPLICABILIDADE DAS REGRAS)
    # -------------------------------------------------------------------------
    print("\n🌳 3. AUDITORIA DE REGRAS DE DECISÃO (SINGLE DECISION TREE):")
    print("-" * 70)
    explainer_tree = DecisionTreeClassifier(max_depth=3, class_weight='balanced', random_state=42)
    explainer_tree.fit(X_train, y_train)
    
    tree_rules = export_text(explainer_tree, feature_names=list(X_enhanced.columns))
    print("Regras Lógicas Extraídas da Árvore de Decisão:")
    print(tree_rules)
    print("=" * 70)

if __name__ == "__main__":
    train_advanced_hybrid_ml()
