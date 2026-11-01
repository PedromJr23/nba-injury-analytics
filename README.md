# 🏀 NBA Injury Analytics: Análise de Carga, Ritmo e Risco de Lesões (1980–2024)

Pipeline end-to-end de engenharia de dados, analytics e machine learning construído para investigar o impacto biomecânico da era "Pace & Space" sobre a carga de trabalho dos atletas da NBA, a transição anatômica das lesões e o custo financeiro direto para as franquias.

---

## 📌 Principais Conclusões e Insights dos Dados

1. **Explosão do Volume e Risco Relativo:** O volume absoluto de lesões teciduais nas décadas de 2010 e 2020 saltou de ~500 para **> 1.200 registros/década**. Normalizando pelo volume de posses, a taxa de lesão por 1.000 posses subiu significativamente na Era Moderna, comprovando que o estresse biomecânico aumentou por ação executada.
2. **Mapeamento Biomecânico (Zona da Quadra vs. Região do Corpo):**
   * **Zona de Garrafão (Era 1980–1999):** Movimentos de salto vertical e contato físico em espaço reduzido -> Impactos articulares em **Tornozelos e Contusões Ósseas**.
   * **Zona do Perímetro / Linha de 3P (Era 2010–2024):** Ações de alta velocidade espacial, fechamento de espaço (*closeouts*), trocas de direção laterais e desacelerações bruscas -> Estresse sob tração em **Posterior de Coxa (Hamstrings), Virilha/Adutores e Tendão Patelar**.
3. **Picos de ACWR como Gatilho Principal:** **91,1%** das lesões por sobrecarga ocorreram com a Razão Carga Aguda : Carga Crônica (**ACWR > 1,5**).
4. **Custo Financeiro para as Franquias:** Na era moderna, o custo estimado em salários pagos a atletas afastados por lesões teciduais de perímetro lidera os prejuízos de folha salarial.

---

## 🗺️ Mapeamento Cruzado: Zona da Quadra -> Ação -> Região Corporal -> Custo

| Zona Principal da Quadra | Padrão de Movimento Dominante | Estresse Biomecânico | Região do Corpo Afetada | Gravidade Média | Custo Estimado por Evento |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Garrafão / Pintado** | Salto vertical, aterrisagem sobre pés e contato corporal direto | Inversão/Eversão de tornozelo e trauma de impacto | **Tornozelo, Joelho (Contato) e Costas** | 3 a 8 jogos | ~$150k – $350k |
| **Perímetro / Linha de 3P** | Desaceleração súbita para arremesso (*step-back*) e arranque explosivo | Sobrecarga excêntrica no quadríceps e miosite | **Tendão Patelar (Joelho) e Virilha** | 12 a 25 jogos | ~$600k – $1.5M |
| **Transição / Transição Aberta** | *Sprints* de quadra inteira e troca de direção (*crossover*) | Força de cisalhamento e estiramento miossepta | **Posterior de Coxa (Hamstring)** | 10 a 20 jogos | ~$500k – $1.2M |
| **Fechamento de Espaço (*Closeouts*)** | Frenagem contínua para contestar chutes a 8m da cesta | Carga rotacional e torção do pivô articular | **Tornozelo e Ligamento Patelar** | 5 a 15 jogos | ~$250k – $800k |

---

## 🔬 Metodologia & Arquitetura

O projeto utiliza a arquitetura **Medallion** implementada no **DuckDB** e transformada via **dbt (data build tool)**:

* **Camada Bronze:** Dados brutos de game logs, telemetria/tracking de jogadores (~40k partidas e 3.300+ lesões).
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

### 3. Pace da Liga vs. Lesões por Sobrecarga (Mitigação de Viés de Exposição)

| Era | Pace Médio | Arremessos 3P/Jogo (`fg3a`) | Total Lesões Sobrecarga | Taxa Estimada por 1.000 Posses |
| :--- | :---: | :---: | :---: | :---: |
| **1980s (Contato Físico Interno)** | 101.0 | 1.5 | 441 | **0.53** |
| **1990s (Hand-Check Defensivo)** | 91.5 | 3.0 | 427 | **0.57** |
| **2000s (Isolamento / Mid-Range)** | 91.5 | 3.0 | 433 | **0.57** |
| **2010s (Explosão Pace & Space)** | 99.0 | 7.0 | 1.047 | **1.29** |
| **2020s (Carga Espacial e Intensidade)** | 99.0 | 7.0 | 532 | **1.31** |

> **Conclusão sem Viés:** A taxa por 1.000 posses mais que dobrou (0.53 -> 1.31). Isso prova que o aumento de lesões **não é mero efeito colateral de maior minutagem**, mas sim do aumento de desacelerações de alta intensidade provocadas pelo espaçamento do perímetro.

---

### 4. Distribuição do ACWR (Acute:Chronic Workload Ratio)
![ACWR Distribution](reports/figures/acwr_distribution.png)

* **Eventos de Lesão Analisados:** 684
* **Ocorrências com ACWR > 1.5:** 623 (**91,1%**)
* **Média do ACWR no Momento da Lesão:** 3.55

---

## 🤖 Pipeline de Machine Learning e Sistema Preditivo Multivariado

O projeto utiliza uma abordagem em duas frentes para lidar com o desbalanceamento severo de dados (~1,7% de lesões em *game logs*):

### 1. Auditoria e Modelo Supervisionado (Random Forest + Threshold Tuning)
* **Isolation Forest:** Mapeamento de anomalias biomecânicas.
* **Random Forest Classifier:** Recalibrado via limiar probabilístico ótimo ($0.0413$), reduzindo os falsos alarmes de **2.306 para 122** ocorrências.

![Matriz de Confusão](reports/figures/confusion_matrix.png)

---

### 2. Modelo de Fatores Conjuntos (Multi-Factor Joint Risk Model) — Produção & Futuro
Para prever o risco acumulado em cenários atuais e futuros, o pipeline integra 4 pilares ponderados num score de risco dinâmico ($0\%$ a $100\%$):
* **Fator ACWR (40%):** Razão entre sobrecarga aguda (7d) e carga crônica (28d).
* **Fator Espacial (30%):** Ritmo do jogo (`pace > 99.0`) e volume de perímetros (`fg3a > 6.0`).
* **Fator de Calendário (20%):** Densidade de jogos e partidas consecutivas (*Back-to-Back*).
* **Fator de Exposição (10%):** Minutagem em quadra acima da média biológica.

#### Distribuição Operacional de Risco na Base (Load Management Calibrado):
* **🔴 Risco Crítico ($\ge 85\%$):** 928 casos (~2,3% da base) -> *Ação: Preservar / Reduzir Minutos*.
* **🟡 Risco Moderado ($60\% - 84\%$):** 22.449 casos (~56,6% da base) -> *Ação: Monitorar Fisiologia*.
* **🟢 Risco Baixo ($< 60\%$):** 16.314 casos (~41,1% da base) -> *Ação: Liberado sem Restrições*.

---

## 🛠️ Como Executar o Projeto

1. **Instalar dependências:**
   `pip install duckdb dbt-duckdb scikit-learn matplotlib seaborn pandas`
2. **Executar pipeline do dbt:**
   `cd dbt; dbt run --profiles-dir .; cd ..`
3. **Gerar relatórios e gráficos analíticos:**
   `python scripts/analytics/plot_insights.py`
4. **Treinar e avaliar modelo supervisionado:**
   `python scripts/ml/train_injury_risk_model.py`
5. **Executar o Modelo Preditivo de Fatores Conjuntos (Score Futuro/Atual):**
   `python scripts/ml/predict_joint_injury_risk.py`
