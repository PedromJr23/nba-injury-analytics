# 🏀 NBA Injury Analytics: Análise de Carga, Ritmo e Risco de Lesões (1980–2024)

Pipeline end-to-end de engenharia de dados, analytics e machine learning construído para investigar o impacto biomecânico da era "Pace & Space" sobre a carga de trabalho dos atletas da NBA, a transição anatômica das lesões e o custo financeiro direto para as franquias.

---

## 📌 Principais Conclusões e Insights dos Dados

1. **Explosão do Volume de Lesões:** Os registros de lesões teciduais nas décadas de 2010 e 2020 saltaram para **> 1.200 registros/década** contra ~500 nas eras anteriores.
2. **Mapeamento Biomecânico (Zona da Quadra vs. Região do Corpo):**
   * **Zona de Garrafão (Era 1980–1999):** Movimentos de salto vertical e contato físico em espaço reduzido $\rightarrow$ Impactos articulares em **Tornozelos e Contusões Ósseas**.
   * **Zona do Perímetro / Linha de 3P (Era 2010–2024):** Ações de alta velocidade espacial, fechamento de espaço (closeouts), trocas de direção laterais e desacelerações bruscas $\rightarrow$ Estresse sob tração em **Posterior de Coxa (Hamstrings), Virilha/Adutores e Tendão Patelar**.
3. **Picos de ACWR como Gatilho Principal:** **91,1%** das lesões por sobrecarga ocorreram com a Razão Carga Aguda : Carga Crônica (**ACWR > 1,5**).
4. **Custo Financeiro para as Franquias:** Na era moderna, o custo estimado em salários pagos a atletas afastados por lesões teciduais de perímetro lidera os prejuízos de folha salarial.

---

## 🗺️ Mapeamento Cruzado: Zona da Quadra $\rightarrow$ Ação $\rightarrow$ Região Corporal $\rightarrow$ Custo

| Zona Principal da Quadra | Padrão de Movimento Dominante | Estresse Biomecânico | Região do Corpo Afetada | Gravidade Média | Custo Estimado por Evento |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Garrafão / Pintado** | Salto vertical, aterrisagem sobre pés e contato corporal direto | Inversão/Eversão de tornozelo e trauma de impacto | **Tornozelo, Joelho (Contato) e Costas** | 3 a 8 jogos | ~$150k – $350k |
| **Perímetro / Linha de 3P** | Desaceleração súbita para arremesso (*step-back*) e arranque explisivo | Sobrecarga excêntrica no quadríceps e miosite | **Tendão Patelar (Joelho) e Virilha** | 12 a 25 jogos | ~$600k – $1.5M |
| **Transição / Transição Aberta** | *Sprints* de quadra inteira e troca de direção (*crossover*) | Força de cisalhamento e estiramento miossepta | **Posterior de Coxa (Hamstring)** | 10 a 20 jogos | ~$500k – $1.2M |
| **Fechamento de Espaço (*Closeouts*)** | Frenagem contínua para contestar chutes a 8m da cesta | Carga rotacional e torção do pivô articular | **Tornozelo e Ligamento Patelar** | 5 a 15 jogos | ~$250k – $800k |

---

## 🔬 Metodologia & Arquitetura

O projeto utiliza a arquitetura **Medallion** implementada no **DuckDB** e transformada via **dbt (data build tool)**:

* **Camada Bronze:** Game logs brutos, tracking de distância/velocidade e histórico de lesões (~40k partidas e 3.300+ lesões).
* **Camada Silver:** Taxonomia padronizada de lesões (*Overuse/Soft Tissue* vs. *Trauma/Contact*), janelas móveis de carga aguda (7d), carga crônica (28d) e flags de *Back-to-Back*.
* **Camada Gold:** Marts analíticos ligando métricas de *Pace/Space* com custo financeiro em salários e risco preditivo.

---

## 📊 Evidências Estatísticas e Visualizações

### 1. Mudança na Distribuição Anatômica do Corpo (1980–1999 vs. 2010–2024)
![Top Lesões por Era](reports/figures/top_injuries_by_era.png)

---

### 2. Prejuízo Financeiro Estimado por Tipo de Lesão na Era Moderna ($ Milhões)
![Custo Financeiro das Lesões](reports/figures/injury_financial_cost.png)

---

### 3. Pace da Liga vs. Lesões por Sobrecarga (1980–2024)
| Era | Pace Médio | Arremessos de 3P (`fg3a`) | Lesões por Sobrecarga | % Lesões de Sobrecarga |
| :--- | :---: | :---: | :---: | :---: |
| **1980s (Era de Contato Físico)** | 101.0 | 1.5 | 441 | 88.2% |
| **1990s (Era do Hand-Check Defensivo)** | 91.5 | 3.0 | 427 | 85.4% |
| **2000s (Isolamento e Média Distância)** | 91.5 | 3.0 | 433 | 86.6% |
| **2010s (Explosão do Pace & Space)** | 99.0 | 7.0 | 1.047 | 87.2% |
| **2020s (Carga Espacial e Intensidade)** | 99.0 | 7.0 | 532 | 88.7% |

---

### 4. Distribuição do ACWR (Acute:Chronic Workload Ratio)
![ACWR Distribution](reports/figures/acwr_distribution.png)

* **Eventos de Lesão Analisados:** 684
* **Ocorrências com ACWR > 1.5:** 623 (**91,1%**)
* **Média do ACWR no Momento da Lesão:** 3.55

---

## 🤖 Pipeline de Machine Learning e Auditoria de Regras

1. **Isolation Forest (Não Supervisionado):** Identifica anomalias de carga biomecânica sem viés de rótulo.
2. **Random Forest Classifier (Supervisionado):** Ajustado com `class_weight='balanced'` para priorizar a Sensibilidade (**Recall**).
3. **Auditor de Regras:** Extração transparente de gatilhos condicionais por Árvore de Decisão.

![Matriz de Confusão](reports/figures/confusion_matrix.png)

---

## 🛠️ Como Executar o Projeto

1. Instalar dependências: `pip install duckdb dbt-duckdb scikit-learn matplotlib seaborn pandas`
2. Executar pipeline do dbt: `cd dbt; dbt run --profiles-dir .; cd ..`
3. Gerar relatórios e gráficos: `python scripts/analytics/plot_insights.py`
4. Treinar modelo de ML: `python scripts/ml/train_injury_risk_model.py`
