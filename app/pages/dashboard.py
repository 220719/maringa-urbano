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
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("""
        <div style="background:#fff8f0;border:2px solid #f97316;border-radius:12px;
                    padding:24px;text-align:center">
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
                Esta plataforma foi desenvolvida como parte de uma
                <b>pesquisa em inteligência urbana</b>, integrando técnicas modernas de
                geoprocessamento, aprendizado de máquina e dados abertos
                aplicados à gestão pública municipal de Maringá-PR.
            </p>
            <p style="font-size:0.95rem;line-height:1.7;color:#333">
                Os dados são reais, coletados via <b>OSM Overpass API</b> e
                <b>IBGE Censo 2022</b>, cobrindo 3.072 equipamentos urbanos
                em 47 zonas e 793 setores censitários.
            </p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.link_button("🔗 LinkedIn", "https://linkedin.com/in/anuar-mincache", use_container_width=True)
        with c2:
            st.link_button("🎓 Lattes", "http://lattes.cnpq.br/9526608938362113", use_container_width=True)
        with c3:
            st.link_button("🐙 GitHub", "https://github.com/220719", use_container_width=True)
        st.markdown("""
        <div style="background:#16a34a;color:white;border-radius:20px;
                    padding:8px 16px;text-align:center;font-size:0.8rem;margin-top:8px">
            📍 Em operação — Maringá, Paraná · Jun/2025 · OSM + IBGE Censo 2022
        </div>
        """, unsafe_allow_html=True)

def render():
    gdf, bairros = load_data()
    bairros["classe"] = bairros["iqu_mediano"].apply(iqu_classe)

    from pages.hero import render_hero
    render_hero()
    st.markdown("---")
    render_autor()
    st.markdown("---")

    st.info("""
**O que é o IQU — Índice de Qualidade Urbana?**
O IQU é uma nota de **0 a 10** por zona que combina seis dimensões:
**saúde**, **educação**, **mobilidade**, **qualidade de vida**, **serviços essenciais** e **segurança**.
Quanto maior, melhor servido é o bairro. Abaixo de 2 = zona crítica.
O mapa interativo completo está na aba **Mapa de Cobertura**.
""")

    st.markdown("---")
    st.markdown("#### Equipamentos Mapeados em Maringá")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col, label, cat, cor in [
        (c1,"Saude",         "saude",               "#ef5350"),
        (c2,"Educacao",      "educacao",             "#FFA726"),
        (c3,"Mobilidade",    "mobilidade",           "#42A5F5"),
        (c4,"Qual. Vida",    "qualidade_vida",       "#66BB6A"),
        (c5,"Servicos",      "servicos_essenciais",  "#AB47BC"),
        (c6,"Seguranca",     "seguranca",            "#FF7043"),
    ]:
        with col:
            valor = int(gdf[cat].sum())
            st.markdown(f"""
            <div style="background:#1e1e2e;border-left:4px solid {cor};border-radius:8px;
                        padding:14px 10px;text-align:center;margin-bottom:8px;">
                <div style="font-size:1.8rem;font-weight:800;color:{cor}">{valor}</div>
                <div style="font-size:0.75rem;color:#aaa;margin-top:4px">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")
    total_eq   = int(gdf[["saude","educacao","mobilidade","qualidade_vida","servicos_essenciais","seguranca"]].sum().sum())
    iqu_med    = float(bairros["iqu_mediano"].median())
    iqu_p25    = float(bairros["iqu_mediano"].quantile(0.25))
    iqu_p75    = float(bairros["iqu_mediano"].quantile(0.75))
    b_criticos = int((bairros["iqu_mediano"] < 2).sum())
    b_bons     = int((bairros["iqu_mediano"] >= 6).sum())

    c1,c2,c3,c4 = st.columns(4)
    for col, valor, label, cor in [
        (c1, f"{total_eq:,}",         "Total Equipamentos",              "#42A5F5"),
        (c2, f"{iqu_med:.2f}/10",     f"IQU Mediano  P25={iqu_p25:.1f} P75={iqu_p75:.1f}", "#66BB6A"),
        (c3, f"{b_criticos} bairros", "Bairros Criticos (IQU < 2)",      "#ef5350"),
        (c4, f"{b_bons} bairros",     "Bairros Bem Servidos (IQU >= 6)", "#FFA726"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#1e1e2e;border-radius:8px;padding:16px;text-align:center">
                <div style="font-size:1.4rem;font-weight:700;color:{cor}">{valor}</div>
                <div style="color:#aaa;font-size:0.75rem;margin-top:4px">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Top 10 Melhores Bairros")
    st.caption("Bairros com maior IQU mediano")
    top = bairros.head(10).sort_values("iqu_mediano")
    fig2 = px.bar(top, x="iqu_mediano", y="NM_BAIRRO", orientation="h",
                  color="iqu_mediano", color_continuous_scale=["#FFA726","#66BB6A","#42A5F5"],
                  template="plotly_dark", labels={"iqu_mediano":"IQU","NM_BAIRRO":""},
                  text=top["iqu_mediano"].apply(lambda x: f"{x:.1f}"))
    fig2.update_traces(textposition="outside")
    fig2.update_layout(plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
                       height=420, coloraxis_showscale=False, margin=dict(l=300,r=60,t=20,b=20))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Bottom 10 Bairros Criticos")
    st.caption("Bairros com menor IQU mediano — maior necessidade de investimento")
    bot = bairros.tail(10).sort_values("iqu_mediano", ascending=False)
    fig3 = px.bar(bot, x="iqu_mediano", y="NM_BAIRRO", orientation="h",
                  color="iqu_mediano", color_continuous_scale=["#ef5350","#FFA726","#FFEE58"],
                  template="plotly_dark", labels={"iqu_mediano":"IQU","NM_BAIRRO":""},
                  text=bot["iqu_mediano"].apply(lambda x: f"{x:.1f}"))
    fig3.update_traces(textposition="outside")
    fig3.update_layout(plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
                       height=420, coloraxis_showscale=False, margin=dict(l=300,r=60,t=20,b=20))
    st.plotly_chart(fig3, use_container_width=True)

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
    fig4 = go.Figure(go.Pie(
        labels=list(cats.keys()), values=list(cats.values()),
        hole=0.55, marker_colors=["#ef5350","#FFA726","#42A5F5","#66BB6A","#AB47BC","#FF7043"],
        textinfo="label+percent",
    ))
    fig4.update_layout(
        template="plotly_dark", paper_bgcolor="#1e1e2e", plot_bgcolor="#1e1e2e",
        height=380, legend=dict(orientation="h", y=-0.15),
        annotations=[dict(text=f"<b>{total_eq:,}</b><br>total", x=0.5, y=0.5,
                          font_size=16, showarrow=False, font_color="#fff")]
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Explorar Bairros por Classe de IQU")
    st.caption("113 bairros nomeados — filtre por classe e explore os indicadores")

    opcoes = ["Todos","Muito Baixo","Baixo","Moderado","Alto","Muito Alto"]
    if "classe_sel" not in st.session_state:
        st.session_state.classe_sel = "Todos"
    cols_btn = st.columns(6)
    for i, op in enumerate(opcoes):
        with cols_btn[i]:
            if st.button(op, key=f"btn_{op}", use_container_width=True):
                st.session_state.classe_sel = op

    df = bairros.copy()
    if st.session_state.classe_sel != "Todos":
        df = df[df["classe"] == st.session_state.classe_sel]
    df = df.sort_values("iqu_mediano", ascending=False).reset_index(drop=True)

    c1,c2,c3 = st.columns(3)
    with c1: st.metric("IQU Mediano", f"{df['iqu_mediano'].median():.2f}")
    with c2: st.metric("Total Equipamentos", f"{int(df['total_equipamentos'].sum()):,}")
    with c3: st.metric("Bairros", f"{len(df)}")

    st.markdown("")
    for i in range(0, len(df), 3):
        row = df.iloc[i:i+3]
        cols_card = st.columns(3)
        for j, (_, r) in enumerate(row.iterrows()):
            cor = CORES_CLASSE.get(r["classe"], "#555")
            pct = min(r["iqu_mediano"]/10*100, 100)
            with cols_card[j]:
                st.markdown(f"""
                <div style="background:#1e1e2e;border-left:4px solid {cor};
                            border-radius:8px;padding:16px;margin-bottom:12px;">
                    <div style="font-size:0.95rem;font-weight:700;color:#fff;
                                white-space:nowrap;overflow:hidden;text-overflow:ellipsis"
                         title="{r['NM_BAIRRO']}">{r['NM_BAIRRO']}</div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                        <span style="font-size:1.6rem;font-weight:800;color:{cor}">{r['iqu_mediano']:.2f}</span>
                        <span style="font-size:0.7rem;color:{cor};padding:3px 8px;
                                     background:{cor}22;border-radius:12px">{r['classe']}</span>
                    </div>
                    <div style="background:#2a2a3e;border-radius:4px;height:4px;margin-bottom:10px">
                        <div style="background:{cor};width:{pct:.0f}%;height:4px;border-radius:4px"></div>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;font-size:0.7rem">
                        <div style="background:#12192a;border-radius:5px;padding:5px;text-align:center">
                            <div style="color:#ef5350;font-weight:700">{int(r['saude'])}</div>
                            <div style="color:#555">saude</div>
                        </div>
                        <div style="background:#12192a;border-radius:5px;padding:5px;text-align:center">
                            <div style="color:#FFA726;font-weight:700">{int(r['educacao'])}</div>
                            <div style="color:#555">educ.</div>
                        </div>
                        <div style="background:#12192a;border-radius:5px;padding:5px;text-align:center">
                            <div style="color:#42A5F5;font-weight:700">{int(r['mobilidade'])}</div>
                            <div style="color:#555">mob.</div>
                        </div>
                        <div style="background:#12192a;border-radius:5px;padding:5px;text-align:center">
                            <div style="color:#66BB6A;font-weight:700">{int(r['qualidade_vida'])}</div>
                            <div style="color:#555">vida</div>
                        </div>
                        <div style="background:#12192a;border-radius:5px;padding:5px;text-align:center">
                            <div style="color:#AB47BC;font-weight:700">{int(r['servicos_essenciais'])}</div>
                            <div style="color:#555">serv.</div>
                        </div>
                        <div style="background:#12192a;border-radius:5px;padding:5px;text-align:center">
                            <div style="color:#FF7043;font-weight:700">{int(r['seguranca'])}</div>
                            <div style="color:#555">seg.</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
