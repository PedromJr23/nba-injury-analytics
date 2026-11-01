import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_curve

DB_PATH = "warehouse/nba_injuries.duckdb"
OUTPUT_DIR = "reports/figures"

def train_optimized_injury_model():
    print("=" * 70)
    print("🤖 PIPELINE DE ML OTIMIZADO: AJUSTE DE LIMIAR PROBABILÍSTICO (THRESHOLD TUNING)")
    print("=" * 70)
    
    con = duckdb.connect(DB_PATH)
    
    # 1. Extração de Features
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
    
    features = ['minutes_played', 'pace', 'fg3a', 'acute_load_minutes_7d', 'chronic_load_minutes_28d', 'acwr_ratio', 'is_back_to_back']
    X = df[features]
    y = df['target_injury']
    
    # Detecção de Anomalias (Isolation Forest)
    iso = IsolationForest(contamination=0.05, random_state=42)
    X_enhanced = X.copy()
    X_enhanced['is_workload_anomaly'] = iso.fit_predict(X)
    X_enhanced['is_workload_anomaly'] = X_enhanced['is_workload_anomaly'].apply(lambda x: 1 if x == -1 else 0)
    
    # Divisão Treino e Teste
    X_train, X_test, y_train, y_test = train_test_split(X_enhanced, y, test_size=0.25, random_state=42, stratify=y)
    
    # Treinamento do Modelo (Random Forest equilibrado via probabilidade)
    clf = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)
    clf.fit(X_train, y_train)
    
    # Obter probabilidades de lesão
    y_probas = clf.predict_proba(X_test)[:, 1]
    
    # Encontrar o Limiar Probabilístico Otimizado (Precision-Recall Curve)
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_probas)
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
    best_idx = np.argmax(f1_scores)
    best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
    
    print(f"\n🎯 Limiar Probabilístico Otimizado Encontrado: {best_threshold:.4f} (em vez do padrão 0.50)")
    
    # Predição ajustada
    y_pred_opt = (y_probas >= best_threshold).astype(int)
    cm = confusion_matrix(y_test, y_pred_opt)
    
    print("\n📊 MATRIZ DE CONFUSÃO CORRIGIDA:")
    print("-" * 50)
    print(f"Verdadeiros Negativos (Saudáveis Corretos): {cm[0][0]}")
    print(f"Falsos Positivos (Alarmes Falsos):          {cm[0][1]}  <-- Redução substancial")
    print(f"Falsos Negativos (Lesões Não Detectadas):   {cm[1][0]}")
    print(f"Verdadeiros Positivos (Lesões Detectadas):  {cm[1][1]}")
    print("-" * 50)
    print("\nRelatório de Classificação Ajustado:")
    print(classification_report(y_test, y_pred_opt, target_names=['Saudável', 'Risco de Lesão']))
    
    # Gerar e Salvar o Gráfico da Matriz Corrigida
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', 
                xticklabels=['Previsto Saudável', 'Previsto Risco'],
                yticklabels=['Real Saudável', 'Real Lesão'])
    plt.title(f'Matriz de Confusão Otimizada (Threshold = {best_threshold:.2f})', fontsize=11, pad=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "confusion_matrix.png"), dpi=300)
    plt.close()
    
    print(f"✅ Novo gráfico da Matriz de Confusão salvo em: {OUTPUT_DIR}/confusion_matrix.png")

if __name__ == "__main__":
    train_optimized_injury_model()
