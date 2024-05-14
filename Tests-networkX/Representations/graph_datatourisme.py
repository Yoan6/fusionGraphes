import requests
import json
import networkx as nx
import matplotlib.pyplot as plt

ville = "Moirans"  # TODO A changer pour prendre en compte le code de la commune (objet['isLocatedAt']['schema:address']['hasAddressCity']['@id'][3:])

# Compteur pour les identifiants des nœuds
node_id_counter = 0

def extract_dataTourisme(url):
    # Télécharge le fichier JSON-LD depuis l'URL
    response = requests.get(url)
    data = response.json()
    return data

# URL pour télécharger le fichier JSON-LD
url = "https://diffuseur.datatourisme.fr/webservice/f4f07d2f40c98b4eb046da28af2e651c/031aee5f-9dd7-4196-a677-610abe8fda77"  # Clé API : 031aee5f-9dd7-4196-a677-610abe8fda77

# Extraction des données du fichier JSON-LD
data = extract_dataTourisme(url)

# Fonction pour filtrer les données pour la ville
def filter_dataTourisme(data, ville):
    etablissements_ville_recherchee = []
    # Parcourt chaque objet dans le fichier JSON-LD
    for objet in data['@graph']:
        if 'isLocatedAt' in objet and 'schema:address' in objet['isLocatedAt'] and 'schema:addressLocality' in \
                objet['isLocatedAt']['schema:address']:
            ville_etablissement = objet['isLocatedAt']['schema:address']['schema:addressLocality']      # TODO A changer pour prendre en compte le code de la commune : objet['isLocatedAt']['schema:address']['hasAddressCity']['@id'][3:]
            if ville == ville_etablissement:
                etablissements_ville_recherchee.append(objet)
    return etablissements_ville_recherchee

# Filtrage des données pour la ville
etablissements_ville_recherchee = filter_dataTourisme(data, ville)

# Fonction pour construire le graphe des établissements touristiques
def build_graph_datatourisme(data):
    global node_id_counter  # Utilisation de la variable externe node_id_counter

    # Initialisation de deux graphe dirigé, un pour les établissements économiques et un pour les établissements culturels
    G_culturel = nx.DiGraph()
    G_economique = nx.DiGraph()
    node_labels = {}
    edge_labels = {}
    node_details = {}  # Structure de données pour stocker les informations détaillées de chaque nœud

    # Création de l'identifiant unique du nœud en utilisant le compteur
    node_id_economie = node_id_counter
    node_id_counter += 1

    # Ajout du premier noeud pour les établissements économiques
    G_economique.add_node(node_id_economie)
    node_labels[node_id_economie] = "Tourisme et loisir"
    node_details[node_id_economie] = {
        'title': "Tourisme et loisir",
        'texte': "",
        'balise': "h3"
    }

    node_id_culturel = node_id_counter
    node_id_counter += 1

    # Ajout du premier noeud pour les établissements culturels
    G_culturel.add_node(node_id_culturel)
    node_labels[node_id_culturel] = "Patrimoine culturel"
    node_details[node_id_culturel] = {
        'title': "Patrimoine culturel",
        'texte': "",
        'balise': "h3"
    }

    def add_nodes():
        global node_id_counter

        title = objet['rdfs:label']['@value']
        # Description de l'établissement si elle existe sinon chaine vide
        text = objet['owl:topObjectProperty']['shortDescription']['@value'] if 'owl:topObjectProperty' in objet else ""

        # Création de l'identifiant unique du nœud en utilisant le compteur
        node_id_etablissement = node_id_counter
        node_id_counter += 1

        # Si l'établissement est économique on l'ajoute au graphe économique
        if ('schema:FoodEstablishment' or 'schema:LocalBusiness' or 'schema:Hotel' or 'schema:LodgingBusiness' or 'schema:Accommodation' or 'schema:TouristInformationCenter' or 'schema:Winery' or 'schema:Restaurant' or 'schema:Product') in objet['@type']:
            G_economique.add_node(node_id_etablissement)
            node_labels[node_id_etablissement] = title
            node_details[node_id_etablissement] = {
                'title': title,
                'text': "",
                'balise': "h4"
            }

            # On lie l'établissement au noeud économie
            G_economique.add_edge(node_id_economie, node_id_etablissement)
            edge_labels[(node_id_economie, node_id_etablissement)] = ''

            # On crée un noeud pour la description de l'établissement si elle existe
            if 'owl:topObjectProperty' in objet and objet['owl:topObjectProperty']['shortDescription']['@value']:
                node_id_description = node_id_counter
                node_id_counter += 1

                G_economique.add_node(node_id_description)
                node_labels[node_id_description] = "Description"
                node_details[node_id_description] = {
                    'title': "Description",
                    'text': objet['owl:topObjectProperty']['shortDescription']['@value'],
                    'balise': "p"
                }

                # On lie la description à l'établissement
                G_economique.add_edge(node_id_etablissement, node_id_description)
                edge_labels[(node_id_etablissement, node_id_description)] = ''


            # On crée un noeud pour les coordonnées de l'établissement si les coordonnées sont disponibles
            if ('schema:geo' in objet['isLocatedAt'] and 'schema:latitude' in objet['isLocatedAt']['schema:geo'] and 'schema:longitude' in objet['isLocatedAt']['schema:geo']):
                node_id_coord = node_id_counter
                node_id_counter += 1

                G_economique.add_node(node_id_coord)
                node_labels[node_id_coord] = "Coordonnées"
                node_details[node_id_coord] = {
                    'title': "Coordonnées",
                    'text': str(objet['isLocatedAt']['schema:geo']['schema:latitude']['@value']) + ", " + str(objet['isLocatedAt']['schema:geo']['schema:longitude']['@value']),
                    'balise': "p"
                }

                # On lie les coordonnées à l'établissement
                G_economique.add_edge(node_id_etablissement, node_id_coord)
                edge_labels[(node_id_etablissement, node_id_coord)] = ''

        # Si l'établissement est culturel on l'ajoute au graphe culturel
        else:
            G_culturel.add_node(node_id_etablissement)
            node_labels[node_id_etablissement] = title
            node_details[node_id_etablissement] = {
                'title': title,
                'text': "",
                'balise': "h4"
            }

            # On lie l'établissement au noeud culturel
            G_culturel.add_edge(node_id_culturel, node_id_etablissement)
            edge_labels[(node_id_culturel, node_id_etablissement)] = ''

            # On crée un noeud pour la description de l'établissement si elle existe
            if 'owl:topObjectProperty' in objet and objet['owl:topObjectProperty']['shortDescription']['@value']:
                node_id_description = node_id_counter
                node_id_counter += 1

                G_culturel.add_node(node_id_description)
                node_labels[node_id_description] = "Description"
                node_details[node_id_description] = {
                    'title': "Description",
                    'text': objet['owl:topObjectProperty']['shortDescription']['@value'],
                    'balise': "p"
                }

                # On lie la description à l'établissement
                G_culturel.add_edge(node_id_etablissement, node_id_description)
                edge_labels[(node_id_etablissement, node_id_description)] = ''

            # On crée un noeud pour les coordonnées de l'établissement si les coordonnées sont disponibles
            if ('schema:geo' in objet['isLocatedAt'] and 'schema:latitude' in objet['isLocatedAt']['schema:geo'] and 'schema:longitude' in objet['isLocatedAt']['schema:geo']):
                node_id_coord = node_id_counter
                node_id_counter += 1

                G_culturel.add_node(node_id_coord)
                node_labels[node_id_coord] = "Coordonnées"
                node_details[node_id_coord] = {
                    'title': "Coordonnées",
                    'text': str(objet['isLocatedAt']['schema:geo']['schema:latitude']['@value']) + ", " + str(objet['isLocatedAt']['schema:geo']['schema:longitude']['@value']),
                    'balise': "p"
                }

                # On lie les coordonnées à l'établissement
                G_culturel.add_edge(node_id_etablissement, node_id_coord)
                edge_labels[(node_id_etablissement, node_id_coord)] = ''


    # # Nom de l'établissement
    # print(objet['rdfs:label']['@value'])
    # print(objet['@id'])
    # print(objet['@type'])
    # # Code de la commune
    # print(objet['isLocatedAt']['schema:address']['hasAddressCity']['@id'][3:])  # On enlève les 3 premiers caractères (kb:) pour obtenir le code de la commune
    # if 'hasRepresentation' in objet and 'ebucore:hasRelatedResource' in objet['hasRepresentation']:
    #     print(objet['hasRepresentation']['ebucore:hasRelatedResource']['ebucore:locator']['@value'])
    # if ('owl:topObjectProperty' in objet):
    #     print(objet['owl:topObjectProperty']['shortDescription']['@value'])
    # print(objet['isLocatedAt']['schema:geo']['schema:latitude']['@value'], ",", objet['isLocatedAt']['schema:geo']['schema:longitude']['@value'])
    # print("")

    # Ajout des noeuds et des attributs pour chaque établissement
    for objet in data:
        add_nodes()

    return G_economique, G_culturel, node_labels, edge_labels, node_details

# Construction du graphe des établissements touristiques
G_economique, G_culturel, node_labels, edge_labels, node_details = build_graph_datatourisme(etablissements_ville_recherchee)

# Fusion des deux graphes pour obtenir un graphe unique
G = nx.compose(G_economique, G_culturel)

def display_node_info(G, node_details, node, depth=0):
    # Récupère les informations du nœud
    info = node_details[node]

    # Crée une chaîne de caractères pour afficher les informations du nœud
    if info['balise'] in ['h3', 'h4']:
        node_info = info['title']
    elif info['balise'] == 'p':
        node_info = info['text'].strip()
    else:
        node_info = ""

    # Affiche les informations du nœud avec l'indentation correspondante
    print("  " * depth + node_info)

    # Parcours récursif des enfants du nœud actuel
    for child in G.successors(node):
        display_node_info(G, node_details, child, depth + 1)

# On parcourt les noeuds pour trouver l'id du noeud des établissements économiques
for node_id in G.nodes():
    if node_labels[node_id] == "Tourisme et loisir":
        display_node_info(G, node_details, node_id)
        break

print("")

# On parcourt les noeuds pour trouver l'id du noeud des établissements culturels
for node_id in G.nodes():
    if node_labels[node_id] == "Patrimoine culturel":
        display_node_info(G, node_details, node_id)
        break

# Visualisation du graphe des établissements économiques
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=1500, node_color='lightblue', font_size=10,
        font_weight='bold')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
plt.title("Graphe des établissements économiques")
plt.show()