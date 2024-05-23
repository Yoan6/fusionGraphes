import networkx as nx
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import pandas as pd

ville = 'Cras'      # Ville pour laquelle on extraie les données
code_commune = '38137'      # Code de la commune

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
    download_link = download_a['href']
    # On charge le fichier CSV dans un DataFrame
    data = pd.read_csv(download_link, dtype=str, sep=';', encoding='utf-8')
    return data

# URL du site des élus à traiter
url_elus = 'https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/'

# Extraction des données du fichier CSV
csv_file = extract_csv(url_elus)

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

            # Ajout des attributs de l'élu comme des nœuds de balise 'tr' sous le nœud 'table'
            for k, v in row.items():
                attribute_node_id = node_id_counter
                node_id_counter += 1
                # Ajout d'un noeud pour chaque attribut de l'élu
                G.add_node(attribute_node_id, title=k, text=v, balise='tr')
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
            print("        " + G_elus.nodes[node_id]['title']), " : ", G_elus.nodes[node_id]['text']

    # Dessine le graphe
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G_elus, seed=42)  # Positionnement des nœuds
    nx.draw(G_elus, pos, with_labels=True, labels=node_labels, node_size=1500, node_color='skyblue', font_size=10, font_weight='bold')
    nx.draw_networkx_edge_labels(G_elus, pos, edge_labels=edge_labels, font_color='red')
    plt.title('Graphe des élus municipaux')
    plt.show()
else:
    print(f"Aucun élu municipal trouvé pour la ville de {ville}")
