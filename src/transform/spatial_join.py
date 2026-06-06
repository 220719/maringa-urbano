"""
Spatial join: equipamentos OSM × setores censitários IBGE.
Usa normalização por percentil (rank) para evitar distorção por outliers.
"""

import geopandas as gpd
import pandas as pd
import duckdb
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIAS = [
    "saude", "educacao", "mobilidade",
    "qualidade_vida", "servicos_essenciais", "seguranca"
]

PESOS = {
    "saude":               0.25,
    "educacao":            0.20,
    "mobilidade":          0.15,
    "qualidade_vida":      0.15,
    "servicos_essenciais": 0.15,
    "seguranca":           0.10,
}


def load_data():
    print("Carregando dados...")
    setores = gpd.read_file(RAW_DIR / "maringa_setores.geojson").to_crs("EPSG:4326")
    osm = gpd.read_file(RAW_DIR / "osm_todos.geojson").to_crs("EPSG:4326")
    print(f"  ✓ Setores: {len(setores)} | Equipamentos: {len(osm)}")
    return setores, osm


def spatial_join(setores, osm):
    print("\nRealizando spatial join...")
    joined = gpd.sjoin(
        osm, setores[["CD_SETOR", "NM_BAIRRO", "AREA_KM2", "geometry"]],
        how="left", predicate="within"
    ).dropna(subset=["CD_SETOR"])
    print(f"  ✓ {len(joined)} equipamentos dentro dos setores")
    return joined


def calcular_contagens(setores, joined):
    print("\nCalculando contagens por setor...")
    contagens = (
        joined.groupby(["CD_SETOR", "categoria"])
        .size()
        .reset_index(name="count")
        .pivot(index="CD_SETOR", columns="categoria", values="count")
        .fillna(0).astype(int).reset_index()
    )
    for cat in CATEGORIAS:
        if cat not in contagens.columns:
            contagens[cat] = 0

    gdf = setores.merge(contagens, on="CD_SETOR", how="left")
    for cat in CATEGORIAS:
        gdf[cat] = gdf[cat].fillna(0).astype(int)

    gdf["total_equipamentos"] = gdf[CATEGORIAS].sum(axis=1)
    return gdf


def calcular_iqu(gdf):
    print("\nCalculando IQU com normalização por percentil rank...")

    # Rank percentil: evita distorção por outliers (ex: 2375 pontos de ônibus)
    for cat in CATEGORIAS:
        col_norm = f"{cat}_norm"
        # rank percentil entre 0 e 1; setores sem nada ficam em 0
        ranked = gdf[cat].rank(method="average", pct=True)
        # setores com 0 equipamentos recebem score 0 explicitamente
        gdf[col_norm] = ranked.where(gdf[cat] > 0, 0.0)

    gdf["iqu"] = (
        sum(gdf[f"{cat}_norm"] * peso for cat, peso in PESOS.items()) * 10
    ).round(2)

    gdf["iqu_classe"] = pd.cut(
        gdf["iqu"],
        bins=[-0.01, 2, 4, 6, 8, 10],
        labels=["Muito Baixo", "Baixo", "Moderado", "Alto", "Muito Alto"]
    )

    print(f"\n  Distribuição IQU:")
    print(gdf["iqu_classe"].value_counts().sort_index())
    print(f"\n  IQU médio: {gdf['iqu'].mean():.2f}")
    print(f"  IQU máx:   {gdf['iqu'].max():.2f}")
    print(f"  IQU mín:   {gdf['iqu'].min():.2f}")
    return gdf


def salvar(gdf):
    cols_norm = [c for c in gdf.columns if c.endswith("_norm")]
    gdf_save = gdf.drop(columns=cols_norm)

    gdf_save.to_file(PROCESSED_DIR / "maringa_iqu.geojson", driver="GeoJSON")
    print(f"\n  ✓ GeoJSON: {PROCESSED_DIR / 'maringa_iqu.geojson'}")

    df = gdf_save.drop(columns=["geometry"])
    con = duckdb.connect(str(PROCESSED_DIR / "maringa_urbano.duckdb"))
    con.execute("DROP TABLE IF EXISTS setores_iqu")
    con.execute("CREATE TABLE setores_iqu AS SELECT * FROM df")
    con.close()
    print(f"  ✓ DuckDB: {PROCESSED_DIR / 'maringa_urbano.duckdb'}")

    resumo = (
        df.groupby("NM_BAIRRO")
        .agg(
            setores=("CD_SETOR", "count"),
            iqu_medio=("iqu", "mean"),
            total_equipamentos=("total_equipamentos", "sum"),
        )
        .round(2)
        .sort_values("iqu_medio", ascending=False)
        .reset_index()
    )
    resumo.to_csv(PROCESSED_DIR / "resumo_bairros.csv", index=False)
    print(f"\n  Top 10 bairros por IQU:")
    print(resumo.head(10).to_string(index=False))
    print(f"\n  Bottom 5 bairros por IQU:")
    print(resumo.tail(5).to_string(index=False))


if __name__ == "__main__":
    setores, osm = load_data()
    joined = spatial_join(setores, osm)
    gdf = calcular_contagens(setores, joined)
    gdf = calcular_iqu(gdf)
    salvar(gdf)
    print("\n=== Spatial Join concluído ===")
