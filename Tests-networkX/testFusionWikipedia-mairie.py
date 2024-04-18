import networkx as nx
import matplotlib.pyplot as plt
import csv

#=============================================================  1er graphe  ===============================================================================================
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

# Ajoute un noeud qui va contenir les élus municipaux
G.add_node("Elus municipaux")


#===================================================================  2ème graphe  =========================================================================================
# Crée un graphe dirigé
G2 = nx.DiGraph()

# Ouvre le fichier CSV
with open('elus-municipaux-cm.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    # Saute la première ligne qui contient les en-têtes
    next(reader)
    for row in reader:
        # Vérifie si la ligne concerne la ville de Vourey
        if row[5] == "Vourey":
            # Récupére les informations de l'élu
            code_dept, libelle_dept, code_collectivite, libelle_collectivite, code_commune, libelle_commune, nom, prenom, sexe, date_naissance, code_cat_soc_pro, libelle_cat_soc_pro, date_debut_mandat, libelle_fonction, date_debut_fonction, nationalite = row

            # Crée un nœud pour l'élu
            G2.add_node(nom + ' ' + prenom)

            # Ajoute les attributs à ce nœud
            G2.nodes[nom + ' ' + prenom]['Code du département'] = code_dept
            G2.nodes[nom + ' ' + prenom]['Libellé du département'] = libelle_dept
            G2.nodes[nom + ' ' + prenom]['Code de la collectivité à statut particulier'] = code_collectivite
            G2.nodes[nom + ' ' + prenom]['Libellé de la collectivité à statut particulier'] = libelle_collectivite
            G2.nodes[nom + ' ' + prenom]['Code de la commune'] = code_commune
            G2.nodes[nom + ' ' + prenom]['Libellé de la commune'] = libelle_commune
            G2.nodes[nom + ' ' + prenom]['Nom de l\'élu'] = nom
            G2.nodes[nom + ' ' + prenom]['Prénom de l\'élu'] = prenom
            G2.nodes[nom + ' ' + prenom]['Code sexe'] = sexe
            G2.nodes[nom + ' ' + prenom]['Date de naissance'] = date_naissance
            G2.nodes[nom + ' ' + prenom]['Code de la catégorie socio-professionnelle'] = code_cat_soc_pro
            G2.nodes[nom + ' ' + prenom]['Libellé de la catégorie socio-professionnelle'] = libelle_cat_soc_pro
            G2.nodes[nom + ' ' + prenom]['Date de début du mandat'] = date_debut_mandat
            G2.nodes[nom + ' ' + prenom]['Libellé de la fonction'] = libelle_fonction
            G2.nodes[nom + ' ' + prenom]['Date de début de la fonction'] = date_debut_fonction
            G2.nodes[nom + ' ' + prenom]['Code nationalité'] = nationalite

# Ajoute les élus comme sous-nœuds du nœud "Elus municipaux"
for node in G2.nodes():
    G.add_edge("Elus municipaux", node)

# Fusion des deux graphes
G3 = nx.compose(G, G2)
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(G3, seed=42)  # Positionnement des nœuds
nx.draw(G3, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold')
plt.title('Graphe des élus municipaux et des parties et sous-parties de l\'infobox de la ville de Vourey')
# Affiche les éléments du graphe
print("Noeuds et attributs:")
for node, attrs in G3.nodes(data=True):
    print(node, attrs)
print("Noeuds", G3.nodes())
plt.show()