import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import scipy as sp

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

        print("Infobox : ", infobox_data)

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
def build_graph(sections):
    # Initialisation du graphe dirigé
    G = nx.DiGraph()
    node_labels = {}
    edge_labels = {}

    # Compteur pour les identifiants des nœuds
    node_id_counter = 0

    # Structure de données pour stocker les informations détaillées de chaque nœud
    node_details = {}

    # Fonction récursive pour ajouter les nœuds au graphe
    def add_nodes(section, parent_node=None):
        nonlocal node_id_counter  # Utilisation de la variable externe node_id_counter

        # Récupération des informations de la section
        title = section['title']
        text = section['text']
        balise = section['balise']

        # Création de l'identifiant unique du nœud en utilisant le compteur
        node_id = node_id_counter
        node_id_counter += 1  # Incrémentation du compteur pour le prochain nœud

        # Ajout du nœud au graphe avec son identifiant unique
        G.add_node(node_id)

        # Ajout du titre du nœud dans le libellé pour l'affichage du graphe
        node_labels[node_id] = title

        # Ajout des informations détaillées dans la structure de données node_details
        node_details[node_id] = {
            'title': title,
            'text': text,
            'balise': balise
        }

        if parent_node is not None:
            G.add_edge(parent_node, node_id)
            edge_labels[(parent_node, node_id)] = ''  # Label vide pour l'arc

        # Parcours récursif des enfants du nœud actuel
        for child in section['children']:
            add_nodes(child, parent_node=node_id)

    # Appel initial de la fonction récursive avec la racine des sections
    add_nodes({'title': 'Root', 'text': '', 'balise': 'Root', 'children': sections})

    return G, node_labels, edge_labels, node_details



# URL de la page Wikipedia à traiter
url_wikipedia = 'https://fr.wikipedia.org/wiki/Riverie'

# Extraction des sections récursivement à partir de l'URL donnée
sections = extract_sections_recursive(url_wikipedia)
# On enlève la deuxième section qui est le sommaire et les deux dernières sections qui sont les références et les liens externes tout en gardant la première section qui est l'infobox
sections = sections[0:1] + sections[2:-2]
# On enlève les deux dernières sections qui sont les références et les liens externes
sections = sections[:-2]
print("Sections : ", sections)

# Construction du graphe des sections et sous-sections
G, node_labels, edge_labels, node_details = build_graph(sections)

# Affichage des nœuds et arêtes du graphe
print("Noeuds et arêtes du graphe:")
print("Noeuds:", G.nodes())
print("Arêtes:", G.edges())

def display_node_info(G, node_details, node, depth=0):
    # Récupère les informations du nœud
    info = node_details[node]

    # Crée une chaîne de caractères pour afficher les informations du nœud
    if info['balise'] == 'ul':
        # Ne rien afficher pour la balise 'ul'
        node_info = ""
    elif info['balise'] == 'li':
        # Affiche le texte avec un tiret pour la balise 'li'
        node_info = f"- {info['text'].strip()}"
    elif info['balise'] == 'p':
        # Affiche le texte pour la balise 'p'
        node_info = info['text'].strip()
    elif info['balise'] == 'tr':
        # Affiche le titre suivi du texte pour la balise 'tr'
        node_info = f"{info['title']}: {info['text'].strip()}"
    elif info['balise'] in ['h2', 'h3', 'h4', 'h5', 'h6', 'title']:
        # Affiche le titre pour les balises 'h*' et 'title'
        node_info = info['title']
    else:
        # Utilise le titre par défaut pour les autres balises
        node_info = f"Title: {info['title']}"

    # Affiche les informations du nœud avec l'indentation correspondante
    print("    " * depth + node_info)

    # Parcours des enfants du nœud
    for child in G.successors(node):
        # Appel récursif pour afficher les informations de chaque enfant avec une indentation supplémentaire
        display_node_info(G, node_details, child, depth + 1)

def display_graph_info(G, node_details):
    # Parcours des nœuds du graphe
    for node in G.nodes:
        # Si le nœud n'a pas de prédécesseurs, c'est la racine, on affiche son information et celle de ses enfants
        if not list(G.predecessors(node)):
            display_node_info(G, node_details, node)

display_graph_info(G, node_details)

# Visualisation du graphe
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=1500, node_color='lightblue', font_size=10,
        font_weight='bold')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
plt.title('Graphe des sections et sous-sections de la page Wikipedia sur Riverie')
plt.show()
