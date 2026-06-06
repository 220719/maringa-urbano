# Maringá Urbano — Plataforma de Inteligência Urbana

> Plataforma de análise e visualização de equipamentos urbanos de Maringá-PR, combinando dados abertos do OpenStreetMap e IBGE Censo 2022 com Machine Learning e geoprocessamento.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.44-red)
![GeoPandas](https://img.shields.io/badge/GeoPandas-1.0-green)

---

## Sobre o Projeto

O **Maringá Urbano** mapeia e analisa **3.072 equipamentos urbanos** distribuídos em **47 zonas** e **793 setores censitários** de Maringá-PR. A plataforma combina extração automática de dados via OSM Overpass API e IBGE, geoprocessamento com GeoPandas e Folium, o Índice de Qualidade Urbana (IQU) ponderado por área, clustering K-Means para identificação de perfis urbanos e um dashboard interativo com mapa coroplético e análises por zona.

---

## Funcionalidades

**Dashboard** — KPIs por categoria, rankings Top/Bottom 10 zonas, cards visuais com indicadores.

**Mapa de Cobertura** — Choropleth IQU por setor censitário, toggle entre IQU e Perfil ML, camadas de equipamentos, popup detalhado, tiles Satélite/Dark/Ruas.

**Análise por Zona** — Ficha completa com contexto histórico, radar comparativo zona vs mediana, ranking entre as 47 zonas, comparador lado a lado.

**ML — Perfil Urbano** — K-Means k=3 (Silhouette=0.315), PCA 2D, radar triplo, 3 perfis:
- Zona Consolidada (Centro, universitária, nobres)
- Zona em Desenvolvimento (cobertura intermediária)
- Zona de Expansão (periferia, prioridade de investimento)

---

## Dados

| Fonte | Dados | Volume |
|---|---|---|
| OSM Overpass API | Equipamentos urbanos | 3.072 pontos |
| IBGE Censo 2022 | Setores censitários | 793 setores |
| IBGE API | Boundary municipal | 486 km² |

### Categorias de Equipamentos

| Categoria | Quantidade |
|---|---|
| Saúde (hospitais, clínicas, postos) | 78 |
| Educação (escolas, universidades, creches) | 187 |
| Mobilidade (pontos de ônibus, terminais) | 2.375 |
| Qualidade de Vida (parques, praças) | 240 |
| Serviços Essenciais (mercados, farmácias, bancos) | 175 |
| Segurança (delegacias, bombeiros) | 18 |

---

## Metodologia — IQU

O **Índice de Qualidade Urbana** é calculado em duas etapas:

**1. IQU por setor** — normalização por percentil rank com pesos: Saúde 25%, Educação 20%, Mobilidade 15%, Qualidade de Vida 15%, Serviços 15%, Segurança 10%.

**2. IQU por zona** — média ponderada pela área de cada setor, eliminando distorção de zonas grandes com muitos setores vazios (ex: Zona 7 corrigida de 0.42 para 3.43).

---

## Machine Learning

- Algoritmo: K-Means
- Features: 7 variáveis (6 categorias + IQU ponderado)
- Seleção de k: Silhouette Score (0.315 com k=3)
- Visualização: PCA 2D
- Resultado: 3 perfis urbanos distintos

---

## Como Rodar

Pré-requisitos: Python 3.12 e uv.

    git clone https://github.com/220719/maringa-urbano.git
    cd maringa-urbano
    uv venv .venv
    source .venv/bin/activate
    uv pip install -r requirements.txt

Extração de dados:

    python src/extract/osm_extract.py
    python src/extract/ibge_extract.py
    python src/transform/spatial_join.py
    python src/ml/clustering_zonas.py

Executar o app:

    streamlit run app/main.py

Acesse em http://localhost:8501

---

## Estrutura do Projeto

    maringa-urbano/
    ├── app/
    │   ├── main.py
    │   └── pages/
    │       ├── dashboard.py
    │       ├── mapa.py
    │       ├── bairros.py
    │       ├── ml.py
    │       └── hero.py
    ├── data/
    │   ├── raw/
    │   └── processed/
    ├── src/
    │   ├── extract/
    │   ├── transform/
    │   └── ml/
    ├── requirements.txt
    └── README.md

---

## Stack Tecnológica

| Tecnologia | Uso |
|---|---|
| Python 3.12 | Linguagem principal |
| Streamlit 1.44 | Frontend / Dashboard |
| GeoPandas 1.0 | Geoprocessamento |
| Folium 0.19 | Mapas interativos |
| scikit-learn 1.6 | K-Means + PCA |
| DuckDB 1.2 | Backend de dados |
| Plotly 6.0 | Visualizações interativas |
| OSM Overpass API | Equipamentos urbanos |
| IBGE API | Malha censitária |

---

## Autor

**Anuar Mincache**
- GitHub: https://github.com/220719
- LinkedIn: https://linkedin.com/in/anuar-mincache
- ORCID: https://orcid.org/0000-0001-8528-8020

---

*Dados: OSM Overpass API + IBGE Censo 2022 · Maringá-PR · Jun/2025*
