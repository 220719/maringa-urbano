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
    bairros = pd.read_csv(PROCESSED / "resumo_bairros_completo.csv")
    return gdf, bairros

CORES_CLASSE = {
    "Muito Baixo": "#ef5350",
    "Baixo":       "#FFA726",
    "Moderado":    "#FFEE58",
    "Alto":        "#66BB6A",
    "Muito Alto":  "#42A5F5",
}

def iqu_classe(v):
    if v >= 8: return "Muito Alto"
    if v >= 6: return "Alto"
    if v >= 4: return "Moderado"
    if v >= 2: return "Baixo"
    return "Muito Baixo"

def render_autor():
    import streamlit as st
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("""
        <div style="background:#fff8f0;border:2px solid #f97316;border-radius:12px;
                    padding:24px;text-align:center;max-width:220px">
            <div style="font-size:3rem">👨‍🔬</div>
            <div style="font-size:1.1rem;font-weight:800;color:#f97316;margin-top:8px">
                Anuar<br>Mincache
            </div>
            <div style="font-size:0.75rem;color:#888;margin-top:8px;line-height:1.6">
                PhD Physics | Data Science<br>
                Machine Learning | Research
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="padding:8px 0">
            <h3 style="color:#f97316;margin-bottom:12px">Sobre este projeto</h3>
            <p style="font-size:0.95rem;line-height:1.7;color:#333">
                Plataforma de <b>inteligência urbana</b> que mapeia e analisa
                equipamentos públicos de Maringá-PR, combinando
                geoprocessamento, machine learning e dados abertos.
            </p>
            <p style="font-size:0.95rem;line-height:1.7;color:#333">
                Dados reais via <b>OSM Overpass API</b> e <b>IBGE Censo 2022</b> —
                3.072 equipamentos · 47 zonas · 793 setores censitários.
            </p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.link_button("🔗 LinkedIn", "https://linkedin.com/in/anuar-mincache",
                          use_container_width=True)
        with c2:
            st.link_button("🐙 GitHub", "https://github.com/220719",
                          use_container_width=True)
        with c3:
            st.link_button("📦 Repositório", "https://github.com/220719/maringa-urbano",
                          use_container_width=True)
        with c4:
            st.link_button("🔬 ORCID", "https://orcid.org/0000-0001-8528-8020",
                          use_container_width=True)

        st.markdown("""
        <div style="background:#16a34a;color:white;border-radius:20px;
                    padding:8px 16px;text-align:center;font-size:0.8rem;margin-top:8px">
            📍 Em operação — Maringá, Paraná · Jun/2025
        </div>
        """, unsafe_allow_html=True)