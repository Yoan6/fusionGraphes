import networkx as nx
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import pandas as pd

ville = 'Mens'  # Ville pour laquelle on extraie les données
code_commune = '38226'  # Code de la commune
lastUpdate = ''  # Date de la dernière mise à jour

# Compteur pour les identifiants des nœuds
node_id_counter = 0


# Récupère les données du fichier CSV des élus municipaux
def extract_csv(url):
    # Récupération de la réponse HTTP
    response = requests.get(url)
    # Analyse du contenu HTML de la page
    soup = BeautifulSoup(response.content, 'html.parser')

    # On regarde le header avec l'id : 'resource-d5f400de-ae3f-4966-8cb6-a85c70c6c24a-header'
    header = soup.find('header', {'id': 'resource-d5f400de-ae3f-4966-8cb6-a85c70c6c24a-header'})
    # On récupère le lien de téléchargement du fichier CSV des élus municipaux
    download_a = header.find('a', {'class': 'fr-btn fr-btn--sm fr-icon-download-line matomo_download'})
    # On récupère la date de la dernière mise à jour (commence par Mis à jour le)
    lastUpdate = header.find('p', {'class': 'fr-text--xs fr-m-0 dash-after'}).text
    download_link = download_a['href']
    # On charge le fichier CSV dans un DataFrame
    data = pd.read_csv(download_link, dtype=str, sep=';', encoding='utf-8')
    return data, lastUpdate


# URL du site des élus à traiter
url_elus = 'https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/'

# Extraction des données du fichier CSV
csv_file, lastUpdate = extract_csv(url_elus)

# On récupère seulement la date de la dernière mise à jour
lastUpdate = lastUpdate.replace('Mis à jour le ', '')

# On met en majuscule la première lettre de chaque mot
ville = ville.title()

# Si le code de la commune commence par 0, on le retire
if code_commune.startswith('0'):
    code_commune = code_commune[1:]

# Filtrage des données pour la ville en fonction du nom de la ville et du code de la commune
ville_data = csv_file[(csv_file['Libellé de la commune'] == ville) & (csv_file['Code de la commune'] == code_commune)]

if len(ville_data) != 0:
    # Fonction pour construire le graphe des élus municipaux
    def build_graph(csv_data):
        # Compteur pour les identifiants des nœuds
        global node_id_counter  # Utilisation de la variable externe node_id_counter

        # Initialisation du graphe dirigé
        G = nx.DiGraph()
        node_labels = {}
        edge_labels = {}

        def add_nodes():
            # Compteur pour les identifiants des nœuds
            global node_id_counter  # Utilisation de la variable externe node_id_counter

            # Nom complet de l'élu
            nom_prenom = row['Nom de l\'élu'] + ' ' + row['Prénom de l\'élu']

            # Création de l'identifiant unique du nœud en utilisant le compteur
            node_id = node_id_counter
            node_id_counter += 1  # Incrémentation du compteur pour le prochain nœud

            # Ajout du nœud pour l'élu sous forme de balise 'table'
            G.add_node(node_id, title=nom_prenom, text='', balise='table')

            # Ajout du titre du nœud dans le libellé pour l'affichage du graphe
            node_labels[node_id] = nom_prenom

            # Ajout des nœuds pour "Nom de l'élu" et "Prénom de l'élu" en premier
            for key in ['Nom de l\'élu', 'Prénom de l\'élu']:
                value = row[key]
                if pd.notna(value):
                    attribute_node_id = node_id_counter
                    node_id_counter += 1
                    # Ajout d'un noeud pour chaque attribut de l'élu
                    G.add_node(attribute_node_id, title=key, text=str(value), balise='tr')
                    # Ajout du libellé du nœud pour l'affichage du graphe
                    node_labels[attribute_node_id] = f"{key}: {value}"
                    # Ajout d'un lien du nœud 'table' vers le nœud 'tr'
                    G.add_edge(node_id, attribute_node_id)

            # Ajout des autres attributs de l'élu comme des nœuds de balise 'tr' sous le nœud 'table'
            for k, v in row.items():
                # S'il y a une valeur qui n'est pas NaN et que ce n'est ni 'Nom de l\'élu' ni 'Prénom de l\'élu', on l'ajoute
                if pd.notna(v) and k not in ['Nom de l\'élu', 'Prénom de l\'élu']:
                    attribute_node_id = node_id_counter
                    node_id_counter += 1
                    # Ajout d'un noeud pour chaque attribut de l'élu
                    G.add_node(attribute_node_id, title=k, text=str(v), balise='tr')
                    # Ajout du libellé du nœud pour l'affichage du graphe
                    node_labels[attribute_node_id] = f"{k}: {v}"
                    # Ajout d'un lien du nœud 'table' vers le nœud 'tr'
                    G.add_edge(node_id, attribute_node_id)

            # Ajoute un lien du nœud principal 'Elus municipaux' vers le nœud 'table' de l'élu
            G.add_edge(elus_node_id, node_id)

        # Création du nœud principal 'Elus municipaux'
        elus_node_id = node_id_counter
        node_id_counter += 1
        G.add_node(elus_node_id, title='Elus municipaux', text='', balise='h3')
        node_labels[elus_node_id] = 'Elus municipaux'

        # Ajout de la date de la dernière mise à jour
        lastUpdate_node_id = node_id_counter
        node_id_counter += 1
        G.add_node(lastUpdate_node_id, title='Dernière modif élus', text=lastUpdate, balise='p')
        node_labels[lastUpdate_node_id] = 'Dernière modif élus'
        G.add_edge(elus_node_id, lastUpdate_node_id)

        # Ajout des nœuds et des attributs au graphe
        for _, row in csv_data.iterrows():
            add_nodes()

        return G, node_labels, edge_labels


    # Construction du graphe des élus municipaux
    G_elus, node_labels, edge_labels = build_graph(ville_data)

    # Affiche les nœuds et les attributs du graphe
    print("Noeuds et attributs:")
    for node_id in G_elus.nodes():
        # Si c'est un nœud de type 'table', afficher le titre
        if G_elus.nodes[node_id]['balise'] == 'table':
            print(G_elus.nodes[node_id]['title'])
        else:
            print("        " + G_elus.nodes[node_id]['title'] + " : " + G_elus.nodes[node_id]['text'])

    # Dessine le graphe
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G_elus, seed=42)  # Positionnement des nœuds
    nx.draw(G_elus, pos, with_labels=True, labels=node_labels, node_size=1500, node_color='skyblue', font_size=10,
            font_weight='bold')
    nx.draw_networkx_edge_labels(G_elus, pos, edge_labels=edge_labels, font_color='red')
    plt.title('Graphe des élus municipaux')
    plt.show()
else:
    print(f"Aucun élu municipal trouvé pour la ville de {ville}")
