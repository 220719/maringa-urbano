"""
K-Means clustering de bairros por perfil urbano.
Input:  data/processed/resumo_bairros_completo.csv
Output: data/processed/bairros_clusters.csv
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from pathlib import Path

PROCESSED = Path("data/processed")

FEATURES = ["saude","educacao","mobilidade","qualidade_vida",
            "servicos_essenciais","seguranca","iqu_mediano"]

PERFIS = {
    0: ("🏙️ Centro Dinâmico",    "#42A5F5"),
    1: ("🌿 Bairro Residencial",  "#66BB6A"),
    2: ("🚧 Periferia Carente",   "#ef5350"),
    3: ("🚌 Corredor de Mobilidade", "#FFA726"),
}

def main():
    df = pd.read_csv(PROCESSED / "resumo_bairros_completo.csv")
    print(f"Bairros: {len(df)}")

    X = df[FEATURES].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Escolha do K via silhouette
    print("\nSilhouette scores:")
    scores = {}
    for k in range(2, 8):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        scores[k] = score
        print(f"  k={k}: {score:.3f}")

    best_k = max(scores, key=scores.get)
    print(f"\nMelhor k: {best_k} (silhouette={scores[best_k]:.3f})")

    # Treina com melhor k
    km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df["cluster"] = km.fit_predict(X_scaled)

    # PCA para visualização 2D
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_scaled)
    df["pca_x"] = coords[:, 0]
    df["pca_y"] = coords[:, 1]

    # Perfil de cada cluster
    print("\nPerfil dos clusters:")
    perfil = df.groupby("cluster")[FEATURES].mean().round(2)
    print(perfil)

    # Nomeia clusters pelo iqu_mediano (maior = mais dinâmico)
    iqu_por_cluster = df.groupby("cluster")["iqu_mediano"].mean().sort_values(ascending=False)
    print("\nIQU médio por cluster:")
    print(iqu_por_cluster)

    df.to_csv(PROCESSED / "bairros_clusters.csv", index=False)
    perfil.to_csv(PROCESSED / "perfil_clusters.csv")
    print(f"\nSalvo em data/processed/bairros_clusters.csv")
    return best_k, df, perfil

if __name__ == "__main__":
    main()
