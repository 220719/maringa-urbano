import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

PROCESSED = Path(__file__).parent.parent.parent / "data" / "processed"

FEATURES  = ["saude","educacao","mobilidade","qualidade_vida","servicos_essenciais","seguranca"]
LABELS_PT = ["Saúde","Educação","Mobilidade","Qual. Vida","Serviços","Segurança"]
CORES_CAT = ["#ef5350","#FFA726","#42A5F5","#66BB6A","#AB47BC","#FF7043"]

PERFIS = {
    1: ("🏙️ Zona Consolidada",        "#42A5F5"),
    2: ("🌱 Zona em Desenvolvimento",  "#FFA726"),
    0: ("🚧 Zona de Expansão",         "#ef5350"),
}

CORES_IQU = {
    "Muito Baixo": "#ef5350",
    "Baixo":       "#FFA726",
    "Moderado":    "#FFEE58",
    "Alto":        "#66BB6A",
    "Muito Alto":  "#42A5F5",
}

@st.cache_data
def load_data():
    df = pd.read_csv(PROCESSED / "zonas_clusters.csv")
    df["perfil_nome"] = df["cluster"].map({k: v[0] for k,v in PERFIS.items()})
    df["perfil_cor"]  = df["cluster"].map({k: v[1] for k,v in PERFIS.items()})
    df["iqu_classe"]  = df["iqu_mediano"].apply(lambda v:
        "Muito Alto" if v>=8 else "Alto" if v>=6 else
        "Moderado" if v>=4 else "Baixo" if v>=2 else "Muito Baixo")
    return df

DESCRICOES_ZONA = {
    "Zona 1":       "🏙️ Centro e Novo Centro — Coração da cidade, alta densidade de prédios modernos e centros de compras.",
    "Zona 2":       "🌳 Vizinha da Catedral e do Parque do Ingá — Predominantemente residencial, uma das mais valorizadas.",
    "Zona 3":       "⚒️ Vila Operária — Um dos bairros mais antigos, com forte comércio local e história pioneira.",
    "Zona 4":       "🏥 Área nobre — Forte presença de clínicas, hospitais e residências de classe média-alta.",
    "Zona 5":       "🎭 Maringá Velho — Bairro histórico de alto padrão, sede do Teatro Calil Haddad e Horto Florestal.",
    "Zona 7":       "🎓 Região Universitária — Ao redor da UEM, a mais populosa, com vida noturna agitada.",
    "Zona 23":      "🛣️ Vila Morangueira — Bairro tradicional que liga o centro a importantes avenidas comerciais.",
    "Zona Central": "🏛️ Zona Central histórica — Núcleo original do planejamento urbano de Maringá.",
}

def render():
    df = load_data()
    mediana_cidade = {f: df[f].median() for f in FEATURES}

    st.markdown("## 📊 Análise por Zona")
    st.caption("Explore o perfil urbano de cada zona, compare com a média da cidade e confronte duas zonas.")
    st.markdown("---")

    # SEÇÃO 1 — Ficha da zona
    st.markdown("### 1️⃣ Ficha da Zona")

    # Ordena numericamente
    def sort_zona(z):
        z = z.replace("Zona ","").replace("Central","999")
        try: return int(z)
        except: return 999

    zonas_sorted = sorted(df["NM_SUBDIST"].tolist(), key=sort_zona)
    zona_sel = st.selectbox("Selecione uma zona:", zonas_sorted)

    b        = df[df["NM_SUBDIST"]==zona_sel].iloc[0]
    cor_iqu  = CORES_IQU.get(b["iqu_classe"], "#888")
    cor_perf = b["perfil_cor"]
    pct      = min(b["iqu_mediano"]/10*100, 100)
    rank     = int(df["iqu_mediano"].rank(ascending=False)[df["NM_SUBDIST"]==zona_sel].values[0])

    desc = DESCRICOES_ZONA.get(zona_sel, "")
    desc_html = f'''<div style="margin-top:10px;font-size:0.85rem;color:#93c5fd;
                              background:#1e3a5f;padding:8px 12px;border-radius:6px">
                        {desc}</div>''' if desc else ""

    st.markdown(f"""
    <div style="background:#1e1e2e;border-radius:12px;padding:20px 24px;
                border-left:6px solid {cor_iqu};margin-bottom:16px">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">
            <div style="flex:1">
                <div style="font-size:2rem;font-weight:900;color:#fff">{zona_sel}</div>
                <div style="font-size:0.85rem;color:#8b949e;margin-top:4px">
                    {int(b['setores'])} setores censitários · {int(b['total_equipamentos'])} equipamentos
                </div>
                {desc_html}
                <div style="margin-top:10px">
                    <span style="background:{cor_perf}22;color:{cor_perf};
                                 padding:4px 12px;border-radius:20px;font-size:0.8rem;
                                 border:1px solid {cor_perf}44">{b['perfil_nome']}</span>
                    <span style="background:{cor_iqu}22;color:{cor_iqu};
                                 padding:4px 12px;border-radius:20px;font-size:0.8rem;
                                 border:1px solid {cor_iqu}44;margin-left:8px">IQU {b['iqu_classe']}</span>
                </div>
            </div>
            <div style="text-align:right">
                <div style="font-size:3.5rem;font-weight:900;color:{cor_iqu};line-height:1">{b['iqu_mediano']:.2f}</div>
                <div style="font-size:0.8rem;color:#8b949e">IQU / 10</div>
                <div style="font-size:0.8rem;color:#8b949e;margin-top:4px">#{rank} de {len(df)} zonas</div>
            </div>
        </div>
        <div style="margin-top:14px;background:#2a2a3e;border-radius:6px;height:6px">
            <div style="background:{cor_iqu};width:{pct:.0f}%;height:6px;border-radius:6px"></div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Mini cards
    cols = st.columns(6)
    for col, feat, label, cor in zip(cols, FEATURES, LABELS_PT, CORES_CAT):
        val   = int(b[feat])
        med   = mediana_cidade[feat]
        ic    = "↑" if val > med else ("=" if val == med else "↓")
        dcor  = "#66BB6A" if val > med else ("#aaa" if val == med else "#ef5350")
        with col:
            st.markdown(f"""
            <div style="background:#1e1e2e;border-top:3px solid {cor};
                        border-radius:8px;padding:12px 8px;text-align:center">
                <div style="font-size:1.6rem;font-weight:800;color:{cor}">{val}</div>
                <div style="font-size:0.7rem;color:#8b949e;margin:2px 0">{label}</div>
                <div style="font-size:0.65rem;color:{dcor}">{ic} vs mediana</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # SEÇÃO 2 — Radar
    st.markdown("### 2️⃣ Perfil da Zona vs Maringá")
    st.caption("Área colorida = zona selecionada · Área cinza = mediana de Maringá")

    max_vals   = [max(df[f].max(), 0.001) for f in FEATURES]
    vals_b     = [b[f] for f in FEATURES]
    vals_med   = [mediana_cidade[f] for f in FEATURES]
    vals_b_n   = [v/m for v,m in zip(vals_b,   max_vals)]
    vals_med_n = [v/m for v,m in zip(vals_med, max_vals)]

    fig_r = go.Figure()
    fig_r.add_trace(go.Scatterpolar(
        r=vals_med_n+[vals_med_n[0]], theta=LABELS_PT+[LABELS_PT[0]],
        fill="toself", name="Mediana Maringá",
        line_color="#555", fillcolor="rgba(85,85,85,0.2)", mode="lines",
    ))
    fig_r.add_trace(go.Scatterpolar(
        r=vals_b_n+[vals_b_n[0]], theta=LABELS_PT+[LABELS_PT[0]],
        fill="toself", name=zona_sel,
        line_color=cor_iqu,
        fillcolor=f"rgba({int(cor_iqu[1:3],16)},{int(cor_iqu[3:5],16)},{int(cor_iqu[5:7],16)},0.35)",
        mode="lines+markers", marker=dict(size=7, color=cor_iqu),
    ))
    fig_r.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,1],
                           tickfont=dict(size=10,color="#aaa"), gridcolor="#333"),
            angularaxis=dict(tickfont=dict(size=13,color="#fff"), gridcolor="#333"),
            bgcolor="#1e1e2e",
        ),
        paper_bgcolor="#1e1e2e", template="plotly_dark",
        height=420, legend=dict(orientation="h", y=-0.1, font=dict(color="#fff",size=12)),
    )
    st.plotly_chart(fig_r, use_container_width=True)

    st.markdown("---")

    # SEÇÃO 3 — Ranking
    st.markdown("### 3️⃣ Posição no Ranking Geral")
    st.caption(f"**{zona_sel}** está na posição **#{rank}** entre as {len(df)} zonas de Maringá.")

    df_rank = df.sort_values("iqu_mediano", ascending=False).reset_index(drop=True)
    idx     = df_rank[df_rank["NM_SUBDIST"]==zona_sel].index[0]
    vizinhos = df_rank.iloc[max(0,idx-4):min(len(df_rank),idx+5)].copy()

    cores_bar = [cor_iqu if r["NM_SUBDIST"]==zona_sel else "#2a2a3e"
                 for _, r in vizinhos.iterrows()]

    fig_rank = go.Figure(go.Bar(
        x=vizinhos["iqu_mediano"],
        y=vizinhos["NM_SUBDIST"],
        orientation="h",
        marker_color=cores_bar,
        text=vizinhos["iqu_mediano"].apply(lambda x: f"{x:.2f}"),
        textposition="outside",
    ))
    fig_rank.add_vline(
        x=df["iqu_mediano"].median(),
        line_dash="dash", line_color="#666",
        annotation_text="mediana Maringá",
        annotation_font_color="#888",
    )
    fig_rank.update_layout(
        template="plotly_dark", plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
        height=360, showlegend=False,
        xaxis=dict(range=[0, df["iqu_mediano"].max()*1.2], title="IQU"),
        yaxis=dict(title=""),
        margin=dict(l=140, r=80, t=10, b=10),
    )
    st.plotly_chart(fig_rank, use_container_width=True)

    st.markdown("---")

    # SEÇÃO 4 — Comparador
    st.markdown("### 4️⃣ Comparar com Outra Zona")
    outras   = [z for z in zonas_sorted if z != zona_sel]
    zona_b   = st.selectbox("Comparar com:", outras, index=0)
    b2       = df[df["NM_SUBDIST"]==zona_b].iloc[0]
    cor_iqu2 = CORES_IQU.get(b2["iqu_classe"], "#888")

    col1, col2 = st.columns(2)
    for col, bdata, bcor, btitle in [(col1,b,cor_iqu,zona_sel),(col2,b2,cor_iqu2,zona_b)]:
        pct2 = min(bdata["iqu_mediano"]/10*100, 100)
        with col:
            st.markdown(f"""
            <div style="background:#1e1e2e;border-left:5px solid {bcor};
                        border-radius:10px;padding:16px;margin-bottom:12px">
                <div style="font-size:1.2rem;font-weight:800;color:#fff">{btitle}</div>
                <div style="font-size:2.2rem;font-weight:900;color:{bcor};margin:6px 0">
                    IQU {bdata['iqu_mediano']:.2f}
                </div>
                <div style="background:#2a2a3e;border-radius:4px;height:5px;margin-bottom:10px">
                    <div style="background:{bcor};width:{pct2:.0f}%;height:5px;border-radius:4px"></div>
                </div>
                <div style="font-size:0.8rem;color:#8b949e">{bdata['perfil_nome']}</div>
                <div style="font-size:0.75rem;color:#555;margin-top:4px">
                    {int(bdata['setores'])} setores · {int(bdata['total_equipamentos'])} equipamentos
                </div>
            </div>""", unsafe_allow_html=True)

    # Gráfico comparativo
    comp = pd.DataFrame([
        {"Categoria": label, zona_sel: int(b[f]), zona_b: int(b2[f])}
        for f, label in zip(FEATURES, LABELS_PT)
    ])
    fig_c = go.Figure()
    fig_c.add_trace(go.Bar(
        name=zona_sel, x=comp["Categoria"], y=comp[zona_sel],
        marker_color=cor_iqu, text=comp[zona_sel], textposition="outside",
    ))
    fig_c.add_trace(go.Bar(
        name=zona_b, x=comp["Categoria"], y=comp[zona_b],
        marker_color=cor_iqu2, text=comp[zona_b], textposition="outside",
    ))
    fig_c.update_layout(
        barmode="group", template="plotly_dark",
        plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
        height=380,
        legend=dict(orientation="h", y=-0.15, font=dict(color="#fff",size=12)),
        yaxis_title="Equipamentos",
        margin=dict(t=20, b=40),
    )
    st.plotly_chart(fig_c, use_container_width=True)

    # Tabela resumo
    st.markdown("#### Resumo comparativo")
    resumo = pd.DataFrame({
        "Indicador": LABELS_PT + ["IQU Mediano","Cluster","Setores"],
        zona_sel:    [int(b[f]) for f in FEATURES] + [f"{b['iqu_mediano']:.2f}", b['perfil_nome'], int(b['setores'])],
        zona_b:      [int(b2[f]) for f in FEATURES] + [f"{b2['iqu_mediano']:.2f}", b2['perfil_nome'], int(b2['setores'])],
    })
    st.dataframe(resumo, use_container_width=True, hide_index=True)
