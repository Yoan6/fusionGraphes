import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import re
import html

# Nettoye le texte tout en conservant les caractères spéciaux tels que les accents
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
                if td and not td.find('div', {'id': 'img_toggle_0'}):  # Vérification de la structure spécifique
                    # Texte de la balise <td>
                    td_text = clean_text(td.get_text(separator=' ', strip=True))
                    # Ajouter les données à la section actuelle
                    current_section['children'].append(
                        {'title': th_text, 'text': td_text, 'balise': 'tr', 'children': []})
                # Sinon, la ligne contient un titre de section
                else:
                    # Vérifie si le texte de la balise <th> est un titre de section
                    if th_text in titles:
                        title = th_text
                        # Créer une nouvelle section
                        current_section = {'title': title, 'text': '', 'balise': 'title', 'children': []}
                        infobox_data.append(current_section)

        print("Infobox : ", infobox_data)

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
def build_graph(sections):
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
url_wikipedia = 'https://fr.wikipedia.org/wiki/Vourey'

# Extraction des sections récursivement à partir de l'URL donnée
sections = extract_sections_recursive(url_wikipedia)
# On enlève la première section qui est le sommaire et les deux dernières sections qui sont les références et les liens externes
sections = sections[1:-2]
print("Sections : ", sections)

# Construction du graphe des sections et sous-sections
G, node_labels, edge_labels = build_graph(sections)

# Affichage des nœuds et arêtes du graphe
print("Noeuds et arêtes du graphe:")
print("Noeuds:", G.nodes())
print("Arêtes:", G.edges())

# Fonction récursive pour afficher les sections avec leur texte
def display_sections_with_text(section, depth=0):
    indent = '    ' * depth
    # On affiche le titre de la section
    # Dans le cas des listes, on n'affiche pas le titre de la section et de ses enfants
    if section['balise'] != 'li' and section['balise'] != 'ul':
        print(indent + section['title'])
    else:
        # Si la section est une liste
        print(indent)

    # Afficher le texte associé à ce nœud principal
    if section['text']:
        # Si la section contient du texte
        text_lines = section['text'].strip().split('\n')
        for line in text_lines:
            # Si la section est une liste non ordonnée
            if (section['balise'] == 'li'):
                # Afficher la ligne avec un tiret (-) ajouté
                updated_line = '- ' + line.strip()
                print(indent + '    ' + updated_line)
            else:
                # Sinon, afficher la ligne normalement
                print(indent + '    ' + line.strip())

    # Parcourir les sous-sections récursivement
    for child in section['children']:
        display_sections_with_text(child, depth + 1)

# Appel de la fonction avec la racine de la structure des sections
for section in sections:
    # Afficher le texte associé au nœud principal avant de parcourir les sous-sections
    if section['text']:
        print(section['text'].strip())
    display_sections_with_text(section)

# Visualisation du graphe
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=1500, node_color='lightblue', font_size=10,
        font_weight='bold')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
plt.title('Graphe des sections et sous-sections de la page Wikipedia sur Riverie')
plt.show()
