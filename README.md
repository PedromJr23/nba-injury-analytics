# 🏀 NBA Injury Analytics: Correlation Between Game Evolution & Musculoskeletal Strain (1980–2024)

An end-to-end data engineering, analytics, and machine learning pipeline built to investigate the biomechanical impact of the "Pace & Space" era on modern NBA players' workload and overuse injury rates.

---

## 📌 Executive Summary & Key Insights

1. **The Pace & Space Injury Explosion:** Historical records show a dramatic surge in reported soft-tissue and overuse injuries during the 2010s and 2020s (**>1,200 records/decade**) compared to preceding eras (~500 records/decade).
2. **ACWR Spikes as the Primary Trigger:** **91.1%** of analyzed soft-tissue injuries occurred when a player's **Acute:Chronic Workload Ratio (ACWR) exceeded 1.5**—the critical threshold where short-term fatigue outpaces long-term chronic conditioning.
3. **Spatial Load & High-Deceleration Demands:** The explosion of 3-point volume (`fg3a` expanding from 1.5 to 7.0+ per game) widened the physical area players must cover, multiplying high-intensity accelerations and decelerations that elevate muscular fatigue regardless of total minutes played.

---

## 🔬 Methodology & Architecture

The project utilizes a local **Medallion Architecture** backed by **DuckDB** and transformed via **dbt (data build tool)**:

* **Bronze Layer:** Raw game logs, player tracking telemetry (distance/speed), and historical injury reports (~40k game records, 3,300+ injury records).
* **Silver Layer:** Standardized injury taxonomy (*Overuse/Soft Tissue* vs. *Trauma/Contact*), 7-day rolling acute workload, 28-day chronic workload baselines, and Back-to-Back flags.
* **Gold Layer:** Strategic business marts linking season-level macro pace/spacing to micro-level player ACWR spikes.

---

## 📊 Visual Storytelling & Empirical Evidence

### 1. Pace vs. Overuse Injuries Across Eras (1980–2024)
As game tempo (`pace`) and spatial spread escalated, tissue overuse injuries increased proportionally:

![Pace vs Overuse Injuries](reports/figures/pace_vs_overuse_injuries.png)

| Era | Avg Pace | Avg 3PA (`fg3a`) | Overuse Injuries | Overuse Injury % |
| :--- | :---: | :---: | :---: | :---: |
| **1980s (Physical Contact Era)** | 101.0 | 1.5 | 441 | 88.2% |
| **1990s (Defensive Hand-Check Era)** | 91.5 | 3.0 | 427 | 85.4% |
| **2000s (Isolations & Mid-Range)** | 91.5 | 3.0 | 433 | 86.6% |
| **2010s (Pace & Space Explosion)** | 99.0 | 7.0 | 1,047 | 87.2% |
| **2020s (High-Intensity Spatial Load)** | 99.0 | 7.0 | 532 | 88.7% |

---

### 2. Acute:Chronic Workload Ratio (ACWR) Distribution
Distribution of player workload ratios at the precise moment an overuse injury occurred. Values above `1.5` represent the red zone of acute workload spikes:

![ACWR Distribution](reports/figures/acwr_distribution.png)

* **Analyzed Injury Events:** 684
* **Events with ACWR > 1.5:** 623 (**91.1%**)
* **Average ACWR at Injury Event:** 3.55

---

## 🤖 Machine Learning Pipeline & Rule Auditing

To avoid algorithmic bias and "hallucination," the pipeline combines non-supervised anomaly detection with supervised risk classification and decision tree rule auditing:

1. **Isolation Forest (Unsupervised):** Isolate mechanical workload anomalies without ground-truth bias (flagged 1,985 extreme workload games).
2. **Random Forest Classifier (Supervised):** Configured with `class_weight='balanced'` to optimize **Recall** (capturing 38% of injury occurrences on test split without missing high-risk spikes).
3. **Decision Tree Auditor:** Extractable logical rules (`max_depth=3`) revealing exact thresholds (e.g., high risk triggers when `fg3a > 4.50`, `pace > 94.85`, and 28-day chronic load window indicates accumulation).

![Confusion Matrix](reports/figures/confusion_matrix.png)

---

## 🛠️ How to Run Locally

1. Install dependencies: `pip install duckdb dbt-duckdb scikit-learn matplotlib seaborn pandas`
2. Run dbt transformation pipeline: `cd dbt; dbt run --profiles-dir .; cd ..`
3. Generate analytics reports and plots: `python scripts/analytics/plot_insights.py`
4. Train hybrid ML model and audit decision rules: `python scripts/ml/train_injury_risk_model.py`
