from sklearn.metrics import normalized_mutual_info_score

# --- Suivi de l'évolution des communautés dynamiques ---
def track_community_events(communities_prev, communities_next):
    """
    Détecte les événements dynamiques entre deux partitions de communautés :
    - naissance, mort, fusion, scission
    Retourne un dict {"birth":[], "death":[], "merge":[], "split":[], "stable":[]}
    """
    prev_sets = [set(c) for c in communities_prev]
    next_sets = [set(c) for c in communities_next]
    events = {"birth":[], "death":[], "merge":[], "split":[], "stable":[]}
    # Naissance : communauté nouvelle sans intersection significative avec les anciennes
    for c2 in next_sets:
        overlaps = [len(c2 & c1) for c1 in prev_sets]
        if max(overlaps, default=0) == 0:
            events["birth"].append(list(c2))
    # Mort : communauté ancienne sans intersection significative avec les nouvelles
    for c1 in prev_sets:
        overlaps = [len(c1 & c2) for c2 in next_sets]
        if max(overlaps, default=0) == 0:
            events["death"].append(list(c1))
    # Fusion : plusieurs anciennes -> une nouvelle
    for c2 in next_sets:
        matches = [c1 for c1 in prev_sets if len(c1 & c2) > 0]
        if len(matches) > 1:
            events["merge"].append({"new": list(c2), "from": [list(c) for c in matches]})
    # Scission : une ancienne -> plusieurs nouvelles
    for c1 in prev_sets:
        matches = [c2 for c2 in next_sets if len(c1 & c2) > 0]
        if len(matches) > 1:
            events["split"].append({"old": list(c1), "to": [list(c) for c in matches]})
    # Stables : recouvrement fort (Jaccard > 0.8)
    for c2 in next_sets:
        for c1 in prev_sets:
            if len(c2 & c1) > 0 and (len(c2 & c1) / max(len(c2 | c1),1)) > 0.8:
                events["stable"].append(list(c2))
    return events

# --- NMI (Normalized Mutual Information) ---
def compute_nmi(partition_a, partition_b, node_list=None):
    """
    Calcule le NMI entre deux partitions (listes de communautés)
    partition_a, partition_b : listes de listes de noeuds
    node_list : ensemble de tous les noeuds (optionnel)
    """
    if node_list is None:
        node_list = set()
        for c in partition_a + partition_b:
            node_list.update(c)
        node_list = sorted(node_list)
    label_a = [-1]*len(node_list)
    label_b = [-1]*len(node_list)
    node_to_idx = {n:i for i,n in enumerate(node_list)}
    for idx, comm in enumerate(partition_a):
        for n in comm:
            label_a[node_to_idx[n]] = idx
    for idx, comm in enumerate(partition_b):
        for n in comm:
            label_b[node_to_idx[n]] = idx
    return normalized_mutual_info_score(label_a, label_b)
"""
community_dissimilarity.py
Détection de communautés dynamiques par mesure de dissimilarité
Basé sur l'article : Dissimilarity Measure for Community Discovery in Dynamic Networks
"""
import networkx as nx
import numpy as np
from typing import List

def compute_L(G, v):
    """Nombre de liens entre voisins de v"""
    neighbors = list(G.neighbors(v))
    return G.subgraph(neighbors).number_of_edges()

def edge_dissimilarity(G, u, v, threshold):
    neighbors_u = set(G.neighbors(u))
    neighbors_v = set(G.neighbors(v))
    C = len(neighbors_u & neighbors_v)
    U = len(neighbors_u | neighbors_v)
    L = compute_L(G, u) + compute_L(G, v)
    S = len(neighbors_u) + len(neighbors_v)
    if C > 0:
        if U > 0 and (C / U) < threshold:
            return L / (C * S) if (C * S) > 0 else 0
        else:
            return 0
    else:
        return L

def compute_all_dissimilarities(G):
    density = nx.density(G)
    threshold = 0.5 if density >= 0.001 else 0.25
    for u, v in G.edges():
        G[u][v]['dissimilarity'] = edge_dissimilarity(G, u, v, threshold)

def remove_edges_iteratively(G):
    G = G.copy()
    compute_all_dissimilarities(G)
    edges_sorted = sorted(G.edges(data=True), key=lambda x: x[2]['dissimilarity'], reverse=True)
    # Pour chaque nœud, on garde la trace de la dernière arête supprimée qui le reliait à une autre composante
    last_bridge = dict()  # clé: frozenset(sous-graphe), valeur: (u, v)
    for u, v, data in edges_sorted:
        if G.degree(u) > 1 and G.degree(v) > 1:
            # Avant suppression, noter les composantes auxquelles appartiennent u et v
            comp_u = None
            comp_v = None
            for comp in nx.connected_components(G):
                if u in comp:
                    comp_u = frozenset(comp)
                if v in comp:
                    comp_v = frozenset(comp)
            G.remove_edge(u, v)
            # Après suppression, si u ou v devient isolé, mémoriser la dernière arête qui le reliait
            for comp in nx.connected_components(G):
                if len(comp) < 4:
                    # Trouver si comp contient u ou v
                    if u in comp or v in comp:
                        # On note la dernière arête supprimée qui reliait ce sous-graphe
                        last_bridge[frozenset(comp)] = (u, v)
    return G, last_bridge

def merge_small_communities(G, last_bridge, min_size=4):
    # Détecter toutes les composantes connexes
    communities = [set(int(n) for n in c) for c in nx.connected_components(G)]
    large = [c for c in communities if len(c) >= min_size]
    small = [c for c in communities if len(c) < min_size]
    merged = list(large)
    used = set()
    # Fusion stricte selon la dernière arête supprimée
    for s in small:
        key = frozenset(s)
        if key in last_bridge:
            u, v = last_bridge[key]
            # Trouver la composante cible (celle contenant u ou v qui n'est pas s)
            target = None
            for c in merged:
                if (u in c or v in c) and not s.issubset(c):
                    target = c
                    break
            if target is not None:
                merged = [c for c in merged if c != target]
                merged.append(target | s)
                used.update(target | s)
            else:
                merged.append(s)
                used.update(s)
        else:
            merged.append(s)
            used.update(s)
    # Ajouter les nœuds isolés manquants
    missing = set(int(n) for n in G.nodes()) - set().union(*merged)
    for n in missing:
        merged.append({n})
    return merged

def detect_communities_dissimilarity(G, min_size=4):
    G2, last_bridge = remove_edges_iteratively(G)
    communities = merge_small_communities(G2, last_bridge, min_size=min_size)
    return communities

def compute_modularity(G, communities):
    return nx.algorithms.community.quality.modularity(G, communities)

def process_dynamic_graphs(graph_snapshots: List[nx.Graph]):
    results = []
    for t, G in enumerate(graph_snapshots):
        comms = detect_communities_dissimilarity(G)
        results.append({'t': t, 'communities': comms, 'graph': G})
    return results
