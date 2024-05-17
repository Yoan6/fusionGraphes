import networkx as nx
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

ville = 'Villeconin'  # TODO: Change this to take into account the commune code

# Function to download and cache the CSV file locally
def download_csv(url, cache_path):
    if not os.path.exists(cache_path):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        header = soup.find('header', {'id': 'resource-d5f400de-ae3f-4966-8cb6-a85c70c6c24a-header'})
        download_a = header.find('a', {'class': 'fr-btn fr-btn--sm fr-icon-download-line matomo_download'})
        download_link = download_a['href']
        data = pd.read_csv(download_link, dtype=str, sep=';', encoding='utf-8')
        data.to_csv(cache_path, index=False, sep=';')
    else:
        data = pd.read_csv(cache_path, dtype=str, sep=';')
    return data

# URL and local cache path
url_elus = 'https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/'
cache_path = 'elus_municipaux.csv'

# Extract data from the CSV file
csv_file = download_csv(url_elus, cache_path)

# Filter data for the specified city
ville_data = csv_file[csv_file['Libellé de la commune'] == ville]

# Function to build the graph of municipal councilors
def build_graph(csv_data):
    global node_id_counter
    node_id_counter = 0  # Reset the node counter

    G = nx.DiGraph()
    node_labels = {}
    node_details = {}

    def add_node_with_attributes(parent_id, title, attributes):
        global node_id_counter
        node_id = node_id_counter
        node_id_counter += 1
        G.add_node(node_id)
        node_labels[node_id] = title
        node_details[node_id] = {
            'title': title,
            'attributes': attributes
        }
        G.add_edge(parent_id, node_id)
        return node_id

    elus_node_id = node_id_counter
    node_id_counter += 1
    G.add_node(elus_node_id)
    node_labels[elus_node_id] = 'Elus municipaux actuels'
    node_details[elus_node_id] = {
        'title': 'Elus municipaux actuels',
        'attributes': {}
    }

    for _, row in csv_data.iterrows():
        nom_prenom = row['Prénom de l\'élu'] + ' ' + row['Nom de l\'élu']
        attributes = {k: v for k, v in row.items()}
        add_node_with_attributes(elus_node_id, nom_prenom, attributes)

    return G, node_labels, node_details

# Build the graph of municipal councilors
G_elus, node_labels, node_details_elus = build_graph(ville_data)

# Print nodes and attributes of the graph from node_details
print("Noeuds et attributs:")
for node, details in node_details_elus.items():
    print(details['title'])
    for attr, value in details['attributes'].items():
        print(f"    {attr}: {value}")

# Draw the graph
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(G_elus, seed=42)
nx.draw(G_elus, pos, with_labels=True, labels=node_labels, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold')
plt.title('Graphe des élus municipaux de ' + ville)
plt.show()
