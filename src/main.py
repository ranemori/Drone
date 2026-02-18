def plot_dissimilarity_histogram(results, out_path="resultats/histogramme_dissimilarites.png"):
    """
    Trace l'histogramme de toutes les valeurs de dissimilarité calculées sur les arêtes de tous les snapshots.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    dissim_values = []
    for res in results:
        G = res.get('graph')
        if G is None:
            continue
        for u, v, data in G.edges(data=True):
            diss = data.get('dissimilarity')
            if diss is not None:
                dissim_values.append(diss)
    if not dissim_values:
        print("Aucune dissimilarité trouvée pour l'histogramme.")
        return
    plt.figure(figsize=(7,5))
    sns.histplot(dissim_values, bins=30, kde=True, color="purple")
    plt.xlabel("Dissimilarité des arêtes")
    plt.ylabel("Nombre d'arêtes")
    plt.title("Histogramme des dissimilarités (tous snapshots)")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.show()
def plot_communities_count_curve(modularity_list, nmi_list, export_rows, out_path="resultats/courbe_nb_communautes.png"):
    """
    Trace la courbe du nombre de communautés détectées à chaque snapshot, avec modularité et NMI.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.figure(figsize=(12,5))
    x = list(range(len(modularity_list)))
    modularity_y = [m if m is not None else float('nan') for m in modularity_list]
    nmi_y = [n if n is not None else float('nan') for n in nmi_list]
    nb_comms = [row.get("nb_communities", float('nan')) for row in export_rows]
    ax1 = plt.gca()
    l1 = ax1.plot(x, modularity_y, label="Modularité", color="tab:orange")
    l2 = ax1.plot(x, nmi_y, label="NMI", color="tab:green")
    ax1.set_xlabel("Snapshot t")
    ax1.set_ylabel("Modularité / NMI")
    ax2 = ax1.twinx()
    l3 = ax2.plot(x, nb_comms, label="Nb communautés", color="tab:blue", linestyle="--", marker="o")
    ax2.set_ylabel("Nombre de communautés")
    # Fusionner légendes
    lines = l1 + l2 + l3
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper left")
    plt.title("Modularité, NMI et nombre de communautés")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.show()
def plot_curves_with_event_markers(modularity_list, nmi_list, export_rows, out_path="resultats/courbes_modularite_nmi_evenements.png"):
    """
    Trace les courbes de modularité et NMI avec des marqueurs verticaux aux snapshots où une fusion ou scission a lieu.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.figure(figsize=(12,5))
    x = list(range(len(modularity_list)))
    modularity_y = [m if m is not None else float('nan') for m in modularity_list]
    nmi_y = [n if n is not None else float('nan') for n in nmi_list]
    sns.lineplot(x=x, y=modularity_y, label="Modularité")
    sns.lineplot(x=x, y=nmi_y, label="NMI")
    # Chercher les snapshots avec fusion/scission
    fusion_idx = []
    scission_idx = []
    for i, row in enumerate(export_rows):
        events = row.get("events")
        if not events:
            continue
        if events.get("merge"):
            fusion_idx.append(i)
        if events.get("split"):
            scission_idx.append(i)
    for idx in fusion_idx:
        plt.axvline(idx, color="red", linestyle=":", alpha=0.6, label="Fusion" if idx==fusion_idx[0] else None)
    for idx in scission_idx:
        plt.axvline(idx, color="blue", linestyle="--", alpha=0.6, label="Scission" if idx==scission_idx[0] else None)
    plt.xlabel("Snapshot t")
    plt.ylabel("Valeur")
    plt.title("Évolution de la modularité et du NMI (événements)")
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.tight_layout()
    plt.savefig(out_path)
    plt.show()
def plot_event_histogram(export_rows, out_path="resultats/histogramme_evenements.png"):
    """
    Affiche un histogramme des événements dynamiques (fusion, scission, naissance, mort, stable) sur toute la séquence.
    export_rows: liste de dicts contenant la clé 'events' (une par snapshot)
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    from collections import Counter
    event_types = ["birth", "death", "merge", "split", "stable"]
    total_counts = Counter({k:0 for k in event_types})
    for row in export_rows:
        events = row.get("events")
        if not events:
            continue
        for k in event_types:
            v = events.get(k, [])
            if k in ("merge", "split"):
                total_counts[k] += len(v)
            else:
                total_counts[k] += len(v)
    plt.figure(figsize=(7,5))
    sns.barplot(x=list(total_counts.keys()), y=list(total_counts.values()), palette="muted")
    plt.ylabel("Nombre d'événements")
    plt.title("Histogramme des événements dynamiques")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.show()
"""
main.py
Projet : Détection de communautés dynamiques dans un réseau de drones
Basé sur l'article : Dissimilarity Measure for Community Discovery in Dynamic Networks
"""


from placelab_loader import load_placelab_snapshots
from community_dissimilarity import process_dynamic_graphs, track_community_events, compute_nmi, compute_modularity

def plot_comparaison_multi(csv_files, labels, col, ylabel, out_path):
    """
    Génère une courbe de comparaison multi-méthodes (NMI ou modularité).
    csv_files: liste de chemins CSV (un par méthode)
    labels: noms à afficher dans la légende
    col: nom de la colonne à tracer ('nmi', 'modularity', ...)
    ylabel: label de l'axe Y
    out_path: chemin du fichier de sortie
    """
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
    plt.figure(figsize=(7,5))
    for csv, label in zip(csv_files, labels):
        df = pd.read_csv(csv)
        if col in df.columns:
            y = df[col].fillna(0).values
        elif col.upper() in df.columns:
            y = df[col.upper()].fillna(0).values
        else:
            continue
        x = range(1, len(y)+1)
        plt.plot(x, y, marker='o', label=label)
    plt.xlabel('TimeSteps')
    plt.ylabel(ylabel)
    plt.title(ylabel + ' comparison')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.show()

def auto_plot_comparaisons(resultats_dir="resultats"):
    """
    Génère automatiquement toutes les figures de comparaison NMI et modularité pour tous les fichiers CSV présents dans resultats/.
    """
    import glob
    import os
    csv_files = glob.glob(os.path.join(resultats_dir, "*.csv"))
    # Détection des méthodes et labels
    labels = [os.path.splitext(os.path.basename(f))[0].replace("resultats_dynamiques", "Our method").replace("nmi_", "").replace("modularity_", "").upper() for f in csv_files]
    # NMI
    plot_comparaison_multi(csv_files, labels, col="nmi", ylabel="NMI", out_path=os.path.join(resultats_dir, "comparaison_nmi.png"))
    # Modularité
    plot_comparaison_multi(csv_files, labels, col="modularity", ylabel="Modularity", out_path=os.path.join(resultats_dir, "comparaison_modularite.png"))
    """
    Génère une courbe de comparaison NMI (ou modularité) multi-méthodes comme dans l'article.
    csv_files: liste de chemins CSV (un par méthode)
    labels: noms à afficher dans la légende
    out_path: chemin du fichier de sortie
    """
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
    plt.figure(figsize=(7,5))
    for csv, label in zip(csv_files, labels):
        df = pd.read_csv(csv)
        if 'nmi' in df.columns:
            y = df['nmi'].fillna(0).values
        elif 'NMI' in df.columns:
            y = df['NMI'].fillna(0).values
        else:
            continue
        x = range(1, len(y)+1)
        plt.plot(x, y, marker='o', label=label)
    plt.xlabel('TimeSteps')
    plt.ylabel('NMI')
    plt.title('Normalized mutual information')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.show()

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import json
    import os
    import networkx as nx
    import imageio
    # Charger les snapshots PlaceLab (données réelles)
    snapshots = load_placelab_snapshots("data/traces_placelab.csv", rssi_threshold=-90, window_size=10.0)
    print(f"{len(snapshots)} snapshots extraits du dataset PlaceLab.")
    results = process_dynamic_graphs(snapshots)

    prev_communities = None
    modularity_list = []
    nmi_list = []
    export_rows = []
    export_json = []
    # Exporter tous les snapshots pour GIF animé
    snapshots_to_plot = list(range(len(results)))
    gif_images = []
    for i, res in enumerate(results):
        comms = res['communities']
        G = res['graph']
        row = {"t": res['t'], "nb_communities": len(comms)}
        # Vérification partition valide
        if not comms or any(len(c) == 0 for c in comms):
            print(f"Snapshot t={res['t']} : Partition vide ou invalide, modularité non calculée.")
            row["modularity"] = None
            row["nmi"] = None
            row["communities"] = [sorted(list(c)) for c in comms]
            row["events"] = None
            export_rows.append(row)
            export_json.append(row)
            continue
        try:
            if G.number_of_edges() > 0:
                modularity = compute_modularity(G, comms)
                modularity_list.append(modularity)
                print(f"Snapshot t={res['t']} : {len(comms)} communautés, modularité={modularity:.3f}")
                row["modularity"] = modularity
            else:
                print(f"Snapshot t={res['t']} : {len(comms)} communautés, modularité non calculée (graphe sans arêtes)")
                modularity_list.append(None)
                row["modularity"] = None
        except Exception as e:
            print(f"Snapshot t={res['t']} : {len(comms)} communautés, modularité non calculée (erreur: {e})")
            modularity_list.append(None)
            row["modularity"] = None
        for idx, comm in enumerate(comms):
            print(f"  Communauté {idx+1}: {sorted(comm)}")
        # Suivi dynamique des événements et NMI
        if prev_communities is not None:
            events = track_community_events(prev_communities, comms)
            nmi = compute_nmi(prev_communities, comms)
            print(f"  Événements dynamiques : {events}")
            print(f"  NMI avec snapshot précédent : {nmi:.4f}")
            nmi_list.append(nmi)
            row["nmi"] = nmi
            row["events"] = events
        else:
            nmi_list.append(None)
            row["nmi"] = None
            row["events"] = None
        row["communities"] = [sorted(list(c)) for c in comms]
        export_rows.append(row)
        export_json.append(row)
        prev_communities = comms
        print()

        # Visualisation du graphe de communautés pour chaque snapshot (pour GIF)
        plt.figure(figsize=(7,5))
        pos = None
        try:
            pos = nx.spring_layout(G, seed=42)
        except:
            pos = None
        colors = sns.color_palette('hls', len(comms))
        node_color_map = {}
        for idx, comm in enumerate(comms):
            for n in comm:
                node_color_map[n] = colors[idx]
        node_colors = [node_color_map.get(n, (0.5,0.5,0.5)) for n in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=300, alpha=0.8)
        nx.draw_networkx_edges(G, pos, alpha=0.3)
        nx.draw_networkx_labels(G, pos, font_size=10)
        plt.title(f"Communautés à t={i}")
        plt.axis('off')
        plt.tight_layout()
        img_path = f"resultats/communautes_t{i}.png"
        plt.savefig(img_path)
        plt.close()
        gif_images.append(imageio.imread(img_path))

        # Cartographie des arêtes supprimées (rouge = supprimée, gris = présente)
        if hasattr(res, 'edges_removed') or 'edges_removed' in res:
            edges_removed = res.get('edges_removed', [])
        else:
            edges_removed = []
        # Pour la compatibilité, on tente de retrouver les arêtes supprimées si elles sont stockées
        # (sinon, cette partie peut être adaptée si edges_removed est à ajouter dans process_dynamic_graphs)
        # On colorie les arêtes supprimées en rouge, les autres en gris
        plt.figure(figsize=(7,5))
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=300, alpha=0.8)
        # Arêtes présentes
        nx.draw_networkx_edges(G, pos, edgelist=list(G.edges()), edge_color="#888888", alpha=0.3)
        # Arêtes supprimées (si connues)
        if edges_removed:
            nx.draw_networkx_edges(G, pos, edgelist=edges_removed, edge_color="red", width=2, alpha=0.7)
        nx.draw_networkx_labels(G, pos, font_size=10)
        plt.title(f"Arêtes supprimées à t={i}")
        plt.axis('off')
        plt.tight_layout()
        img_path2 = f"resultats/edges_removed_t{i}.png"
        plt.savefig(img_path2)
        plt.close()

    # Export CSV
    df_export = pd.DataFrame(export_rows)
    os.makedirs("resultats", exist_ok=True)
    df_export.to_csv("resultats/resultats_dynamiques.csv", index=False)
    # Export JSON
    with open("resultats/resultats_dynamiques.json", "w", encoding="utf-8") as fjson:
        json.dump(export_json, fjson, ensure_ascii=False, indent=2)

    # Visualisation courbes modularité/NMI avec marqueurs d'événements
    plot_curves_with_event_markers(modularity_list, nmi_list, export_rows)

    # Courbe du nombre de communautés
    plot_communities_count_curve(modularity_list, nmi_list, export_rows)

    # Histogramme des dissimilarités (tous snapshots)
    plot_dissimilarity_histogram(results)

    # Génération du GIF animé de l'évolution des communautés
    imageio.mimsave("resultats/animation_communautes.gif", gif_images, duration=0.5)

    # Génération automatique des figures de comparaison NMI et modularité (tous les CSV de resultats/)
    auto_plot_comparaisons()

    # Histogramme des événements dynamiques (barplot)
    plot_event_histogram(export_rows)
