import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

PROCESSED = Path(__file__).parent.parent.parent / "data" / "processed"

FEATURES    = ["saude","educacao","mobilidade","qualidade_vida","servicos_essenciais","seguranca","iqu_ponderado"]
LABELS_PT   = ["Saúde","Educação","Mobilidade","Qual. Vida","Serviços","Segurança","IQU"]

PERFIS = {
    1: ("🏙️ Zona Consolidada",       "#42A5F5",
        "Melhor cobertura geral. Centro, área universitária e zonas nobres. IQU ponderado acima de 3.4."),
    2: ("🌱 Zona em Desenvolvimento", "#FFA726",
        "Cobertura intermediária. Boa mobilidade mas ainda carente em saúde e serviços essenciais."),
    0: ("🚧 Zona de Expansão",        "#ef5350",
        "Zonas periféricas e de expansão urbana. Alta mobilidade mas baixa cobertura geral. Prioridade de investimento."),
}

@st.cache_data
def load_data():
    df    = pd.read_csv(PROCESSED / "zonas_clusters.csv")
    perfil = pd.read_csv(PROCESSED / "perfil_clusters_zonas.csv", index_col=0)
    df["perfil_nome"] = df["cluster"].map({k: v[0] for k,v in PERFIS.items()})
    df["perfil_cor"]  = df["cluster"].map({k: v[1] for k,v in PERFIS.items()})
    return df, perfil

def render():
    df, perfil = load_data()

    st.markdown("## 🤖 ML — Perfil Urbano por Zona")
    st.markdown("K-Means aplicado às **47 zonas** de Maringá usando 7 variáveis urbanas.")
    st.markdown("---")

    with st.expander("📖 Entenda as 7 variáveis usadas pelo modelo", expanded=False):
        st.markdown("""
O modelo analisa cada zona com base em **7 variáveis**:

| # | Variável | O que conta | Por que importa |
|---|---|---|---|
| 1 | 🏥 **Saúde** | Hospitais, clínicas, postos | Acesso a atendimento médico |
| 2 | 🎓 **Educação** | Escolas, creches, universidades | Acesso ao ensino |
| 3 | 🚌 **Mobilidade** | Pontos de ônibus, terminais | Deslocamento sem carro |
| 4 | 🌳 **Qualidade de Vida** | Parques, praças, academias | Lazer e bem-estar |
| 5 | 🛒 **Serviços Essenciais** | Mercados, farmácias, bancos | Consumo básico |
| 6 | 🚨 **Segurança** | Delegacias, bombeiros | Presença do Estado |
| 7 | 📊 **IQU Mediano** | Índice de Qualidade Urbana | Resumo ponderado |

> O número ideal de grupos **(3)** foi escolhido pelo **Silhouette Score** (0.315).
        """)

    st.markdown("---")
    st.markdown("#### Grupos identificados pelo modelo")

    c1, c2, c3 = st.columns(3)
    for col, (cid, (nome, cor, desc)) in zip([c1,c2,c3], PERFIS.items()):
        n     = int((df["cluster"] == cid).sum())
        zonas = ", ".join(sorted(df[df["cluster"]==cid]["NM_SUBDIST"].tolist()))
        with col:
            st.markdown(f"""
            <div style="background:#1e1e2e;border-left:5px solid {cor};
                        border-radius:8px;padding:16px;margin-bottom:8px;min-height:200px">
                <div style="font-size:1rem;font-weight:700;color:{cor}">{nome}</div>
                <div style="font-size:2.5rem;font-weight:900;color:#fff;margin:6px 0">{n}</div>
                <div style="font-size:0.75rem;color:#aaa">zonas</div>
                <hr style="border-color:#333;margin:10px 0">
                <div style="font-size:0.75rem;color:#888;margin-bottom:8px">{desc}</div>
                <div style="font-size:0.7rem;color:#555;line-height:1.6">{zonas}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # PCA scatter
    st.markdown("#### Dispersão das Zonas no Espaço de Features (PCA 2D)")
    st.caption("Cada ponto é uma zona. Zonas próximas têm perfil urbano parecido. Passe o mouse para ver detalhes.")

    fig = px.scatter(
        df, x="pca_x", y="pca_y",
        color="perfil_nome",
        color_discrete_map={v[0]: v[1] for v in PERFIS.values()},
        hover_name="NM_SUBDIST",
        hover_data={"iqu_ponderado":":.2f","pca_x":False,"pca_y":False,
                    "perfil_nome":False,"perfil_cor":False,
                    "saude":True,"educacao":True,"mobilidade":True},
        template="plotly_dark",
        text="NM_SUBDIST",
        labels={
            "pca_x":"← menos equipamentos    |    mais equipamentos →",
            "pca_y":"← mobilidade baixa    |    mobilidade alta →",
            "perfil_nome":"Perfil",
        },
    )
    fig.update_traces(
        marker=dict(size=14, opacity=0.9),
        textposition="top center",
        textfont=dict(size=10, color="#ccc"),
    )
    fig.update_layout(
        plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
        height=540,
        legend=dict(orientation="h", y=-0.15, font=dict(size=13, color="#fff"),
                    bgcolor="#1e1e2e", bordercolor="#333", borderwidth=1),
        xaxis=dict(title_font=dict(size=12,color="#aaa"), tickfont=dict(color="#666"),
                   gridcolor="#2a2a3e", zeroline=True, zerolinecolor="#444"),
        yaxis=dict(title_font=dict(size=12,color="#aaa"), tickfont=dict(color="#666"),
                   gridcolor="#2a2a3e", zeroline=True, zerolinecolor="#444"),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Radar — 3 gráficos lado a lado
    st.markdown("#### Perfil Médio de Cada Grupo — Radar")
    st.caption("Quanto maior a área, mais bem servido é o grupo naquela dimensão.")

    col_r1, col_r2, col_r3 = st.columns(3)
    for col, (cid, (nome, cor, _)) in zip([col_r1,col_r2,col_r3], PERFIS.items()):
        vals      = [perfil.loc[cid, f] for f in FEATURES]
        max_vals  = [max(perfil[f].max(), 0.001) for f in FEATURES]
        vals_norm = [v/m for v,m in zip(vals, max_vals)]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=vals_norm + [vals_norm[0]],
            theta=LABELS_PT + [LABELS_PT[0]],
            fill="toself", name=nome,
            line_color=cor,
            fillcolor=f"rgba({int(cor[1:3],16)},{int(cor[3:5],16)},{int(cor[5:7],16)},0.3)",
            mode="lines+markers",
            marker=dict(size=6, color=cor),
        ))
        fig_r.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0,1],
                               tickfont=dict(size=10,color="#ccc"), gridcolor="#333"),
                angularaxis=dict(tickfont=dict(size=12,color="#fff"), gridcolor="#333"),
                bgcolor="#1e1e2e",
            ),
            paper_bgcolor="#1e1e2e", height=300,
            margin=dict(t=50,b=30,l=30,r=30),
            showlegend=False,
            title=dict(text=nome, font=dict(size=12,color=cor), x=0.5),
        )
        with col:
            st.plotly_chart(fig_r, use_container_width=True)

    st.markdown("---")

    # Explorador por grupo
    st.markdown("#### Explorar Zonas por Grupo")
    grupo_sel = st.selectbox("Selecione o perfil:", [v[0] for v in PERFIS.values()])
    df_sel    = df[df["perfil_nome"]==grupo_sel].sort_values("iqu_ponderado", ascending=False)
    cor_sel   = df_sel["perfil_cor"].iloc[0]

    c1,c2,c3 = st.columns(3)
    with c1: st.metric("Zonas neste grupo", len(df_sel))
    with c2: st.metric("IQU Mediano do grupo", f"{df_sel['iqu_mediano'].median():.2f}")
    with c3: st.metric("Total Equipamentos", f"{int(df_sel['total_equipamentos'].sum()):,}")

    st.markdown("")
    for i in range(0, len(df_sel), 3):
        row  = df_sel.iloc[i:i+3]
        cols = st.columns(3)
        for j, (_, r) in enumerate(row.iterrows()):
            pct = min(r["iqu_ponderado"]/10*100, 100)
            with cols[j]:
                st.markdown(f"""
                <div style="background:#1e1e2e;border-left:4px solid {cor_sel};
                            border-radius:8px;padding:14px;margin-bottom:10px">
                    <div style="font-size:1.1rem;font-weight:800;color:{cor_sel}">{r['NM_SUBDIST']}</div>
                    <div style="font-size:1.6rem;font-weight:900;color:#fff;margin:4px 0">
                        IQU {r['iqu_mediano']:.2f}
                    </div>
                    <div style="background:#2a2a3e;border-radius:4px;height:4px;margin-bottom:10px">
                        <div style="background:{cor_sel};width:{pct:.0f}%;height:4px;border-radius:4px"></div>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;font-size:0.72rem">
                        <div style="background:#12192a;border-radius:5px;padding:6px;text-align:center">
                            <div style="color:#ef5350;font-weight:700">{int(r['saude'])}</div>
                            <div style="color:#555">saúde</div>
                        </div>
                        <div style="background:#12192a;border-radius:5px;padding:6px;text-align:center">
                            <div style="color:#FFA726;font-weight:700">{int(r['educacao'])}</div>
                            <div style="color:#555">educ.</div>
                        </div>
                        <div style="background:#12192a;border-radius:5px;padding:6px;text-align:center">
                            <div style="color:#42A5F5;font-weight:700">{int(r['mobilidade'])}</div>
                            <div style="color:#555">mob.</div>
                        </div>
                        <div style="background:#12192a;border-radius:5px;padding:6px;text-align:center">
                            <div style="color:#66BB6A;font-weight:700">{int(r['qualidade_vida'])}</div>
                            <div style="color:#555">vida</div>
                        </div>
                        <div style="background:#12192a;border-radius:5px;padding:6px;text-align:center">
                            <div style="color:#AB47BC;font-weight:700">{int(r['servicos_essenciais'])}</div>
                            <div style="color:#555">serv.</div>
                        </div>
                        <div style="background:#12192a;border-radius:5px;padding:6px;text-align:center">
                            <div style="color:#FF7043;font-weight:700">{int(r['seguranca'])}</div>
                            <div style="color:#555">seg.</div>
                        </div>
                    </div>
                    <div style="margin-top:8px;font-size:0.7rem;color:#555;text-align:right">
                        {int(r['setores'])} setores · {int(r['total_equipamentos'])} equip.
                    </div>
                </div>""", unsafe_allow_html=True)
