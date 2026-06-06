import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from pathlib import Path

PROCESSED = Path(__file__).parent.parent.parent / "data" / "processed"
RAW       = Path(__file__).parent.parent.parent / "data" / "raw"

ICONES = {
    "saude":               ("red",    "plus-sign"),
    "educacao":            ("orange", "book"),
    "qualidade_vida":      ("green",  "leaf"),
    "servicos_essenciais": ("purple", "shopping-cart"),
    "seguranca":           ("darkred","shield"),
}

LABELS = {
    "saude":               "Saúde",
    "educacao":            "Educação",
    "mobilidade":          "Mobilidade",
    "qualidade_vida":      "Qualidade de Vida",
    "servicos_essenciais": "Serviços Essenciais",
    "seguranca":           "Segurança",
}

PERFIS_COR = {
    0: "#42A5F5",  # Estruturada
    1: "#ef5350",  # Carente
    2: "#FFA726",  # Alta Mobilidade
}

DESCRICOES_ZONA = {
    "Zona 1":    "Centro e Novo Centro",
    "Zona 2":    "Catedral / Parque do Ingá",
    "Zona 3":    "Vila Operária",
    "Zona 4":    "Área Nobre / Saúde",
    "Zona 5":    "Maringá Velho",
    "Zona 7":    "Região Universitária (UEM)",
    "Zona 23":   "Vila Morangueira",
    "Zona Central": "Centro Histórico",
}

PERFIS_NOME = {
    0: "Zona Estruturada",
    1: "Zona Carente",
    2: "Alta Mobilidade",
}

@st.cache_data
def load_gdf():
    gdf = gpd.read_file(PROCESSED / "maringa_iqu.geojson")
    gdf["NM_BAIRRO"]  = gdf["NM_BAIRRO"].fillna("Sem nome")
    gdf["NM_SUBDIST"] = gdf["NM_SUBDIST"].fillna("Sem zona")
    gdf["iqu_classe"] = gdf["iqu_classe"].astype(str)
    # Junta cluster por zona
    zonas = pd.read_csv(PROCESSED / "zonas_clusters.csv")[["NM_SUBDIST","cluster","iqu_mediano"]]
    gdf = gdf.merge(zonas, on="NM_SUBDIST", how="left")
    gdf["cluster"]     = gdf["cluster"].fillna(-1).astype(int)
    gdf["iqu_mediano"] = gdf["iqu_mediano"].fillna(0).round(2)
    gdf["iqu_mediano"] = gdf["iqu_mediano"].fillna(0)
    return gdf

@st.cache_data
def load_osm():
    return gpd.read_file(RAW / "osm_todos.geojson")

@st.cache_data
def load_boundary():
    return gpd.read_file(RAW / "maringa_boundary.geojson")

def cor_iqu(iqu):
    if iqu >= 8: return "#42A5F5"
    if iqu >= 6: return "#66BB6A"
    if iqu >= 4: return "#FFEE58"
    if iqu >= 2: return "#FFA726"
    return "#ef5350"

def cor_cluster(cluster):
    try:
        return PERFIS_COR.get(int(cluster), "#888")
    except:
        return "#888"

def build_map(gdf, osm, boundary, cats_ativas, tile, modo_cor):
    m = folium.Map(location=[-23.425, -51.938], zoom_start=12, tiles=None)

    tiles_map = {
        "Satélite": ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", "Esri"),
        "Ruas":     ("OpenStreetMap", "OpenStreetMap"),
        "Dark":     ("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", "CartoDB"),
    }
    for nome, (url, attr) in tiles_map.items():
        folium.TileLayer(tiles=url, attr=attr, name=nome, show=(nome==tile)).add_to(m)

    # Boundary
    folium.GeoJson(
        boundary.__geo_interface__,
        style_function=lambda f: {
            "fillColor": "transparent", "color": "#42A5F5",
            "weight": 2.5, "dashArray": "6 4",
        },
        name="Limite Municipal", show=True,
    ).add_to(m)

    # Choropleth — IQU ou Cluster
    def style_fn(feature):
        if modo_cor == "IQU por Setor":
            iqu = float(feature["properties"].get("iqu", 0) or 0)
            fill = cor_iqu(iqu)
        else:
            cluster = int(feature["properties"].get("cluster", -1) or -1)
            fill = cor_cluster(cluster)
        return {"fillColor": fill, "fillOpacity": 0.6, "color": "#222", "weight": 0.5}

    def highlight_fn(feature):
        return {"fillOpacity": 0.85, "weight": 2, "color": "#fff"}

    # Adiciona descrição contextual ao GDF para o tooltip
    gdf["descricao"] = gdf["NM_SUBDIST"].map(DESCRICOES_ZONA).fillna("")

    tooltip = folium.GeoJsonTooltip(
        fields=["NM_SUBDIST", "descricao", "NM_BAIRRO", "iqu", "total_equipamentos"],
        aliases=["Zona:", "Contexto:", "Bairro:", "IQU Setor:", "Equipamentos:"],
        localize=True, sticky=True,
        style="font-family:sans-serif;font-size:12px;",
    )

    popup = folium.GeoJsonPopup(
        fields=["NM_SUBDIST","NM_BAIRRO","iqu","iqu_classe",
                "saude","educacao","mobilidade",
                "qualidade_vida","servicos_essenciais","seguranca","total_equipamentos"],
        aliases=["Zona","Bairro","IQU Setor","Classe",
                 "Saúde","Educação","Mobilidade",
                 "Qual. Vida","Serviços","Segurança","Total"],
        localize=True, max_width=280,
    )

    folium.GeoJson(
        gdf.__geo_interface__,
        name="Setores Censitários",
        style_function=style_fn,
        highlight_function=highlight_fn,
        tooltip=tooltip,
        popup=popup,
        show=True,
    ).add_to(m)

    # Equipamentos
    for cat in cats_ativas:
        if cat == "mobilidade":
            grupo_mob = folium.FeatureGroup(name="Mobilidade", show=True)
            for _, eq in osm[osm["categoria"]=="mobilidade"].iterrows():
                folium.CircleMarker(
                    location=[eq.geometry.y, eq.geometry.x],
                    radius=3, color="#42A5F5", fill=True, fill_opacity=0.7,
                    tooltip=eq["nome"] if eq["nome"] != "Sem nome" else "Ponto de ônibus",
                ).add_to(grupo_mob)
            grupo_mob.add_to(m)
            continue

        cor, icone = ICONES[cat]
        grupo = MarkerCluster(name=LABELS[cat], show=True)
        for _, eq in osm[osm["categoria"]==cat].iterrows():
            nome = eq["nome"] if eq["nome"] != "Sem nome" else LABELS[cat]
            folium.Marker(
                location=[eq.geometry.y, eq.geometry.x],
                popup=folium.Popup(f"<b>{nome}</b><br><i>{LABELS[cat]}</i>", max_width=180),
                tooltip=nome,
                icon=folium.Icon(color=cor, icon=icone, prefix="glyphicon"),
            ).add_to(grupo)
        grupo.add_to(m)

    # Legenda dinâmica
    if modo_cor == "IQU por Setor":
        legenda_html = """
        <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                    background:white;padding:12px 16px;border-radius:8px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.3);font-family:sans-serif;font-size:12px">
            <b>IQU — Índice de Qualidade Urbana</b><br><br>
            <span style="color:#42A5F5;font-size:16px">■</span> Muito Alto (8–10)<br>
            <span style="color:#66BB6A;font-size:16px">■</span> Alto (6–8)<br>
            <span style="color:#FFEE58;font-size:16px">■</span> Moderado (4–6)<br>
            <span style="color:#FFA726;font-size:16px">■</span> Baixo (2–4)<br>
            <span style="color:#ef5350;font-size:16px">■</span> Muito Baixo (0–2)
        </div>"""
    else:
        legenda_html = """
        <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                    background:white;padding:12px 16px;border-radius:8px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.3);font-family:sans-serif;font-size:12px">
            <b>Perfil Urbano (ML)</b><br><br>
            <span style="color:#42A5F5;font-size:16px">■</span> Zona Consolidada<br>
            <span style="color:#FFA726;font-size:16px">■</span> Zona em Desenvolvimento<br>
            <span style="color:#ef5350;font-size:16px">■</span> Zona de Expansão
        </div>"""

    m.get_root().html.add_child(folium.Element(legenda_html))
    folium.LayerControl(collapsed=False).add_to(m)
    return m

def render():
    st.markdown("## 🗺️ Mapa de Cobertura Urbana")
    st.caption("Visualize Maringá por zona · Clique num setor para detalhes · Hover para tooltip rápido")
    st.markdown("---")

    gdf      = load_gdf()
    osm      = load_osm()
    boundary = load_boundary()

    col1, col2 = st.columns(2)
    with col1:
        tile = st.radio("Mapa base:", ["Satélite","Dark","Ruas"], horizontal=True)
    with col2:
        modo_cor = st.radio(
            "Colorir por:",
            ["IQU por Setor", "Perfil ML (Cluster)"],
            horizontal=True
        )

    st.markdown("**Camadas de equipamentos:**")
    cols = st.columns(6)
    cats_ativas = []
    for i, (cat, label) in enumerate(LABELS.items()):
        with cols[i]:
            default = cat not in ["mobilidade"]
            if st.checkbox(label, value=default, key=f"chk_{cat}"):
                cats_ativas.append(cat)

    st.caption("💡 Dois modos de cor: IQU por setor censitário ou Perfil ML por zona. Clique num setor para popup completo.")

    with st.spinner("Renderizando mapa..."):
        m = build_map(gdf, osm, boundary, cats_ativas, tile, modo_cor)
        st_folium(m, width="100%", height=650, returned_objects=[])

    if modo_cor == "Perfil ML (Cluster)":
        st.markdown("---")
        st.markdown("#### O que significa cada perfil ML?")
        st.caption("O modelo K-Means agrupou as 47 zonas de Maringá em 3 perfis com base em 7 variáveis urbanas.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div style="background:#1e1e2e;border-left:5px solid #42A5F5;border-radius:8px;padding:16px">
                <div style="color:#42A5F5;font-weight:700;font-size:1rem">🏙️ Zona Consolidada</div>
                <div style="color:#aaa;font-size:0.85rem;margin-top:8px;line-height:1.6">
                    Zonas com <b style="color:#fff">melhor cobertura geral</b> de equipamentos urbanos.
                    Inclui o centro, área universitária (Zona 7) e zonas nobres.
                    IQU ponderado acima de <b style="color:#42A5F5">3.4</b>.
                </div>
                <div style="margin-top:10px;font-size:0.75rem;color:#555">
                    Zonas: 1, 2, 4, 5, 7, 8, 24, 40
                </div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div style="background:#1e1e2e;border-left:5px solid #FFA726;border-radius:8px;padding:16px">
                <div style="color:#FFA726;font-weight:700;font-size:1rem">🌱 Zona em Desenvolvimento</div>
                <div style="color:#aaa;font-size:0.85rem;margin-top:8px;line-height:1.6">
                    Zonas com <b style="color:#fff">cobertura intermediária</b>.
                    Boa mobilidade (ônibus) mas ainda carentes em saúde e serviços essenciais.
                    IQU ponderado entre <b style="color:#FFA726">2.0 e 3.4</b>.
                </div>
                <div style="margin-top:10px;font-size:0.75rem;color:#555">
                    26 zonas — maioria do perímetro urbano
                </div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div style="background:#1e1e2e;border-left:5px solid #ef5350;border-radius:8px;padding:16px">
                <div style="color:#ef5350;font-weight:700;font-size:1rem">🚧 Zona de Expansão</div>
                <div style="color:#aaa;font-size:0.85rem;margin-top:8px;line-height:1.6">
                    Zonas <b style="color:#fff">periféricas e de expansão urbana</b>.
                    Alta mobilidade mas baixa cobertura em saúde, educação e segurança.
                    <b style="color:#ef5350">Prioridade de investimento público</b>.
                </div>
                <div style="margin-top:10px;font-size:0.75rem;color:#555">
                    13 zonas — periferia e expansão
                </div>
            </div>""", unsafe_allow_html=True)
        st.info("💡 **Como interpretar:** Zonas da mesma cor têm perfil urbano similar. "
                "Zonas vermelhas indicam onde a prefeitura deveria priorizar investimentos em equipamentos públicos.")

