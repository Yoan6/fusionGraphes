import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt

# Ville
ville = "Cras"
departement = "Isère"

# Initialisation du compteur de nœuds
node_id_counter = 0

# Fonction pour nettoyer le texte en remplaçant les espaces insécables par des espaces normaux
def clean_text(text):
    return text.replace('\xa0', ' ')

# Fonction pour supprimer les balises <sup> d'un élément BeautifulSoup
def remove_sup_tags(soup):
    for sup in soup.find_all('sup'):
        sup.decompose()
    return soup

# Extraction des données du site de Wikipedia
def extract_wikipedia(url):
   response = requests.get(url)
   # Analyse du contenu HTML de la page
   soup = BeautifulSoup(response.text, 'html.parser')
   return soup

# Fonction pour extraire les sections à partir d'une URL donnée
def extract_sections(soup):
    # Suppression des balises <sup>
    soup = remove_sup_tags(soup)

    # Extraction du titre de la page à partir de la balise <h1>
    page_title = soup.find('h1').text.strip()

    # Initialisation du nœud racine avec le titre de la page
    root = {'title': page_title, 'text': '', 'balise': 'h1', 'children': []}
    parents = [root]

    # Création de la section pour l'infobox
    infobox_section = {'title': 'Infobox', 'text': '', 'balise': 'h2', 'children': []}
    # On ajoute une section pour l'infobox de la page
    infobox = soup.find('table', {'class': 'infobox_v2'})
    if (infobox):
        infobox_section['children'] = extract_infobox_data(infobox)
    # Ajout de la section de l'infobox à la racine
    root['children'].append(infobox_section)

    # Parcours des balises h2, h3, h4, h5, h6 dans le code HTML de la page
    for tag in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
        # Appel de la fonction pour traiter chaque section
        process_section(tag, parents)
    return root

# Fonction pour extraire les données de l'infobox
def extract_infobox_data(infobox):
    infobox_data = []
    current_section = None
    # Liste des titres des sections de l'infobox
    titles = {"Administration", "Démographie", "Géographie", "Élections", "Liens"}

    # Parcourir les lignes de l'infobox
    for row in infobox.find_all('tr'):
        # Vérifier si la ligne contient une balise <th>
        th = row.find('th')
        if (th):
            th_text = clean_text(th.get_text(separator=' ', strip=True))
            # Si la ligne contient une balise <td>, c'est une donnée de titre
            td = row.find('td')
            if (td and not td.find('div', {'id': 'img_toggle_0'})):  # Ignorer la partie sur la localisation
                td_text = clean_text(td.get_text(separator=' ', strip=True))
                # Ajoute les données à la section actuelle
                current_section['children'].append({'title': th_text, 'text': td_text, 'balise': 'tr', 'children': []})
            elif (th_text in titles):
                # Crée une nouvelle section pour le titre
                current_section = {'title': th_text, 'text': '', 'balise': 'table', 'children': []}
                infobox_data.append(current_section)
    return infobox_data

# Fonction pour traiter une section
def process_section(tag, parents):
    # Récupération du niveau de la balise
    level = int(tag.name[1])
    # Récupération du titre de la section
    title = clean_text(tag.text.strip().split('[')[0])

    # Déplacement dans la hiérarchie des sections si un niveau inférieur est rencontré
    while len(parents) >= level:
        parents.pop()

    # Création d'un nouveau nœud pour la section avec la balise associée
    new_node = {'title': title, 'text': '', 'balise': tag.name, 'children': []}
    # Ajout du nouveau nœud comme enfant du parent approprié
    parents[-1]['children'].append(new_node)
    parents.append(new_node)

    # Récupération du texte directement sous la balise h*
    current_tag = tag.find_next_sibling()
    while current_tag and current_tag.name not in ['h2', 'h3', 'h4', 'h5', 'h6']:
        if current_tag.name == 'p':
            # Création d'un nouveau nœud pour chaque balise <p>
            new_node['children'].append({'title': 'Paragraph', 'text': clean_text(current_tag.get_text().strip()), 'balise': 'p', 'children': []})
        elif current_tag.name == 'ul':
            # Création d'un nouveau nœud pour la balise <ul> et ses <li>
            ul_node = {'title': 'Unordered List', 'text': '', 'balise': 'ul', 'children': [{'title': 'List Item', 'text': clean_text(li.get_text().strip()), 'balise': 'li', 'children': []} for li in current_tag.find_all('li')]}
            new_node['children'].append(ul_node)
        current_tag = current_tag.find_next_sibling()

# Fonction pour construire le graphe des sections et sous-sections
def build_graph(sections):
    global node_id_counter  # Utilisation de la variable globale node_id_counter
    # Initialisation du graphe dirigé
    G = nx.DiGraph()
    node_labels, edge_labels = {}, {}

    # Fonction récursive pour ajouter les nœuds au graphe
    def add_nodes(section, parent_node=None):
        global node_id_counter  # Utilisation de la variable globale node_id_counter
        # Création de l'identifiant unique du nœud en utilisant le compteur
        node_id = node_id_counter
        node_id_counter += 1
        # Ajout du nœud au graphe avec son identifiant unique et les détails comme attributs
        G.add_node(node_id, title=section['title'], text=section['text'], balise=section['balise'])
        # Ajout du titre du nœud dans le libellé pour l'affichage du graphe
        node_labels[node_id] = section['title']

        if parent_node is not None:
            G.add_edge(parent_node, node_id)
            edge_labels[(parent_node, node_id)] = ''  # Label vide pour l'arc

        # Parcours récursif des enfants du nœud actuel
        for child in section['children']:
            add_nodes(child, parent_node=node_id)

    # Appel initial de la fonction récursive avec la racine des sections
    add_nodes(sections)
    return G, node_labels, edge_labels

# Si la ville a un nom composé avec des espaces, on les remplace par des underscores pour l'URL
ville = ville.replace(' ', '_')

# URL de la page Wikipedia à traiter
url_wikipedia = 'https://fr.wikipedia.org/wiki/' + ville
url_wikipedia_homonyme = 'https://fr.wikipedia.org/wiki/' + ville + '_(' + departement + ')'

# Fonction pour vérifier si une page Wikipedia contient des communes homonymes
def is_an_homonym(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Si la deuxième balise h2 est 'Toponyme' en enlevant toute la partie [modifier le code], alors la page contient des toponymes
    h2_tags = soup.find_all('h2')
    # Si la page ne contient pas de balises h2, c'est qu'il n'y a pas d'homonymes
    if len(h2_tags) == 0:
        return True
    h2_tag = h2_tags[1]
    # Si la deuxième balise h2 n'est pas 'Géographie', alors la page contient des homonymes
    return 'Géographie' not in h2_tag.text.split('[')[0]

if is_an_homonym(url_wikipedia):
    url_wikipedia = url_wikipedia_homonyme

# Extraction des données de la page Wikipedia
soup = extract_wikipedia(url_wikipedia)

# Extraction des sections récursivement à partir de l'URL donnée
sections = extract_sections(soup)

if len(sections['children']) > 1:
    # On enlève la deuxième section qui est le sommaire et les deux dernières sections qui sont les références et les liens externes tout en gardant la première section qui est l'infobox
    sections['children'] = sections['children'][0:1] + sections['children'][2:-2]

    # Construction du graphe des sections et sous-sections
    G, node_labels, edge_labels = build_graph(sections)

    print("Noeuds et arêtes du graphe:")
    print("Noeuds:", G.nodes(data=True))  # Affiche les nœuds avec leurs attributs
    print("Arêtes:", G.edges())

    # Fonction pour afficher les informations d'un nœud et de ses enfants
    def display_node_info(G, node, depth=0):
        # Récupère les informations du nœud
        info = G.nodes[node]
        # Crée une chaîne de caractères pour afficher les informations du nœud
        if (info['balise'] == 'ul'):
            node_info = ""
        elif (info['balise'] == 'li'):
            node_info = f"- {info['text'].strip()}"
        elif (info['balise'] == 'p'):
            node_info = info['text'].strip()
        elif (info['balise'] == 'tr'):
            node_info = f"{info['title']}: {info['text'].strip()}"
        else:
            node_info = info['title']
        # Affiche les informations du nœud avec l'indentation correspondante
        print("    " * depth + node_info)
        # Parcours des enfants du nœud
        for child in G.successors(node):
            display_node_info(G, child, depth + 1)

    # Affichage des informations des nœuds et de leurs enfants
    display_node_info(G, 0)

    # Visualisation du graphe
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=1500, node_color='lightblue', font_size=10,
            font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    plt.title(f'Graphe des sections et sous-sections de la page Wikipedia sur {ville}')
    plt.show()
else:
    print(f"Aucune section trouvée pour la page Wikipedia de {ville}")
