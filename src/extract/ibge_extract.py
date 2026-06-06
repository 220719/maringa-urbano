"""
Download do shapefile de setores censitários de Maringá (IBGE Censo 2022)
e boundary do município via API IBGE.
"""

import requests
import geopandas as gpd
import zipfile
import io
from pathlib import Path

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

COD_MUNICIPIO = "4115200"  # Maringá-PR

# URL correta — confirmada no FTP do IBGE
URL_SETORES_PR = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/"
    "malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/"
    "censo_2022/setores/shp/UF/PR_setores_CD2022.zip"
)


def download_boundary():
    print("Baixando boundary de Maringá...")
    url = f"https://servicodados.ibge.gov.br/api/v3/malhas/municipios/{COD_MUNICIPIO}?formato=application/json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    gdf = gpd.read_file(io.BytesIO(resp.content))
    gdf["municipio"] = "Maringá"
    gdf["cod_ibge"] = COD_MUNICIPIO
    gdf.crs = "EPSG:4326"
    path = RAW_DIR / "maringa_boundary.geojson"
    gdf.to_file(path, driver="GeoJSON")
    print(f"  ✓ Boundary salvo: {path}")
    print(f"  Área: {gdf.to_crs('EPSG:32722').area.sum() / 1e6:.1f} km²")
    return gdf


def download_setores():
    print("\nBaixando setores censitários PR (25MB)...")
    zip_path = RAW_DIR / "PR_setores_CD2022.zip"

    # Baixa o zip
    with requests.get(URL_SETORES_PR, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        total = 0
        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)
                total += len(chunk)
        print(f"  ✓ Download: {total / 1e6:.1f} MB")

    # Extrai
    extract_dir = RAW_DIR / "PR_setores_CD2022"
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)
    print(f"  ✓ Extraído em {extract_dir}")

    # Lê shapefile
    shp_files = list(extract_dir.glob("**/*.shp"))
    print(f"  Shapefile: {shp_files[0].name}")
    gdf_pr = gpd.read_file(shp_files[0])
    print(f"  Total setores PR: {len(gdf_pr)}")
    print(f"  Colunas: {list(gdf_pr.columns)}")

    # Filtra Maringá
    col_mun = next(
        (c for c in gdf_pr.columns if c.upper() in ["CD_MUN", "CD_MUNICIP", "CODMUN"]),
        None
    )
    if col_mun:
        gdf_maringa = gdf_pr[gdf_pr[col_mun].astype(str) == COD_MUNICIPIO].copy()
    else:
        print("  Coluna CD_MUN não encontrada — usando filtro espacial...")
        boundary = gpd.read_file(RAW_DIR / "maringa_boundary.geojson")
        gdf_pr = gdf_pr.to_crs("EPSG:4326")
        gdf_maringa = gpd.sjoin(gdf_pr, boundary[["geometry"]], how="inner", predicate="intersects")

    gdf_maringa = gdf_maringa.to_crs("EPSG:4326")
    path = RAW_DIR / "maringa_setores.geojson"
    gdf_maringa.to_file(path, driver="GeoJSON")
    print(f"  ✓ Setores Maringá: {len(gdf_maringa)} setores → {path}")
    return gdf_maringa


if __name__ == "__main__":
    download_boundary()
    download_setores()
    print("\n=== IBGE Extract concluído ===")
