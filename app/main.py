import streamlit as st

st.set_page_config(
    page_title="Maringá Urbano",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        background: #0d1117 !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #c9d1d9 !important;
        font-size: 0.95rem !important;
        padding: 6px 4px !important;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #8b949e !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #21262d !important;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="padding:12px 0 16px">
        <div style="font-size:1.8rem;font-weight:900;line-height:1.1">
            <span style="color:#3b82f6">Maringá</span>
            <span style="color:#ffffff"> Urbano</span>
        </div>
        <div style="font-size:0.62rem;color:#475569;letter-spacing:3px;margin-top:4px">
            INTELIGÊNCIA URBANA
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    pagina = st.radio(
        "nav",
        [
            "🏠  Dashboard",
            "🗺️  Mapa de Cobertura",
            "📊  Análise por Zona",
            "🤖  ML — Perfil Urbano",
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("""
    <div style="font-size:0.75rem;line-height:2.2">
        <div style="color:#58a6ff;font-weight:600;margin-bottom:4px">Fontes de dados</div>
        <div><span style="color:#3b82f6">●</span> <span style="color:#8b949e">OSM Overpass API</span></div>
        <div><span style="color:#10b981">●</span> <span style="color:#8b949e">IBGE Censo 2022</span></div>
        <div><span style="color:#a78bfa">●</span> <span style="color:#8b949e">scikit-learn K-Means</span></div>
        <div><span style="color:#f59e0b">●</span> <span style="color:#8b949e">GeoPandas + Folium</span></div>
        <br>
        <div style="color:#30363d;font-size:0.7rem;line-height:1.8">
            <span style="color:#58a6ff">3.072</span> equipamentos<br>
            <span style="color:#58a6ff">793</span> setores · <span style="color:#58a6ff">113</span> bairros<br>
            <span style="color:#6e7681">Maringá–PR · Jun/2025</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

paginas = {
    "🏠  Dashboard":          "dashboard",
    "🗺️  Mapa de Cobertura":  "mapa",
    "📊  Análise por Zona": "bairros",
    "🤖  ML — Perfil Urbano": "ml",
}

slug = paginas[pagina]

if slug == "dashboard":
    from pages import dashboard; dashboard.render()
elif slug == "mapa":
    from pages import mapa; mapa.render()
elif slug == "bairros":
    from pages import bairros; bairros.render()
elif slug == "ml":
    from pages import ml; ml.render()
