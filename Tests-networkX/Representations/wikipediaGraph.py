import networkx as nx
import matplotlib.pyplot as plt

# Création d'un graphe orienté
G = nx.DiGraph()

# Ajout des parties principales comme nœuds
parties_principales = [
    "Administration",
    "Démographie",
    "Géographie",
    "Élections"
]
G.add_nodes_from(parties_principales)

# Ajout des sous-parties et des arcs entre les parties principales et les sous-parties
sous_parties = {
    "Administration": ["Pays", "Région", "Département", "Arrondissement", "Intercommunalité", "Maire", "Mandat", "Code postal", "Code commune"],
    "Démographie": ["Population municipale", "Densité", "Population", "Population agglomération"],
    "Géographie": ["Coordonnées", "Altitude", "Superficie", "Type", "Unité urbaine", "Aire d'attraction"],
    "Élections": ["Départementales", "Législatives"]
}

# Ajout des textes liés aux sous-parties comme attributs de nœuds
textes = {
    "Pays": "France",
    "Région": "Auvergne-Rhône-Alpes",
    "Département": "Isère",
    "Arrondissement": "Grenoble",
    "Intercommunalité": "Communauté d'agglomération du Pays voironnais",
    "Maire": "Fabienne Blachot-Minassian",
    "Mandat": "Minassian 2020-2026",
    "Code postal": "38210",
    "Code commune": "38566",
    "Population municipale": "1 687 hab. (2021 en diminution de 1,4 % par rapport à 2015)",
    "Densité": "245 hab./km2",
    "Population agglomération": "63 320 hab. (2021)",
    "Coordonnées": "45° 19′ 18″ nord, 5° 31′ 14″ est",
    "Altitude": "Min. 181 m Max. 402 m",
    "Superficie": "6,88 km2",
    "Type": "Commune urbaine",
    "Unité urbaine": "Voiron (banlieue)",
    "Aire d'attraction": "Grenoble (commune de la couronne)",
    "Départementales": "Canton de Tullins",
    "Législatives": "Neuvième circonscription"
}

# Ajout des sous-parties et des arcs entre les parties principales et les sous-parties
for partie, sous_parties_liste in sous_parties.items():
    for sous_partie in sous_parties_liste:
        G.add_node(sous_partie, text=textes.get(sous_partie, ""))  # Ajoute le nœud de la sous-partie avec le texte correspondant
        G.add_edge(partie, sous_partie)  # Ajoute un arc de la partie à la sous-partie

# Affiche les nœuds et les attributs du graphe
print("Noeuds et attributs:")
for node, attrs in G.nodes(data=True):
    print(node, attrs)

# Dessine le graphe
pos = nx.spring_layout(G, seed=42)  # Positionnement des nœuds
# Dessine les parties principales avec une couleur différente
nx.draw_networkx_nodes(G, pos, nodelist=parties_principales, node_color="lightblue", node_size=3000, label="Parties principales")
# Dessine les sous-parties avec une couleur différente
nx.draw_networkx_nodes(G, pos, nodelist=G.nodes()-parties_principales, node_color="lightgreen", node_size=2000, label="Sous-parties")
nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")
plt.title("Graphe des parties et sous-parties de l'infobox de la ville de Vourey")
plt.legend()
print("G : ", G.nodes.items())
plt.show()
