import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

ville = 'Riverie'

#===============================================1er graphe===================================================

# Récupère les données du fichier CSV des élus municipaux
def extract_csv_elu(url):
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
csv_file = extract_csv_elu(url_elus)

# Filtrage des données pour la ville
ville_data = csv_file[csv_file['Libellé de la commune'] == ville]

# Crée un graphe dirigé
G_elu = nx.DiGraph()

# Ajout des nœuds et des attributs au graphe
for _, row in ville_data.iterrows():
    # Nom complet de l'élu
    nom_prenom = row['Nom de l\'élu'] + ' ' + row['Prénom de l\'élu']
    # On retire les colonnes inutiles (prenom, nom et libellé de la commune)
    attributes = row.drop(['Nom de l\'élu', 'Prénom de l\'élu', 'Libellé de la commune'])
    # On crée un nœud pour l'élu avec ses attributs
    G_elu.add_node(nom_prenom, **attributes)


#===============================================2ème graphe===================================================

# Nettoie le texte tout en conservant les caractères spéciaux tels que les accents
def clean_text(text):
    # Remplace les espaces insécables par des espaces normaux
    texte_propre = text.replace('\xa0', ' ')
    return texte_propre

# Extrait les sections récursivement à partir d'une URL donnée
def extract_sections_recursive(url):
    # Récupération de la réponse HTTP
    response = requests.get(url)
    # Analyse du contenu HTML de la page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialisation du nœud racine
    root = {'title': 'Root', 'text': '', 'balise': 'Root', 'children': []}
    current_node = root
    parents = [root]

    # Création de la section pour l'infobox
    infobox_section = {'title': 'Infobox', 'text': '', 'balise': 'h2', 'children': []}

    # On ajoute une section pour l'infobox de la page
    infobox = soup.find('table', {'class': 'infobox_v2'})
    if infobox:
        # Création d'une nouvelle section pour l'infobox
        infobox_data = []

        current_section = None  # Garde une trace de la section actuelle

        # Liste des titres des sections de l'infobox
        titles = {"Administration", "Démographie", "Géographie", "Élections", "Liens"}

        # Parcourir les lignes de l'infobox
        for row in infobox.find_all('tr'):
            # Vérifier si la ligne contient une balise <th>
            th = row.find('th')
            if th:
                th_text = clean_text(th.get_text(separator=' ', strip=True))
                # Si la ligne contient une balise <td>, c'est une donnée de titre
                td = row.find('td')
                if td and not td.find('div', {'id': 'img_toggle_0'}):  # Permet de ne pas prendre en compte la partie sur la localisation car trop compliqué d'interpréter les données
                    # Texte de la balise <td>
                    td_text = clean_text(td.get_text(separator=' ', strip=True))
                    # Ajoute les données à la section actuelle
                    current_section['children'].append(
                        {'title': th_text, 'text': td_text, 'balise': 'tr', 'children': []})
                else:
                    # Vérifie si le texte de la balise <th> est un titre de section
                    if th_text in titles:
                        title = th_text
                        # Crée une nouvelle section pour le titre
                        current_section = {'title': title, 'text': '', 'balise': 'title', 'children': []}
                        infobox_data.append(current_section)

        # Ajout des données de l'infobox à la section de l'infobox
        infobox_section['children'] = infobox_data

    # Ajout de la section de l'infobox à la racine
    root['children'].append(infobox_section)

    # Parcours des balises h2, h3, h4, h5, h6 dans le code HTML de la page
    for tag in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
        # Récupération du niveau de la balise
        level = int(tag.name[1])
        # Récupération du titre de la section
        title = clean_text(tag.text.strip().split('[')[0])

        # Déplacement dans la hiérarchie des sections si un niveau inférieur est rencontré
        while len(parents) >= level:
            parents.pop()

        # Création d'un nouveau nœud pour la section avec la balise associée
        new_node = {'title': title, 'text': '', 'balise': tag.name, 'children': []}
        # Ajout du nouveau nœud comme enfant du parent approprié si le nombre de noeuds parents est égal à la balise h* - 1
        if len(parents) == level - 1:
            parents[-1]['children'].append(new_node)

        # Mise à jour du nœud courant et des parents
        current_node = new_node
        parents.append(current_node)

        # Récupération du texte directement sous la balise h*
        current_tag = tag.find_next_sibling()
        while current_tag and current_tag.name not in ['h2', 'h3', 'h4', 'h5', 'h6']:
            if current_tag.name == 'p':
                # Création d'un nouveau nœud pour chaque balise <p>
                p_node = {'title': 'Paragraph', 'text': clean_text(current_tag.get_text().strip()), 'balise': 'p', 'children': []}
                current_node['children'].append(p_node)
            elif current_tag.name == 'ul':
                # Création d'un nouveau nœud pour la balise <ul>
                ul_node = {'title': 'Unordered List', 'text': '', 'balise': 'ul', 'children': []}
                current_node['children'].append(ul_node)
                # Parcours des balises <li> dans la balise <ul>
                for li_tag in current_tag.find_all('li'):
                    # Création d'un nouveau nœud pour chaque balise <li>
                    li_node = {'title': 'List Item', 'text': clean_text(li_tag.get_text().strip()), 'balise': 'li', 'children': []}
                    ul_node['children'].append(li_node)
            # Passage à la balise suivante
            current_tag = current_tag.find_next_sibling()

    return root['children']


# Fonction pour construire le graphe des sections et sous-sections
def build_graph_wiki(sections):
    # Initialisation du graphe dirigé
    G = nx.DiGraph()
    node_labels = {}
    edge_labels = {}

    # Fonction récursive pour ajouter les nœuds au graphe
    def add_nodes(section, parent_node=None):
        title = section['title']
        node = len(G.nodes)
        G.add_node(node)

        # Ajout du texte du nœud principal dans le libellé du nœud
        node_labels[node] = title

        if parent_node is not None:
            G.add_edge(parent_node, node)
            edge_labels[(parent_node, node)] = ''  # Label vide pour l'arc

        for child in section['children']:
            add_nodes(child, parent_node=node)

    # Appel initial de la fonction récursive avec la racine des sections
    add_nodes({'title': 'Root', 'text': '', 'balise': 'Root', 'children': sections})

    return G, node_labels, edge_labels

# URL de la page Wikipedia à traiter
url_wikipedia = 'https://fr.wikipedia.org/wiki/' + ville

# Extraction des sections récursivement à partir de l'URL donnée
sections = extract_sections_recursive(url_wikipedia)
# On enlève la deuxième section qui est le sommaire et les deux dernières sections qui sont les références et les liens externes tout en gardant la première section qui est l'infobox
sections = sections[0:1] + sections[2:-2]
# On enlève les deux dernières sections qui sont les références et les liens externes
sections = sections[:-2]

# Construction du graphe des sections et sous-sections
G_wiki, node_labels, edge_labels = build_graph_wiki(sections)


#===============================================Fusion des deux graphes===================================================


# Fusion des deux graphes
G = nx.compose(G_elu, G_wiki)

# Visualisation des données du graphe
def display_node_data(node, graph, node_labels):
    # Vérifie si le nœud a du texte
    if 'text' in node_labels[node]:
        print(node_labels[node]['text'])

    # Parcours des enfants du nœud
    for child in graph.successors(node):
        # Affichage des données du nœud enfant
        display_node_data(child, graph, node_labels)

# Appel initial pour afficher les données de chaque nœud
for node in G.nodes:
    print("Node:", node)
    display_node_data(node, G, node_labels)
    print("============")



# Visualisation du graphe
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=1500, node_color='lightblue', font_size=10,
        font_weight='bold')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
plt.title('Graphe des élus municipaux et des sections Wikipedia de Moirans')
plt.show()
