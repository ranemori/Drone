# Réseau de Drones – Détection de Communautés Dynamiques

Détection et suivi de communautés dynamiques dans un réseau de drones, basée sur la mesure de dissimilarité (article : "Dissimilarity Measure for Community Discovery in Dynamic Networks").

## Fonctionnalités principales

- **Détection de communautés dynamiques** : Algorithme strictement conforme à l’article (suppression d’arêtes, fusion selon la dernière connexion, reconnexion d’arête)
- **Datasets drones/WSN** : PlaceLab, WSN, ou tout graphe dynamique compatible
- **Export des résultats** : CSV et JSON (communautés, modularité, NMI, événements dynamiques)
- **Visualisations automatiques** :
  - Courbes de modularité et NMI (type figures de l’article)
  - Graphes de communautés colorés à différents snapshots
- **Simulation de réseaux de drones** : Génération de scénarios WSN/drones

## Structure du Projet

```
TheorieGraph_Drone/
├── data/                    # Datasets WSN
│   ├── traces_placelab.csv  # Exemple PlaceLab
│   ├── wsn_patrouille_zone.csv
│   ├── wsn_formation_essaim.csv
│   ├── wsn_suivi_cibles.csv
│   └── metadata.json
├── src/                     # Code source
│   ├── main.py              # Pipeline principal (communautés dynamiques)
│   ├── placelab_loader.py   # Chargement PlaceLab
│   ├── community_dissimilarity.py # Algorithme dissimilarité
│   └── ...
├── resultats/               # Exports CSV/JSON et visualisations
├── requirements.txt         # Dépendances Python
└── README.md                # Ce fichier
```

## Installation

### Prérequis

- Python 3.8+
- pip

### Installation des dépendances

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Utilisation

### 1. Télécharger ou générer des datasets

#### a Télécharger des données réelles CRAWDAD (capteurs, mobilité, etc.)

```bash
python scripts/download_crawdad_data.py
```

Ce script permet de télécharger automatiquement des jeux de données réels (Intel Berkeley, SensorScope, etc.) dans le dossier `data/`.

#### b (Optionnel) Générer des scénarios synthétiques WSN/drones

Si vous disposez d'un script de génération (non inclus par défaut), placez-le dans `src/` ou adaptez vos propres données au format CSV compatible.

### 2. Détection de communautés dynamiques (PlaceLab ou WSN)

```bash
python src/main.py
```

Génère automatiquement :
- `resultats/resultats_dynamiques.csv` et `.json` (toutes les métriques)
- `resultats/courbes_modularite_nmi.png` 
- `resultats/communautes_t0.png`, `communautes_tX.png`… (graphes de communautés à différents temps)

## Algorithme de détection de communautés dynamiques 

1. **Suppression d’arêtes par dissimilarité** : Classement et suppression progressive des arêtes selon la mesure de dissimilarité (article Asmi)
2. **Traçabilité stricte** : Pour chaque sous-graphe isolé, mémorisation de la dernière arête supprimée qui le reliait au reste du réseau
3. **Fusion stricte** : Chaque petit sous-graphe est fusionné uniquement avec la composante à laquelle il était relié par la dernière arête supprimée (pas d’optimisation globale)
4. **Reconnexion d’arête** : Test de la modularité en reconnectant la première arête supprimée, comme dans l’algorithme 3 de l’article
5. **Évaluation** : Calcul automatique de la modularité et du NMI à chaque snapshot

### Métriques

- **Modularité** : Qualité de la partition en communautés
- **NMI** : Similarité entre partitions consécutives (Normalized Mutual Information)
- **Événements dynamiques** : naissance, mort, fusion, scission, stabilité des communautés

## Résultats

Les résultats de la détection de communautés dynamiques sont sauvegardés dans `resultats/` :
- `resultats_dynamiques.csv` et `.json` : toutes les communautés, modularité, NMI, événements dynamiques
- `courbes_modularite_nmi.png` : courbes de modularité et NMI (type figures de l’article)
- `communautes_t0.png`, `communautes_tX.png` : visualisation des communautés à différents temps

## Dépendances principales

- networkx : Manipulation de graphes
- numpy : Calcul numérique
- matplotlib, seaborn : Visualisations
- pandas : Traitement de données
- scikit-learn : Calcul du NMI

## Licence

MIT License - Voir LICENSE pour détails

## Auteur

*Rania*
Projet académique – Théorie des graphes appliquée aux réseaux de drones, détection de communautés dynamiques 
