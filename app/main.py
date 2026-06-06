"""
Maringá Urbano — Plataforma de Inteligência Urbana
Vitrine do projeto: mapa aéreo + camadas GeoPandas + IQU
"""

import streamlit as st

st.set_page_config(
    page_title="Maringá Urbano",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS customizado
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0d1117; }
    [data-testid="stSidebar"] * { color: #e6edf3 !important; }
    .main { background-color: #0d1117; }
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #58a6ff; }
    .metric-label { font-size: 0.8rem; color: #8b949e; margin-top: 4px; }
    h1, h2, h3 { color: #e6edf3 !important; }
    .stSelectbox label { color: #8b949e !important; }
</style>
""", unsafe_allow_html=True)

# Navegação
paginas = {
    "🏠 Dashboard":        "dashboard",
    "🗺️ Mapa de Cobertura": "mapa",
    "📊 Análise por Bairro": "bairros",
    "🤖 ML — Perfil Urbano": "ml",
}

with st.sidebar:
    st.image("https://via.placeholder.com/200x60/0d1117/58a6ff?text=Maringá+Urbano", width=200)
    st.markdown("### 🏙️ Inteligência Urbana")
    st.markdown("---")
    pagina = st.radio("Navegação", list(paginas.keys()), label_visibility="collapsed")
    st.markdown("---")
    st.markdown("""
    <small style='color:#8b949e'>
    Dados: OSM Overpass API + IBGE Censo 2022<br>
    Atualizado: Jun/2025
    </small>
    """, unsafe_allow_html=True)

# Roteamento
slug = paginas[pagina]

if slug == "dashboard":
    from pages import dashboard; dashboard.render()
elif slug == "mapa":
    from pages import mapa; mapa.render()
elif slug == "bairros":
    from pages import bairros; bairros.render()
elif slug == "ml":
    from pages import ml; ml.render()
