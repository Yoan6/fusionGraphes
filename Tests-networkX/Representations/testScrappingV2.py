import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt

# Fonction pour extraire les sections récursivement à partir d'une URL donnée
def extract_sections_recursive(url):
    # Récupération de la réponse HTTP
    response = requests.get(url)
    # Analyse du contenu HTML de la page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialisation du nœud racine
    root = {'title': 'Root', 'text': '', 'balise': 'Root', 'children': []}
    current_node = root
    parents = [root]

    # Parcours des balises h2, h3, h4, h5, h6 dans le code HTML de la page
    for tag in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
        # Récupération du niveau de la balise
        level = int(tag.name[1])
        # Récupération du titre de la section
        title = tag.text.strip().split('[')[0]

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
                current_node['text'] += current_tag.get_text().strip() + '\n'
            elif current_tag.name == 'ul':
                # Si la balise est une balise ul, on récupère le texte des balises li et on les ajoute au texte de la section
                current_node['text'] += '<ul>\n'
                current_node['text'] += '\n'.join(
                    [f'<li>{li.get_text().strip()}</li>' for li in current_tag.find_all('li')])
                current_node['text'] += '\n</ul>\n'
            # Passage à la balise suivante
            current_tag = current_tag.find_next_sibling()

    # Récupération du texte pour le nœud racine
    root['text'] = soup.find('body').get_text().strip()
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
        text = section['text']
        node = len(G.nodes)
        G.add_node(node)

        # Ajout du texte du nœud principal dans le libellé du nœud
        node_labels[node] = title + '\n' + text

        if parent_node is not None:
            G.add_edge(parent_node, node)
            edge_labels[(parent_node, node)] = ''  # Label vide pour l'arc

        for child in section['children']:
            add_nodes(child, parent_node=node)

    # Appel initial de la fonction récursive avec la racine des sections
    add_nodes({'title': 'Root', 'text': '', 'balise': 'Root', 'children': sections})

    return G, node_labels, edge_labels

# URL de la page Wikipedia à traiter
url_wikipedia = 'https://fr.wikipedia.org/wiki/Riverie'

# Extraction des sections récursivement à partir de l'URL donnée
sections = extract_sections_recursive(url_wikipedia)
# On enlève la première section qui est le sommaire et les deux dernières sections qui sont les références et les liens externes
sections = sections[1:-2]

# Construction du graphe des sections et sous-sections
G, node_labels, edge_labels = build_graph(sections)

# Affichage des nœuds et arêtes du graphe
print("Noeuds et arêtes du graphe:")
print("Noeuds:", G.nodes())
print("Arêtes:", G.edges())

# Fonction récursive pour afficher les sections avec leur texte
def display_sections_with_text(section, depth=0):
    indent = '    ' * depth
    print(indent + section['title'])

    # Afficher le texte associé à ce nœud principal
    if section['text']:
        # Si la balise <ul> est présente dans le texte de la section
        if '<ul>' in section['text']:
            text_lines = section['text'].strip().split('\n')
            for line in text_lines:
                # Si la ligne commence par '<li>'
                if line.strip().startswith('<li>'):
                    # Remplacer '<li>' par '- ' et retirer '</li>'
                    updated_line = '- ' + line.strip().lstrip('<li>').rstrip('</li>')
                    print(indent + '    ' + updated_line)
                # Si la ligne commence par '<p>'
                elif line.strip().startswith('<p>'):
                    # Retirer '<p>' et '</p>'
                    updated_line = line.strip().lstrip('<p>').rstrip('</p>')
                    print(indent + '    ' + updated_line)
                # Si la ligne est une balise <ul> ou </ul>, ne rien afficher
                elif line.strip().startswith('<ul>') or line.strip().startswith('</ul>'):
                    pass
                else:
                    print(indent + '    ' + line.strip())
        else:
            print(indent + '    ' + section['text'].strip())

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
plt.title('Graphe des sections et sous-sections de la page Wikipedia sur Vourey')
plt.show()
