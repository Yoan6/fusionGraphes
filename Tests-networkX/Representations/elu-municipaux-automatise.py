import csv
import networkx as nx
import matplotlib.pyplot as plt

# Crée un graphe dirigé
G = nx.DiGraph()

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
            G.add_node(nom + ' ' + prenom)

            # Ajoute les attributs à ce nœud
            G.nodes[nom + ' ' + prenom]['Code du département'] = code_dept
            G.nodes[nom + ' ' + prenom]['Libellé du département'] = libelle_dept
            G.nodes[nom + ' ' + prenom]['Code de la collectivité à statut particulier'] = code_collectivite
            G.nodes[nom + ' ' + prenom]['Libellé de la collectivité à statut particulier'] = libelle_collectivite
            G.nodes[nom + ' ' + prenom]['Code de la commune'] = code_commune
            G.nodes[nom + ' ' + prenom]['Libellé de la commune'] = libelle_commune
            G.nodes[nom + ' ' + prenom]['Nom de l\'élu'] = nom
            G.nodes[nom + ' ' + prenom]['Prénom de l\'élu'] = prenom
            G.nodes[nom + ' ' + prenom]['Code sexe'] = sexe
            G.nodes[nom + ' ' + prenom]['Date de naissance'] = date_naissance
            G.nodes[nom + ' ' + prenom]['Code de la catégorie socio-professionnelle'] = code_cat_soc_pro
            G.nodes[nom + ' ' + prenom]['Libellé de la catégorie socio-professionnelle'] = libelle_cat_soc_pro
            G.nodes[nom + ' ' + prenom]['Date de début du mandat'] = date_debut_mandat
            G.nodes[nom + ' ' + prenom]['Libellé de la fonction'] = libelle_fonction
            G.nodes[nom + ' ' + prenom]['Date de début de la fonction'] = date_debut_fonction
            G.nodes[nom + ' ' + prenom]['Code nationalité'] = nationalite

# Affiche les nœuds et les attributs du graphe
print("Noeuds et attributs:")
for node, attrs in G.nodes(data=True):
    print(node, attrs)

# Dessine le graphe
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(G, seed=42)  # Positionnement des nœuds
nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold')
plt.title('Graphe des élus municipaux de Vourey')
plt.show()
