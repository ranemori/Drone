"""
placelab_loader.py
Chargement et transformation du dataset PlaceLab (traces_placelab.csv) en snapshots de graphes pour analyse dynamique.
"""
import pandas as pd
import networkx as nx
from typing import List

def load_placelab_snapshots(csv_path: str, rssi_threshold: float = -90, window_size: float = 10.0) -> List[nx.Graph]:
    """
    Charge le dataset PlaceLab et génère une liste de graphes (snapshots temporels)
    - rssi_threshold : seuil RSSI pour créer une arête
    - window_size : taille de la fenêtre temporelle (en secondes)
    """
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['node_id', 'rssi'])
    df['time'] = df['time'].astype(float)
    df['node_id'] = df['node_id'].astype(int)
    df['rssi'] = df['rssi'].astype(float)
    df['window'] = (df['time'] // window_size).astype(int)
    snapshots = []
    for window, group in df.groupby('window'):
        G = nx.Graph()
        nodes = group['node_id'].unique()
        G.add_nodes_from(nodes)
        # Pour chaque paire de noeuds, créer une arête si RSSI > seuil
        for i, ni in enumerate(nodes):
            rssi_i = group[group['node_id'] == ni]['rssi'].mean()
            for nj in nodes[i+1:]:
                rssi_j = group[group['node_id'] == nj]['rssi'].mean()
                rssi_avg = (rssi_i + rssi_j) / 2
                if rssi_avg >= rssi_threshold:
                    G.add_edge(ni, nj, rssi=rssi_avg)
        if G.number_of_nodes() > 0:
            snapshots.append(G)
    return snapshots
