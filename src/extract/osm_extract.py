"""
Extração de equipamentos urbanos de Maringá via Overpass API.
Salva cada categoria como GeoJSON em data/raw/
"""

import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path
import time

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

HEADERS = {
    "User-Agent": "MaringaUrbano/1.0 (research project; urbanismo)",
    "Accept": "application/json",
}

CATEGORIAS = {
    "saude": [
        '["amenity"="hospital"]',
        '["amenity"="clinic"]',
        '["amenity"="health_post"]',
    ],
    "educacao": [
        '["amenity"="school"]',
        '["amenity"="university"]',
        '["amenity"="kindergarten"]',
        '["amenity"="college"]',
    ],
    "mobilidade": [
        '["highway"="bus_stop"]',
        '["amenity"="bus_station"]',
        '["amenity"="bicycle_parking"]',
    ],
    "qualidade_vida": [
        '["leisure"="park"]',
        '["leisure"="playground"]',
        '["leisure"="sports_centre"]',
        '["leisure"="fitness_centre"]',
    ],
    "servicos_essenciais": [
        '["amenity"="supermarket"]',
        '["shop"="supermarket"]',
        '["amenity"="marketplace"]',
        '["amenity"="bank"]',
        '["amenity"="pharmacy"]',
    ],
    "seguranca": [
        '["amenity"="police"]',
        '["amenity"="fire_station"]',
    ],
}


def build_query(filtros: list[str]) -> str:
    area_def = 'area["name"="Maringá"]["admin_level"="8"]->.maringa;'
    nodes = "\n".join(f'  node{f}(area.maringa);' for f in filtros)
    ways = "\n".join(f'  way{f}(area.maringa);' for f in filtros)
    return f"""
[out:json][timeout:60];
{area_def}
(
{nodes}
{ways}
);
out center;
"""


def fetch_categoria(nome: str, filtros: list[str]) -> gpd.GeoDataFrame:
    query = build_query(filtros)
    print(f"  Buscando: {nome}...")

    resp = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers=HEADERS,
        timeout=60
    )
    resp.raise_for_status()
    elementos = resp.json().get("elements", [])

    registros = []
    for el in elementos:
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        if lat and lon:
            tags = el.get("tags", {})
            registros.append({
                "osm_id": el["id"],
                "tipo": el["type"],
                "categoria": nome,
                "nome": tags.get("name", "Sem nome"),
                "amenity": tags.get("amenity", ""),
                "leisure": tags.get("leisure", ""),
                "shop": tags.get("shop", ""),
                "highway": tags.get("highway", ""),
                "geometry": Point(lon, lat),
            })

    gdf = gpd.GeoDataFrame(registros, crs="EPSG:4326")
    print(f"  ✓ {len(gdf)} equipamentos encontrados")
    return gdf


def main():
    print("=== Extração OSM — Maringá Urbano ===\n")
    gdfs = []

    for nome, filtros in CATEGORIAS.items():
        try:
            gdf = fetch_categoria(nome, filtros)
            if not gdf.empty:
                path = RAW_DIR / f"osm_{nome}.geojson"
                gdf.to_file(path, driver="GeoJSON")
                print(f"  Salvo em {path}\n")
                gdfs.append(gdf)
            time.sleep(2)
        except Exception as e:
            print(f"  ERRO em {nome}: {e}\n")

    if gdfs:
        gdf_all = pd.concat(gdfs, ignore_index=True)
        gdf_all = gpd.GeoDataFrame(gdf_all, crs="EPSG:4326")
        path_all = RAW_DIR / "osm_todos.geojson"
        gdf_all.to_file(path_all, driver="GeoJSON")
        print(f"\n=== Total: {len(gdf_all)} equipamentos ===")
        print(gdf_all.groupby("categoria")["osm_id"].count())
        print(f"\nArquivo consolidado: {path_all}")


if __name__ == "__main__":
    main()
