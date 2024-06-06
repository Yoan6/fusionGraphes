import requests
import json
import networkx as nx
import matplotlib.pyplot as plt

# Ville à rechercher
ville = "Mens"
code_commune = "38226"  # Code de la commune

# Compteur pour les identifiants des nœuds
global node_id_counter
node_id_counter = 0

# Fonction pour extraire les données de DataTourisme à partir de l'URL JSON-LD
def extract_data_tourisme(url):
    # Télécharge le fichier JSON-LD depuis l'URL
    response = requests.get(url)
    data = response.json()
    return data

# URL pour télécharger le fichier JSON-LD (à changer selon le flux de données souhaité sur DATAtourisme)
# URL pour le flux avec le département de l'Isère :
# url = "https://diffuseur.datatourisme.fr/webservice/f4f07d2f40c98b4eb046da28af2e651c/031aee5f-9dd7-4196-a677-610abe8fda77"  # Clé API : 031aee5f-9dd7-4196-a677-610abe8fda77

# URL pour le flux avec les départements avec le plus de données :
url = "https://diffuseur.datatourisme.fr/webservice/6d4c99395d621906226e38084555b15a/031aee5f-9dd7-4196-a677-610abe8fda77"    # Clé API : 031aee5f-9dd7-4196-a677-610abe8fda77

# Extraction des données de DataTourisme
data = extract_data_tourisme(url)

# Fonction pour filtrer les données pour la ville donnée
def filter_data_tourisme(data, ville, code_commune):
    etablissements_ville_recherchee = []
    # Parcourt chaque objet dans le fichier JSON-LD
    for objet in data['@graph']:
        if 'isLocatedAt' in objet and 'schema:address' in objet['isLocatedAt'] and 'schema:addressLocality' in objet['isLocatedAt']['schema:address']:
            ville_etablissement = objet['isLocatedAt']['schema:address']['schema:addressLocality']
            code_commune_etablissement = objet['isLocatedAt']['schema:address']['hasAddressCity']['@id'][3:]
            if ville == ville_etablissement and code_commune == code_commune_etablissement:
                etablissements_ville_recherchee.append(objet)
    return etablissements_ville_recherchee

# Filtrage des données pour la ville donnée
etablissements_ville_recherchee = filter_data_tourisme(data, ville, code_commune)

# Si aucun établissement n'est trouvé pour la ville recherchée, ne rien faire
if etablissements_ville_recherchee:
    # Fonction pour construire le graphe des établissements touristiques
    def build_graph_data_tourisme(data):
        global node_id_counter  # Utilisation de la variable externe node_id_counter

        # Initialisation de deux graphes dirigés, un pour les établissements économiques et un pour les établissements culturels
        G_economique = nx.DiGraph()
        G_culturel = nx.DiGraph()
        node_labels = {}
        edge_labels = {}

        # Création des nœuds racines pour les deux types d'établissements
        node_id_economique = node_id_counter
        node_id_counter += 1
        G_economique.add_node(node_id_economique, title="Tourisme et loisir", text="", balise="h3")
        node_labels[node_id_economique] = "Tourisme et loisir"

        node_id_culturel = node_id_counter
        node_id_counter += 1
        G_culturel.add_node(node_id_culturel, title="Patrimoine culturel", text="", balise="h3")
        node_labels[node_id_culturel] = "Patrimoine culturel"

        # Fonction pour ajouter les nœuds et les attributs pour chaque établissement
        def add_nodes():
            global node_id_counter

            # Récupération des informations de l'établissement
            title = objet['rdfs:label']['@value']

            # Création de l'identifiant unique du nœud
            node_id_etablissement = node_id_counter
            node_id_counter += 1

            # Ajout de l'établissement au graphe approprié
            if ('schema:FoodEstablishment' or 'schema:LocalBusiness' or 'schema:Hotel' or 'schema:LodgingBusiness' or 'schema:Accommodation' or 'schema:TouristInformationCenter' or 'schema:Winery' or 'schema:Restaurant' or 'schema:Product') in objet['@type']:
                G_economique.add_node(node_id_etablissement, title=title, text="", balise="h4")
                node_labels[node_id_etablissement] = title

                # Liaison avec le nœud économique
                G_economique.add_edge(node_id_economique, node_id_etablissement)
                edge_labels[(node_id_economique, node_id_etablissement)] = ''

                # Ajout d'un nœud pour la description si elle existe
                if 'owl:topObjectProperty' in objet and objet['owl:topObjectProperty'] and 'shortDescription' in objet['owl:topObjectProperty']:
                    node_id_description = node_id_counter
                    node_id_counter += 1
                    G_economique.add_node(node_id_description, title="Description", text=objet['owl:topObjectProperty']['shortDescription']['@value'], balise="p")
                    node_labels[node_id_description] = "Description"
                    G_economique.add_edge(node_id_etablissement, node_id_description)
                    edge_labels[(node_id_etablissement, node_id_description)] = ''

                # Ajout d'un nœud pour les coordonnées si elles sont disponibles
                if ('schema:geo' in objet['isLocatedAt'] and 'schema:latitude' in objet['isLocatedAt']['schema:geo'] and 'schema:longitude' in objet['isLocatedAt']['schema:geo']):
                    node_id_coord = node_id_counter
                    node_id_counter += 1
                    G_economique.add_node(node_id_coord, title="Coordonnées", text=str(objet['isLocatedAt']['schema:geo']['schema:latitude']['@value']) + ", " + str(objet['isLocatedAt']['schema:geo']['schema:longitude']['@value']), balise="p")
                    node_labels[node_id_coord] = "Coordonnées"
                    G_economique.add_edge(node_id_etablissement, node_id_coord)
                    edge_labels[(node_id_etablissement, node_id_coord)] = ''
            else:
                G_culturel.add_node(node_id_etablissement, title=title, text="", balise="h4")
                node_labels[node_id_etablissement] = title

                # Liaison avec le nœud culturel
                G_culturel.add_edge(node_id_culturel, node_id_etablissement)
                edge_labels[(node_id_culturel, node_id_etablissement)] = ''

                # Ajout d'un nœud pour la description si elle existe
                if 'owl:topObjectProperty' in objet and objet['owl:topObjectProperty']['shortDescription']['@value']:
                    node_id_description = node_id_counter
                    node_id_counter += 1
                    G_culturel.add_node(node_id_description, title="Description", text=objet['owl:topObjectProperty']['shortDescription']['@value'], balise="p")
                    node_labels[node_id_description] = "Description"
                    G_culturel.add_edge(node_id_etablissement, node_id_description)
                    edge_labels[(node_id_etablissement, node_id_description)] = ''

                # Ajout d'un nœud pour les coordonnées si elles sont disponibles
                if ('schema:geo' in objet['isLocatedAt'] and 'schema:latitude' in objet['isLocatedAt']['schema:geo'] and 'schema:longitude' in objet['isLocatedAt']['schema:geo']):
                    node_id_coord = node_id_counter
                    node_id_counter += 1
                    G_culturel.add_node(node_id_coord, title="Coordonnées", text=str(objet['isLocatedAt']['schema:geo']['schema:latitude']['@value']) + ", " + str(objet['isLocatedAt']['schema:geo']['schema:longitude']['@value']), balise="p")
                    node_labels[node_id_coord] = "Coordonnées"
                    G_culturel.add_edge(node_id_etablissement, node_id_coord)
                    edge_labels[(node_id_etablissement, node_id_coord)] = ''

        # Ajout des nœuds pour chaque établissement
        for objet in data:
            add_nodes()

        return G_economique, G_culturel, node_labels, edge_labels

    # Construction des graphes des établissements économiques et culturels
    G_economique, G_culturel, node_labels, edge_labels = build_graph_data_tourisme(etablissements_ville_recherchee)

    # Fusion des deux graphes pour obtenir un graphe unique
    G = nx.compose(G_economique, G_culturel)

    # Affichage des informations des nœuds et de leurs enfants
    def display_node_info(G, node, depth=0):
        # Récupération des informations du nœud
        info = G.nodes[node]

        # Formatage des informations pour l'affichage
        if info['balise'] in ['h3', 'h4']:
            node_info = info['title']
        elif info['balise'] == 'p':
            node_info = info['text'].strip()
        else:
            node_info = ""

        # Affichage des informations du nœud avec l'indentation appropriée
        print("  " * depth + node_info)

        # Parcours récursif des enfants du nœud actuel
        for child in G.successors(node):
            display_node_info(G, child, depth + 1)

    # Recherche de l'identifiant du nœud pour les établissements économiques
    for node_id in G.nodes():
        if node_labels[node_id] == "Tourisme et loisir":
            display_node_info(G, node_id)
            break

    print("")

    # Recherche de l'identifiant du nœud pour les établissements culturels
    for node_id in G.nodes():
        if node_labels[node_id] == "Patrimoine culturel":
            display_node_info(G, node_id)
            break

    # Visualisation du graphe des établissements économiques
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=1500, node_color='lightblue', font_size=10,
            font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    plt.title("Graphe des établissements économiques et culturels")
    plt.show()

# Si aucun établissement n'est trouvé pour la ville recherchée
else:
    print("Pas d'établissements touristiques pour la ville de " + ville)
