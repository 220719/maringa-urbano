import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

PROCESSED = Path(__file__).parent.parent.parent / "data" / "processed"

@st.cache_data
def load_data():
    gdf = gpd.read_file(PROCESSED / "maringa_iqu.geojson")
    resumo = pd.read_csv(PROCESSED / "resumo_bairros.csv")
    return gdf, resumo

def render():
    gdf, resumo = load_data()

    st.markdown("# Maringa Urbano")
    st.markdown("### Plataforma de Inteligencia Urbana - Equipamentos e Infraestrutura")
    st.markdown("---")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    metricas = [
        (c1, "Saude",         int(gdf["saude"].sum()),                 "equipamentos"),
        (c2, "Educacao",      int(gdf["educacao"].sum()),              "equipamentos"),
        (c3, "Mobilidade",    int(gdf["mobilidade"].sum()),            "pontos"),
        (c4, "Qualidade Vida",int(gdf["qualidade_vida"].sum()),        "equipamentos"),
        (c5, "Servicos",      int(gdf["servicos_essenciais"].sum()),   "equipamentos"),
        (c6, "Seguranca",     int(gdf["seguranca"].sum()),             "equipamentos"),
    ]
    for col, label, valor, unidade in metricas:
        with col:
            st.metric(label, f"{valor}", unidade)

    st.markdown("")
    total_eq = int(gdf[["saude","educacao","mobilidade","qualidade_vida","servicos_essenciais","seguranca"]].sum().sum())
    iqu_medio = float(gdf["iqu"].mean())
    setores_criticos = int((gdf["iqu_classe"] == "Muito Baixo").sum())
    setores_bons = int(gdf["iqu_classe"].isin(["Alto", "Muito Alto"]).sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Equipamentos", f"{total_eq:,}")
    with c2: st.metric("IQU Medio Maringa", f"{iqu_medio:.2f} / 10")
    with c3: st.metric("Setores Criticos", f"{setores_criticos}")
    with c4: st.metric("Setores Bem Servidos", f"{setores_bons}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Distribuicao do IQU por Setor")
        dist = gdf["iqu_classe"].value_counts().reindex(
            ["Muito Baixo", "Baixo", "Moderado", "Alto", "Muito Alto"]
        ).reset_index()
        dist.columns = ["Classe", "Setores"]
        fig = px.bar(dist, x="Classe", y="Setores", color="Classe",
                     color_discrete_sequence=["#da3633","#d29922","#3fb950","#1f6feb","#58a6ff"],
                     template="plotly_dark")
        fig.update_layout(showlegend=False, plot_bgcolor="#161b22",
                          paper_bgcolor="#161b22", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Top 10 Bairros por IQU")
        top = resumo.head(10).sort_values("iqu_medio")
        fig2 = px.bar(top, x="iqu_medio", y="NM_BAIRRO", orientation="h",
                      color="iqu_medio", color_continuous_scale="Blues",
                      template="plotly_dark", labels={"iqu_medio": "IQU", "NM_BAIRRO": ""})
        fig2.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#161b22",
                           height=300, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Composicao por Categoria")
    cats = {
        "Saude": int(gdf["saude"].sum()),
        "Educacao": int(gdf["educacao"].sum()),
        "Mobilidade": int(gdf["mobilidade"].sum()),
        "Qualidade de Vida": int(gdf["qualidade_vida"].sum()),
        "Servicos Essenciais": int(gdf["servicos_essenciais"].sum()),
        "Seguranca": int(gdf["seguranca"].sum()),
    }
    fig3 = go.Figure(go.Pie(
        labels=list(cats.keys()), values=list(cats.values()),
        hole=0.5,
        marker_colors=["#f85149","#d29922","#3fb950","#58a6ff","#bc8cff","#ff7b72"]
    ))
    fig3.update_layout(template="plotly_dark", paper_bgcolor="#161b22",
                       plot_bgcolor="#161b22", height=300,
                       legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(fig3, use_container_width=True)
