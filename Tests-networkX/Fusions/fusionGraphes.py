import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

ville = 'Moirans'

# Compteur pour les identifiants des nœuds
node_id_counter = 0

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

# Fonction pour construire le graphe des élus municipaux
def build_graph_elus(csv_data):
    # Compteur pour les identifiants des nœuds
    global node_id_counter  # Utilisation de la variable externe node_id_counter

    # Initialisation du graphe dirigé
    G_elu = nx.DiGraph()
    node_labels = {}
    edge_labels = {}
    node_details = {}  # Structure de données pour stocker les informations détaillées de chaque nœud

    def add_nodes():
        # Compteur pour les identifiants des nœuds
        global node_id_counter  # Utilisation de la variable externe node_id_counter

        # Nom complet de l'élu
        nom_prenom = row['Nom de l\'élu'] + ' ' + row['Prénom de l\'élu']

        # Création de l'identifiant unique du nœud en utilisant le compteur
        node_id = node_id_counter
        node_id_counter += 1  # Incrémentation du compteur pour le prochain nœud

        # Ajout du nœud au graphe avec son identifiant unique
        G_elu.add_node(node_id)

        # Ajout du titre du nœud dans le libellé pour l'affichage du graphe
        node_labels[node_id] = nom_prenom

        # Ajout des informations détaillées dans la structure de données node_details
        node_details[node_id] = {
            'title': nom_prenom,
            'text': '',
            'balise': 'table'
        }

        # Ajout des attributs de l'élu comme des nœuds de balise 'tr' sous le nœud 'table'
        for k, v in row.items():
            # On transforme le texte des noeud en chaine de caractère pour permettre plus tard d'utiliser la fonction strip()
            v = str(v)
            attribute_node_id = node_id_counter
            node_id_counter += 1
            # Ajout d'un noeud pour chaque attribut de l'élu
            G_elu.add_node(attribute_node_id)
            # Ajout du libellé du nœud pour l'affichage du graphe
            node_labels[attribute_node_id] = f"{k}: {v}"
            # Ajout d'un lien du nœud 'title' vers le nœud 'tr'
            G_elu.add_edge(node_id, attribute_node_id)
            node_details[attribute_node_id] = {
                'title': k,
                'text': v,
                'balise': 'tr'
            }
        # Ajoute un lien du nœud principal 'Elus municipaux' vers le nœud de l'élu
        G_elu.add_edge(elus_node_id, node_id)

    # Création du nœud principal 'Elus municipaux'
    elus_node_id = node_id_counter
    node_id_counter += 1
    G_elu.add_node(elus_node_id)
    node_labels[elus_node_id] = 'Elus municipaux'
    node_details[elus_node_id] = {
        'title': 'Elus municipaux',
        'text': '',
        'balise': 'h3'
    }

    # Ajout des nœuds et des attributs au graphe
    for _, row in csv_data.iterrows():
        add_nodes()

    return G_elu, node_labels, edge_labels, node_details

# Construction du graphe des élus municipaux
G_elu, node_labels, edge_labels, node_details = build_graph_elus(ville_data)


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
                        current_section = {'title': title, 'text': '', 'balise': 'table', 'children': []}
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

    # Fonction récursive pour ajouter les nœuds au graphe
    def add_nodes(section, parent_node=None):
        global node_id_counter  # Utilisation de la variable externe node_id_counter

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
url_wikipedia = 'https://fr.wikipedia.org/wiki/' + ville

# Extraction des sections récursivement à partir de l'URL donnée
sections = extract_sections_recursive(url_wikipedia)
# On enlève la deuxième section qui est le sommaire et les deux dernières sections qui sont les références et les liens externes tout en gardant la première section qui est l'infobox
sections = sections[0:1] + sections[2:-2]

# Construction du graphe des sections et sous-sections
G_wiki, node_labels, edge_labels, node_details = build_graph_wiki(sections)

print("Node labels:", node_labels)


#===============================================3ème graphe===================================================

def extract_dataTourisme(url):
    # Télécharge le fichier JSON-LD depuis l'URL
    response = requests.get(url)
    data = response.json()
    return data

# URL pour télécharger le fichier JSON-LD
url = "https://diffuseur.datatourisme.fr/webservice/f4f07d2f40c98b4eb046da28af2e651c/031aee5f-9dd7-4196-a677-610abe8fda77"  # Clé API : 031aee5f-9dd7-4196-a677-610abe8fda77

# Extraction des données du fichier JSON-LD
data = extract_dataTourisme(url)

# Fonction pour filtrer les données pour la ville
def filter_dataTourisme(data, ville):
    etablissements_ville_recherchee = []
    # Parcourt chaque objet dans le fichier JSON-LD
    for objet in data['@graph']:
        if 'isLocatedAt' in objet and 'schema:address' in objet['isLocatedAt'] and 'schema:addressLocality' in \
                objet['isLocatedAt']['schema:address']:
            ville_etablissement = objet['isLocatedAt']['schema:address']['schema:addressLocality']      # TODO A changer pour prendre en compte le code de la commune : objet['isLocatedAt']['schema:address']['hasAddressCity']['@id'][3:]
            if ville == ville_etablissement:
                etablissements_ville_recherchee.append(objet)
    return etablissements_ville_recherchee

# Filtrage des données pour la ville
etablissements_ville_recherchee = filter_dataTourisme(data, ville)

# Fonction pour construire le graphe des établissements touristiques
def build_graph_datatourisme(data):
    global node_id_counter  # Utilisation de la variable externe node_id_counter

    # Initialisation de deux graphe dirigé, un pour les établissements économiques et un pour les établissements culturels
    G_culturel = nx.DiGraph()
    G_economique = nx.DiGraph()

    # Création de l'identifiant unique du nœud en utilisant le compteur
    node_id_economie = node_id_counter
    node_id_counter += 1

    # Ajout du premier noeud pour les établissements économiques
    G_economique.add_node(node_id_economie)
    node_labels[node_id_economie] = "Tourisme et loisir"
    node_details[node_id_economie] = {
        'title': "Tourisme et loisir",
        'texte': "",
        'balise': "h3"
    }

    node_id_culturel = node_id_counter
    node_id_counter += 1

    # Ajout du premier noeud pour les établissements culturels
    G_culturel.add_node(node_id_culturel)
    node_labels[node_id_culturel] = "Patrimoine culturel"
    node_details[node_id_culturel] = {
        'title': "Patrimoine culturel",
        'texte': "",
        'balise': "h3"
    }

    def add_nodes():
        global node_id_counter

        title = objet['rdfs:label']['@value']
        # Description de l'établissement si elle existe sinon chaine vide
        text = objet['owl:topObjectProperty']['shortDescription']['@value'] if 'owl:topObjectProperty' in objet else ""

        # Création de l'identifiant unique du nœud en utilisant le compteur
        node_id_etablissement = node_id_counter
        node_id_counter += 1

        # Si l'établissement est économique on l'ajoute au graphe économique
        if ('schema:FoodEstablishment' or 'schema:LocalBusiness' or 'schema:Hotel' or 'schema:LodgingBusiness' or 'schema:Accommodation' or 'schema:TouristInformationCenter' or 'schema:Winery' or 'schema:Restaurant' or 'schema:Product') in objet['@type']:
            G_economique.add_node(node_id_etablissement)
            node_labels[node_id_etablissement] = title
            node_details[node_id_etablissement] = {
                'title': title,
                'text': "",
                'balise': "h4"
            }

            # On lie l'établissement au noeud économie
            G_economique.add_edge(node_id_economie, node_id_etablissement)
            edge_labels[(node_id_economie, node_id_etablissement)] = ''

            # On crée un noeud pour la description de l'établissement si elle existe
            if 'owl:topObjectProperty' in objet and objet['owl:topObjectProperty']['shortDescription']['@value']:
                node_id_description = node_id_counter
                node_id_counter += 1

                G_economique.add_node(node_id_description)
                node_labels[node_id_description] = "Description"
                node_details[node_id_description] = {
                    'title': "Description",
                    'text': objet['owl:topObjectProperty']['shortDescription']['@value'],
                    'balise': "p"
                }

                # On lie la description à l'établissement
                G_economique.add_edge(node_id_etablissement, node_id_description)
                edge_labels[(node_id_etablissement, node_id_description)] = ''


            # On crée un noeud pour les coordonnées de l'établissement si les coordonnées sont disponibles
            if ('schema:geo' in objet['isLocatedAt'] and 'schema:latitude' in objet['isLocatedAt']['schema:geo'] and 'schema:longitude' in objet['isLocatedAt']['schema:geo']):
                node_id_coord = node_id_counter
                node_id_counter += 1

                G_economique.add_node(node_id_coord)
                node_labels[node_id_coord] = "Coordonnées"
                node_details[node_id_coord] = {
                    'title': "Coordonnées",
                    'text': str(objet['isLocatedAt']['schema:geo']['schema:latitude']['@value']) + ", " + str(objet['isLocatedAt']['schema:geo']['schema:longitude']['@value']),
                    'balise': "p"
                }

                # On lie les coordonnées à l'établissement
                G_economique.add_edge(node_id_etablissement, node_id_coord)
                edge_labels[(node_id_etablissement, node_id_coord)] = ''

        # Si l'établissement est culturel on l'ajoute au graphe culturel
        else:
            G_culturel.add_node(node_id_etablissement)
            node_labels[node_id_etablissement] = title
            node_details[node_id_etablissement] = {
                'title': title,
                'text': "",
                'balise': "h4"
            }

            # On lie l'établissement au noeud culturel
            G_culturel.add_edge(node_id_culturel, node_id_etablissement)
            edge_labels[(node_id_culturel, node_id_etablissement)] = ''

            # On crée un noeud pour la description de l'établissement si elle existe
            if 'owl:topObjectProperty' in objet and objet['owl:topObjectProperty']['shortDescription']['@value']:
                node_id_description = node_id_counter
                node_id_counter += 1

                G_culturel.add_node(node_id_description)
                node_labels[node_id_description] = "Description"
                node_details[node_id_description] = {
                    'title': "Description",
                    'text': objet['owl:topObjectProperty']['shortDescription']['@value'],
                    'balise': "p"
                }

                # On lie la description à l'établissement
                G_culturel.add_edge(node_id_etablissement, node_id_description)
                edge_labels[(node_id_etablissement, node_id_description)] = ''

            # On crée un noeud pour les coordonnées de l'établissement si les coordonnées sont disponibles
            if ('schema:geo' in objet['isLocatedAt'] and 'schema:latitude' in objet['isLocatedAt']['schema:geo'] and 'schema:longitude' in objet['isLocatedAt']['schema:geo']):
                node_id_coord = node_id_counter
                node_id_counter += 1

                G_culturel.add_node(node_id_coord)
                node_labels[node_id_coord] = "Coordonnées"
                node_details[node_id_coord] = {
                    'title': "Coordonnées",
                    'text': str(objet['isLocatedAt']['schema:geo']['schema:latitude']['@value']) + ", " + str(objet['isLocatedAt']['schema:geo']['schema:longitude']['@value']),
                    'balise': "p"
                }

                # On lie les coordonnées à l'établissement
                G_culturel.add_edge(node_id_etablissement, node_id_coord)
                edge_labels[(node_id_etablissement, node_id_coord)] = ''

    # Ajout des noeuds et des attributs pour chaque établissement
    for objet in data:
        add_nodes()

    return G_economique, G_culturel, node_labels, edge_labels, node_details

# Construction du graphe des établissements touristiques
G_economique_datatourisme, G_culturel_datatourisme, node_labels, edge_labels, node_details = build_graph_datatourisme(etablissements_ville_recherchee)

# 746 783
#===============================================Fusion des graphes===================================================

#============Fusion entre le Wikipédia et celui du répertoire des élus municipaux==============
# On déclare le graphe G comme une copie du graphe de wikipédia
G = G_wiki.copy()

# On prend le graphe de wikipédia et on ajoute le noeud "Politique et administration" du graphe des élus. Le noeud aura comme attributs : {'title': 'Elus municipaux actuels', 'text': '', 'balise': 'h3'}
for node in G_wiki.nodes:
    if node_details[node]['title'] == 'Politique et administration':
        # Récupération du nœud "Politique et administration" dans le graphe Wiki
        politique_node_wiki = node

        # Récupération du nœud "Elus municipaux actuels" dans le graphe des élus
        elus_node_id = None
        for elus_node, details in node_details.items():
            if details['title'] == 'Elus municipaux':
                elus_node_id = elus_node
                break

        # Vérification si le nœud "Elus municipaux" a été trouvé
        if elus_node_id is not None:
            # Ajout de l'arc entre "Politique et administration" et "Elus municipaux"
            G.add_edge(politique_node_wiki, elus_node_id)
            edge_labels[(politique_node_wiki, elus_node_id)] = ''

            # Ajout des enfants de "Elus municipaux" comme enfants de "Elus municipaux" dans le graphe final
            descendants = nx.descendants(G_elu, elus_node_id)
            for descendant in descendants:
                # Ajout des descendants directs de "Elus municipaux" comme enfants de "Elus municipaux" dans le graphe final
                if descendant not in G.nodes:
                    # Si le descendant n'existe pas encore dans le graphe final, l'ajouter avec les mêmes attributs
                    G.add_node(descendant, **node_details[descendant])
                # Ajoute un arc entre "Elus municipaux" et le descendant
                G.add_edge(elus_node_id, descendant)
                edge_labels[(elus_node_id, descendant)] = ''

#============Fusion entre le graphe fusionné et les deux graphes de dataTourisme (économique et culturel)==============

# Liste des nœuds à traiter
nodes_to_process = [
    {'source_node_title': 'Culture locale et patrimoine', 'sub_source_node_title': 'Patrimoine culturel', 'target_graph': G_culturel_datatourisme},
    {'source_node_title': 'Économie', 'sub_source_node_title': 'Tourisme et loisir', 'target_graph': G_economique_datatourisme}
]

# On traite les deux graphes des établissements touristiques (culturels et économiques)
for node_data in nodes_to_process:
    source_node_title = node_data['source_node_title']
    sub_source_node_title = node_data['sub_source_node_title']
    target_graph = node_data['target_graph']

    # Recherche du nœud source dans le graphe fusionné
    source_node_id_fusion = None
    for node in G.nodes:
        if node_details[node]['title'] == source_node_title:
            source_node_id_fusion = node
            break

    # Si le nœud source est trouvé (normalement il est toujours présent car créé lors de la création du graphe Wiki)
    if source_node_id_fusion:
        # Recherche de l'id du nœud cible dans le graphe des établissements touristiques
        target_node_id_tourisme = None      # -> 'Tourisme et loisir' ou 'Patrimoine culturel' selon le graphe
        for node in target_graph.nodes:
            if node_details[node]['title'] == sub_source_node_title:
                target_node_id_tourisme = node
                break

        # Recherche de l'id du nœud cible dans les enfants du nœud source du graphe fusionné
        target_node_id_fusion = None        # -> 'Tourisme et loisir' ou 'Patrimoine culturel' selon le graphe
        for child in G.successors(source_node_id_fusion):
            if node_details[child]['title'] == sub_source_node_title:
                target_node_id_fusion = child
                break

        # Si le nœud cible n'est pas trouvé dans le graphe fusionné
        if not target_node_id_fusion:
            # Ajout du noeud cible du graphe des établissements touristiques comme enfant du nœud source du graphe fusionné
            G.add_node(target_node_id_tourisme, **node_details[target_node_id_tourisme])
            node_labels[target_node_id_tourisme] = node_details[target_node_id_tourisme]['title']
            # Ajout de l'arc entre le nœud source du graphe fusionné et le nœud cible du graphe des établissements touristiques
            G.add_edge(source_node_id_fusion, target_node_id_tourisme)
            edge_labels[(source_node_id_fusion, target_node_id_tourisme)] = ''

            # Ajout des enfants du nœud cible dans le graphe des établissements touristiques comme enfants du nœud cible dans le graphe final
            descendants = nx.descendants(target_graph, target_node_id_tourisme)
            for descendant in descendants:
                if descendant not in G.nodes:
                    # Si le descendant n'existe pas encore dans le graphe final, on l'ajoute avec les mêmes attributs
                    G.add_node(descendant, **node_details[descendant])
                    node_labels[descendant] = node_details[descendant]['title']
                # Ajoute un arc entre le nœud cible et le descendant
                G.add_edge(target_node_id_tourisme, descendant)
                edge_labels[(target_node_id_tourisme, descendant)] = ''
        # Si le nœud cible est trouvé dans le graphe fusionné
        else:
            # Ajout des enfants du nœud cible du graphe des établissements touristiques comme enfants du nœud cible du graphe fusionné
            descendants = nx.descendants(target_graph, target_node_id_tourisme)
            for descendant in descendants:
                if descendant not in G.nodes:
                    # Si le descendant n'existe pas encore dans le graphe final, on l'ajoute avec les mêmes attributs
                    G.add_node(descendant, **node_details[descendant])
                    node_labels[descendant] = node_details[descendant]['title']
                # Ajoute un arc entre le nœud cible et le descendant
                G.add_edge(target_node_id_tourisme, descendant)
                edge_labels[(target_node_id_tourisme, descendant)] = ''


# Visualisation des données du graphe
def display_node_info(G, node_details, node, depth=0, visited=set()):
    # Ajouter le nœud actuel à l'ensemble des nœuds visités
    visited.add(node)

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
    elif info['balise'] in ['h2', 'h3', 'h4', 'h5', 'h6', 'table']:
        # Affiche le titre pour les balises 'h*' et 'title'
        node_info = info['title']
    else:
        # Utilise le titre par défaut pour les autres balises
        node_info = f"Title: {info['title']}"

    # Affiche les informations du nœud avec l'indentation correspondante
    print("    " * depth + node_info)

    # Parcours des enfants du nœud
    for child in G.successors(node):
        # Vérifie si le nœud enfant a déjà été visité
        if child not in visited:
            # Appel récursif pour afficher les informations de chaque enfant avec une indentation supplémentaire
            display_node_info(G, node_details, child, depth + 1, visited)

for node, details in node_details.items():
    if details['title'] == 'Root':
        display_node_info(G, node_details, node)


# Visualisation du graphe
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=1500, node_color='lightblue', font_size=10,
        font_weight='bold')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
plt.title('Graphe des élus municipaux et des sections Wikipedia de Moirans')
plt.show()