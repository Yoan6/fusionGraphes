import networkx as nx
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import pandas as pd


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

ville = 'Moirans'

# Filtrage des données pour la ville
ville_data = csv_file[csv_file['Libellé de la commune'] == ville]

# Crée un graphe dirigé
G = nx.DiGraph()

# Ajout des nœuds et des attributs au graphe
for _, row in ville_data.iterrows():
    # Nom complet de l'élu
    nom_prenom = row['Nom de l\'élu'] + ' ' + row['Prénom de l\'élu']
    # On retire les colonnes inutiles (prenom, nom et libellé de la commune)
    attributes = row.drop(['Nom de l\'élu', 'Prénom de l\'élu', 'Libellé de la commune'])
    # On crée un nœud pour l'élu avec ses attributs
    G.add_node(nom_prenom, **attributes)

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



