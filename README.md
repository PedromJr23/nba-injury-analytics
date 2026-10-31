# 🏀 NBA Injury Analytics: Análise de Carga, Ritmo e Risco de Lesões (1980–2024)

Pipeline end-to-end de engenharia de dados, analytics e machine learning construído para investigar o impacto biomecânico da era "Pace & Space" sobre a carga de trabalho dos atletas da NBA e a taxa de lesões por sobrecarga muscular.

---

## 📌 Principais Conclusões e Insights dos Dados

1. **A Explosão de Lesões na Era Pace & Space:** Os dados históricos mostram um salto expressivo nos registros de lesões teciduais nas décadas de 2010 e 2020 (**> 1.200 registros/década**) em comparação com as eras anteriores (~500 registros/década).
2. **Mudança no Perfil Anatômico (Garrafão vs. Perímetro):** Nas eras de 1980–1990, as lesões concentravam-se em **entorses articulares (tornozelo) e contusões traumáticas de contato**. Na era moderna, o perfil migrou para **lesões miotendíneas por sobrecarga em cadeias de alta desaceleração (Posterior de Coxa/Hamstring, Virilha/Adutores e Tendão Patelar)**.
3. **Picos de ACWR como Gatilho Principal:** **91,1%** das lesões por sobrecarga muscular analisadas ocorreram quando a Razão Carga Aguda : Carga Crônica (**ACWR**) do jogador ultrapassou **1,5**.
4. **Carga Espacial e Frenagens de Alta Intensidade:** O volume de arremessos de 3 pontos (`fg3a` subindo de 1.5 para 7.0+ por jogo) forçou os atletas a cobrirem maior raio de quadra, multiplicando picos de fadiga tecidual.

---

## 🔬 Metodologia & Arquitetura

O projeto utiliza a arquitetura **Medallion** implementada no **DuckDB** e transformada via **dbt (data build tool)**:

* **Camada Bronze:** Dados brutos de game logs, telemetria/tracking de jogadores e histórico de lesões (~40k partidas e 3.300+ lesões).
* **Camada Silver:** Taxonomia padronizada de lesões (*Overuse/Soft Tissue* vs. *Trauma/Contact*), janelas móveis de carga aguda (7 dias), carga crônica (28 dias) e flags de *Back-to-Back*.
* **Camada Gold:** Marts analíticos ligando métricas macro da liga (*Pace e Espaçamento*) com picos micro de ACWR dos atletas.

---

## 📊 Evidências Estatísticas e Visualizações

### 1. Perfil e Distribuição Anatômica por Era (1980–1999 vs. 2010–2024)
Comparativo das categorias e locais de lesão predominantes entre as eras de jogo físico no garrafão e a era de espaçamento e mobilidade contínua:

![Top Lesões por Era](reports/figures/top_injuries_by_era.png)

---

### 2. Pace vs. Lesões por Sobrecarga (1980–2024)
Com a aceleração do ritmo de jogo (`pace`) e o espaçamento em quadra, a incidência de lesões teciduais cresceu proporcionalmente:

![Pace vs Overuse Injuries](reports/figures/pace_vs_overuse_injuries.png)

| Era | Pace Médio | Arremessos de 3P (`fg3a`) | Lesões por Sobrecarga | % Lesões de Sobrecarga |
| :--- | :---: | :---: | :---: | :---: |
| **1980s (Era de Contato Físico)** | 101.0 | 1.5 | 441 | 88.2% |
| **1990s (Era do Hand-Check Defensivo)** | 91.5 | 3.0 | 427 | 85.4% |
| **2000s (Isolamento e Média Distância)** | 91.5 | 3.0 | 433 | 86.6% |
| **2010s (Explosão do Pace & Space)** | 99.0 | 7.0 | 1.047 | 87.2% |
| **2020s (Carga Espacial e Intensidade)** | 99.0 | 7.0 | 532 | 88.7% |

---

### 3. Distribuição do ACWR (Acute:Chronic Workload Ratio)
Distribuição das taxas de sobrecarga dos atletas no exato momento da ocorrência da lesão. Valores acima de `1.5` representam a zona de risco crítico:

![ACWR Distribution](reports/figures/acwr_distribution.png)

* **Eventos de Lesão Analisados:** 684
* **Ocorrências com ACWR > 1.5:** 623 (**91,1%**)
* **Média do ACWR no Momento da Lesão:** 3.55

---

## 🤖 Pipeline de Machine Learning e Auditoria de Regras

1. **Isolation Forest (Não Supervisionado):** Identifica anomalias extremas de carga biomecânica sem dependência de rótulos (1.985 partidas anômalas).
2. **Random Forest Classifier (Supervisionado):** Ajustado com `class_weight='balanced'` para priorizar a **Sensibilidade (Recall)** na detecção de risco.
3. **Auditor de Regras (Árvore de Decisão Explicável):** Extrai regras condicionais diretas indicando gatilhos de saturação de carga.

![Matriz de Confusão](reports/figures/confusion_matrix.png)

---

## 🛠️ Como Executar o Projeto

1. Instalar dependências: `pip install duckdb dbt-duckdb scikit-learn matplotlib seaborn pandas`
2. Executar pipeline do dbt: `cd dbt; dbt run --profiles-dir .; cd ..`
3. Gerar relatórios e gráficos: `python scripts/analytics/plot_insights.py`
4. Treinar modelo de ML e extrair regras: `python scripts/ml/train_injury_risk_model.py`
