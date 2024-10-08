import argparse
import tempfile

import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import json

from dask.dataframe import dd


def run(ville, departement, code_commune):
    ville = ville
    departement = departement
    code_commune = code_commune
    print(f"Ville: {ville}, Département: {departement}, Code commune: {code_commune}")

    lastUpdateElus = ''  # Date de la dernière mise à jour pour les élus

    # Compteur pour les identifiants des nœuds
    global node_id_counter
    node_id_counter = 0

    is_datatourisme_found = False
    is_wikipedia_found = False
    is_elus_found = False
    node_labels = {}
    edge_labels = {}

    #===============================================1er graphe===================================================

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
                if td and not td.find('div', {'id': 'img_toggle_0'}):  # Ignorer la partie sur la localisation
                    td_text = clean_text(td.get_text(separator=' ', strip=True))
                    # Ajoute les données à la section actuelle
                    current_section['children'].append({'title': th_text, 'text': td_text, 'balise': 'tr', 'children': []})
                elif th_text in titles:
                    # Crée une nouvelle section pour le titre
                    current_section = {'title': th_text, 'text': '', 'balise': 'table', 'children': []}
                    infobox_data.append(current_section)
        return infobox_data

    # Fonction pour traiter une section
    def process_section(tag, parents):
        # Récupération du niveau de la balise
        level = int(tag.name[1])
        # Récupération du titre de la section
        title = clean_text(tag.text.strip())

        # Déplacement dans la hiérarchie des sections si un niveau inférieur est rencontré
        while len(parents) >= level:
            parents.pop()

        # Création d'un nouveau nœud pour la section avec la balise associée
        new_node = {'title': title, 'text': '', 'balise': tag.name, 'children': []}
        # Ajout du nouveau nœud comme enfant du parent approprié
        parents[-1]['children'].append(new_node)
        parents.append(new_node)

        # Récupération du texte directement sous la balise h*
        current_tag = tag.find_next(lambda t: t.name in ['p', 'ul', 'h2', 'h3', 'h4', 'h5', 'h6'])
        while current_tag and current_tag.name not in ['h2', 'h3', 'h4', 'h5', 'h6']:
            if current_tag.name == 'p':
                # Création d'un nouveau nœud pour chaque balise <p>
                new_node['children'].append(
                    {'title': 'Paragraph', 'text': clean_text(current_tag.get_text().strip()), 'balise': 'p',
                     'children': []})
            elif current_tag.name == 'ul':
                # Création d'un nouveau nœud pour la balise <ul> et ses <li>
                ul_node = {'title': 'Unordered List', 'text': '', 'balise': 'ul', 'children': [
                    {'title': 'List Item', 'text': clean_text(li.get_text().strip()), 'balise': 'li', 'children': []} for li
                    in current_tag.find_all('li')]}
                new_node['children'].append(ul_node)
            current_tag = current_tag.find_next(lambda t: t.name in ['p', 'ul', 'h2', 'h3', 'h4', 'h5', 'h6'])

    # Fonction pour construire le graphe des sections et sous-sections
    def build_graph_wiki(sections):
        global node_id_counter  # Utilisation de la variable globale node_id_counter
        # Initialisation du graphe dirigé
        G = nx.DiGraph()

        # Fonction récursive pour ajouter les nœuds au graphe
        def add_nodes(section, parent_node=None):
            global node_id_counter  # Utilisation de la variable globale node_id_counter
            # Création de l'identifiant unique du nœud en utilisant le compteur
            node_id = node_id_counter
            node_id_counter += 1
            # Ajout du nœud au graphe avec son identifiant unique
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
    ville_wikipedia = ville.replace(' ', '_')
    print("Ville Wikipedia: " + ville_wikipedia)

    # URL de la page Wikipedia à traiter
    url_wikipedia = 'https://fr.wikipedia.org/wiki/' + ville_wikipedia
    url_wikipedia_homonyme = 'https://fr.wikipedia.org/wiki/' + ville_wikipedia + '_(' + departement + ')'

    # Fonction pour vérifier si une page Wikipedia contient des homonymes
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
        return 'Géographie' not in h2_tag

    if is_an_homonym(url_wikipedia):
        url_wikipedia = url_wikipedia_homonyme

    # Extraction des données de la page Wikipedia
    soup = extract_wikipedia(url_wikipedia)

    # Extraction des sections récursivement à partir de l'URL donnée
    sections = extract_sections(soup)

    if len(sections) > 1:
        is_wikipedia_found = True
        # On enlève la deuxième section qui est le sommaire et les deux dernières sections qui sont les références et les liens externes tout en gardant la première section qui est l'infobox
        sections['children'] = sections['children'][0:1] + sections['children'][2:-2]

        # Construction du graphe des sections et sous-sections
        G_wiki, node_labels, edge_labels = build_graph_wiki(sections)
    else:
        print("Aucune donnée trouvée pour la page Wikipedia de " + ville)


    #===============================================2ème graphe===================================================

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
        # On récupère la date de la dernière mise à jour
        lastUpdate = header.find('p', {'class': 'fr-text--xs fr-m-0 dash-after'}).text
        download_link = download_a['href']

        # Télécharge le fichier CSV et le stocke dans un fichier temporaire
        with requests.get(download_link, stream=True) as r:
            r.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, mode='w+b') as tmp_file:
                for chunk in r.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                tmp_file.flush()  # Vide le buffer pour s'assurer que toutes les données sont écrites

        # Charge le fichier CSV dans un DataFrame Dask
        data = dd.read_csv(tmp_file.name, dtype=str, sep=';', encoding='utf-8')

        return data.compute(), lastUpdate

    # URL du site des élus à traiter
    url_elus = 'https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/'

    # On met en majuscule la première lettre de chaque mot
    ville_elu = ville.title()
    print("Ville Elu: " + ville_elu)

    # Extraction des données du fichier CSV
    csv_file, lastUpdateElus = extract_csv(url_elus)

    # On récupère seulement la date de la dernière mise à jour
    lastUpdateElus = lastUpdateElus.replace('Mis à jour le ', '')

    # Si le code de la commune commence par 0, on le retire
    if code_commune.startswith('0'):
        code_commune = code_commune[1:]

    # Filtrage des données pour la ville en fonction du nom de la ville et du code de la commune
    ville_data = csv_file[(csv_file['Libellé de la commune'] == ville_elu) & (csv_file['Code de la commune'] == code_commune)]

    if len(ville_data) != 0:
        is_elus_found = True
        # Fonction pour construire le graphe des élus municipaux
        def build_graph_elus(csv_data):
            # Compteur pour les identifiants des nœuds
            global node_id_counter  # Utilisation de la variable externe node_id_counter

            # Initialisation du graphe dirigé
            G_elu = nx.DiGraph()

            def add_nodes():
                # Compteur pour les identifiants des nœuds
                global node_id_counter  # Utilisation de la variable externe node_id_counter

                # Nom complet de l'élu
                nom_prenom = row['Nom de l\'élu'] + ' ' + row['Prénom de l\'élu']

                # Création de l'identifiant unique du nœud en utilisant le compteur
                node_id = node_id_counter
                node_id_counter += 1  # Incrémentation du compteur pour le prochain nœud

                # Ajout du nœud au graphe avec son identifiant unique
                G_elu.add_node(node_id, title=nom_prenom, text='', balise='table')

                # Ajout du titre du nœud dans le libellé pour l'affichage du graphe
                node_labels[node_id] = nom_prenom

                # Ajout des nœuds pour "Nom de l'élu" et "Prénom de l'élu" en premier
                for key in ['Nom de l\'élu', 'Prénom de l\'élu']:
                    value = row[key]
                    if pd.notna(value):
                        attribute_node_id = node_id_counter
                        node_id_counter += 1
                        # Ajout d'un noeud pour chaque attribut de l'élu
                        G_elu.add_node(attribute_node_id, title=key, text=str(value), balise='tr')
                        # Ajout du libellé du nœud pour l'affichage du graphe
                        node_labels[attribute_node_id] = f"{key}: {value}"
                        # Ajout d'un lien du nœud 'table' vers le nœud 'tr'
                        G_elu.add_edge(node_id, attribute_node_id)

                # Ajout des autres attributs de l'élu comme des nœuds de balise 'tr' sous le nœud 'table'
                for k, v in row.items():
                    # S'il y a une valeur qui n'est pas NaN et que ce n'est ni 'Nom de l\'élu' ni 'Prénom de l\'élu', on l'ajoute
                    if pd.notna(v) and k not in ['Nom de l\'élu', 'Prénom de l\'élu']:
                        attribute_node_id = node_id_counter
                        node_id_counter += 1
                        # Ajout d'un noeud pour chaque attribut de l'élu
                        G_elu.add_node(attribute_node_id, title=k, text=str(v), balise='tr')
                        # Ajout du libellé du nœud pour l'affichage du graphe
                        node_labels[attribute_node_id] = f"{k}: {v}"
                        # Ajout d'un lien du nœud 'table' vers le nœud 'tr'
                        G_elu.add_edge(node_id, attribute_node_id)

                # Ajoute un lien du nœud principal 'Elus municipaux' vers le nœud 'table' de l'élu
                G_elu.add_edge(elus_node_id, node_id)

            # Création du nœud principal 'Elus municipaux'
            elus_node_id = node_id_counter
            node_id_counter += 1
            G_elu.add_node(elus_node_id, title='Elus municipaux', text='', balise='h3')
            node_labels[elus_node_id] = 'Elus municipaux'

            # Ajout de la date de la dernière mise à jour
            lastUpdate_node_id = node_id_counter
            node_id_counter += 1
            G_elu.add_node(lastUpdate_node_id, title='Dernière modif élus', text=lastUpdateElus, balise='p')
            node_labels[lastUpdate_node_id] = 'Dernière modif élus'
            G_elu.add_edge(elus_node_id, lastUpdate_node_id)

            # Ajout des nœuds et des attributs au graphe
            for _, row in csv_data.iterrows():
                add_nodes()

            return G_elu, node_labels, edge_labels

        # Construction du graphe des élus municipaux
        G_elu, node_labels, edge_labels = build_graph_elus(ville_data)
    else:
        print("Aucun élu trouvé pour la ville de " + ville)


    #===============================================3ème graphe===================================================

    def extract_dataTourisme(url):
        # Télécharge le fichier JSON-LD depuis l'URL
        response = requests.get(url)
        data = response.json()
        return data

    # URL pour télécharger le fichier JSON-LD (à changer selon le flux de données souhaité sur DATAtourisme)

    # URL pour le flux avec le département de l'Isère :
    #url_dataTourisme = "https://diffuseur.datatourisme.fr/webservice/f4f07d2f40c98b4eb046da28af2e651c/031aee5f-9dd7-4196-a677-610abe8fda77"  # Clé API : 031aee5f-9dd7-4196-a677-610abe8fda77

    # URL pour le flux avec TOUS les départements :
    #url_dataTourisme = "https://diffuseur.datatourisme.fr/webservice/7ac0037a21f50718b506b00401fba8a6/031aee5f-9dd7-4196-a677-610abe8fda77" # Clé API : 031aee5f-9dd7-4196-a677-610abe8fda77

    # URL à prendre avec les bons départements :
    url_dataTourisme = "https://diffuseur.datatourisme.fr/webservice/19d1980140e2c890eeb029fc4261f3fd/031aee5f-9dd7-4196-a677-610abe8fda77"    # Clé API : 031aee5f-9dd7-4196-a677-610abe8fda77

    # Extraction des données du fichier JSON-LD
    data = extract_dataTourisme(url_dataTourisme)

    # Fonction pour filtrer les données pour la ville
    def filter_dataTourisme(data, ville, code_commune):
        etablissements_ville_recherchee = []
        # Parcourt chaque objet dans le fichier JSON-LD
        for objet in data['@graph']:
            if 'isLocatedAt' in objet and 'schema:address' in objet['isLocatedAt'] and 'schema:addressLocality' in \
                    objet['isLocatedAt']['schema:address']:
                ville_etablissement = objet['isLocatedAt']['schema:address']['schema:addressLocality']
                code_commune_etablissement = objet['isLocatedAt']['schema:address']['hasAddressCity']['@id'][3:]
                if ville == ville_etablissement or code_commune == code_commune_etablissement:
                    etablissements_ville_recherchee.append(objet)
        return etablissements_ville_recherchee

    # Filtrage des données pour la ville
    etablissements_ville_recherchee = filter_dataTourisme(data, ville, code_commune)

    if etablissements_ville_recherchee:
        is_datatourisme_found = True
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
            G_economique.add_node(node_id_economie, title="Tourisme et loisir", text="", balise="h3")
            node_labels[node_id_economie] = "Tourisme et loisir"

            node_id_culturel = node_id_counter
            node_id_counter += 1

            # Ajout du premier noeud pour les établissements culturels
            G_culturel.add_node(node_id_culturel, title="Patrimoine culturel", text="", balise="h3")
            node_labels[node_id_culturel] = "Patrimoine culturel"

            def add_nodes():
                global node_id_counter

                title = objet['rdfs:label']['@value']

                # Création de l'identifiant unique du nœud en utilisant le compteur
                node_id_etablissement = node_id_counter
                node_id_counter += 1

                # Si l'établissement est économique on l'ajoute au graphe économique
                if ('schema:FoodEstablishment' or 'schema:LocalBusiness' or 'schema:Hotel' or 'schema:LodgingBusiness' or 'schema:Accommodation' or 'schema:TouristInformationCenter' or 'schema:Winery' or 'schema:Restaurant' or 'schema:Product') in objet['@type']:
                    G_economique.add_node(node_id_etablissement, title=title, text="", balise="h4")
                    node_labels[node_id_etablissement] = title

                    # On lie l'établissement au noeud économie
                    G_economique.add_edge(node_id_economie, node_id_etablissement)
                    edge_labels[(node_id_economie, node_id_etablissement)] = ''

                    # Ajout d'un nœud pour la description si elle existe
                    if 'owl:topObjectProperty' in objet and objet['owl:topObjectProperty'] and 'shortDescription' in objet['owl:topObjectProperty']:
                        node_id_description = node_id_counter
                        node_id_counter += 1

                        G_economique.add_node(node_id_description, title="Description", text=objet['owl:topObjectProperty']['shortDescription']['@value'], balise="p")
                        node_labels[node_id_description] = "Description"

                        # On lie la description à l'établissement
                        G_economique.add_edge(node_id_etablissement, node_id_description)
                        edge_labels[(node_id_etablissement, node_id_description)] = ''


                    # On crée un noeud pour les coordonnées de l'établissement si les coordonnées sont disponibles
                    if ('schema:geo' in objet['isLocatedAt'] and 'schema:latitude' in objet['isLocatedAt']['schema:geo'] and 'schema:longitude' in objet['isLocatedAt']['schema:geo']):
                        node_id_coord = node_id_counter
                        node_id_counter += 1

                        G_economique.add_node(node_id_coord, title="Coordonnées", text=str(objet['isLocatedAt']['schema:geo']['schema:latitude']['@value']) + ", " + str(objet['isLocatedAt']['schema:geo']['schema:longitude']['@value']), balise="p")
                        node_labels[node_id_coord] = "Coordonnées"

                        # On lie les coordonnées à l'établissement
                        G_economique.add_edge(node_id_etablissement, node_id_coord)
                        edge_labels[(node_id_etablissement, node_id_coord)] = ''

                    # Ajout d'un noeud pour la dernière mise à jour
                    if 'lastUpdateDatatourisme' in objet:
                        node_id_last_update = node_id_counter
                        node_id_counter += 1
                        # On transforme la date de la dernière mise à jour du format '2024-01-25T06:45:38.485Z' en '25/01/2024'
                        lastUpdate = objet['lastUpdateDatatourisme']['@value'].split('T')[0].split('-')[::-1]
                        G_economique.add_node(node_id_last_update, title="Dernière modif DATAtourisme", text=str('-'.join(lastUpdate)), balise="p")
                        node_labels[node_id_last_update] = "Dernière mise à jour"
                        G_economique.add_edge(node_id_etablissement, node_id_last_update)
                        edge_labels[(node_id_etablissement, node_id_last_update)] = ''

                # Si l'établissement est culturel on l'ajoute au graphe culturel
                else:
                    G_culturel.add_node(node_id_etablissement, title=title, text="", balise="h4")
                    node_labels[node_id_etablissement] = title

                    # On lie l'établissement au noeud culturel
                    G_culturel.add_edge(node_id_culturel, node_id_etablissement)
                    edge_labels[(node_id_culturel, node_id_etablissement)] = ''

                    # On crée un noeud pour la description de l'établissement si elle existe
                    if 'owl:topObjectProperty' in objet and objet['owl:topObjectProperty'] and 'shortDescription' in objet['owl:topObjectProperty']:
                        node_id_description = node_id_counter
                        node_id_counter += 1

                        G_culturel.add_node(node_id_description, title="Description", text=objet['owl:topObjectProperty']['shortDescription']['@value'], balise="p")
                        node_labels[node_id_description] = "Description"

                        # On lie la description à l'établissement
                        G_culturel.add_edge(node_id_etablissement, node_id_description)
                        edge_labels[(node_id_etablissement, node_id_description)] = ''

                    # On crée un noeud pour les coordonnées de l'établissement si les coordonnées sont disponibles
                    if ('schema:geo' in objet['isLocatedAt'] and 'schema:latitude' in objet['isLocatedAt']['schema:geo'] and 'schema:longitude' in objet['isLocatedAt']['schema:geo']):
                        node_id_coord = node_id_counter
                        node_id_counter += 1

                        G_culturel.add_node(node_id_coord, title="Coordonnées", text=str(objet['isLocatedAt']['schema:geo']['schema:latitude']['@value']) + ", " + str(objet['isLocatedAt']['schema:geo']['schema:longitude']['@value']), balise="p")
                        node_labels[node_id_coord] = "Coordonnées"

                        # On lie les coordonnées à l'établissement
                        G_culturel.add_edge(node_id_etablissement, node_id_coord)
                        edge_labels[(node_id_etablissement, node_id_coord)] = ''

                    # Ajout d'un noeud pour la dernière mise à jour
                    if 'lastUpdateDatatourisme' in objet:
                        node_id_last_update = node_id_counter
                        node_id_counter += 1
                        # On transforme la date de la dernière mise à jour du format '2024-01-25T06:45:38.485Z' en '25/01/2024'
                        lastUpdate = objet['lastUpdateDatatourisme']['@value'].split('T')[0].split('-')[::-1]
                        G_culturel.add_node(node_id_last_update, title="Dernière modif DATAtourisme", text=str('-'.join(lastUpdate)), balise="p")
                        node_labels[node_id_last_update] = "Dernière mise à jour"
                        G_culturel.add_edge(node_id_etablissement, node_id_last_update)
                        edge_labels[(node_id_etablissement, node_id_last_update)] = ''

            # Ajout des noeuds et des attributs pour chaque établissement
            for objet in data:
                add_nodes()

            return G_economique, G_culturel, node_labels, edge_labels

        # Construction du graphe des établissements touristiques
        G_economique_datatourisme, G_culturel_datatourisme, node_labels, edge_labels = build_graph_datatourisme(etablissements_ville_recherchee)
    else:
        print("Aucun établissement touristique trouvé pour la ville de " + ville)


    #===============================================Fusion des graphes===================================================

    #============Fusion entre le Wikipédia et celui du répertoire des élus municipaux==============

    G = nx.DiGraph()

    # Fonction pour ajouter les fils d'un noeud d'un graphe à un autre graphe en gardant toute l'arborecence
    def add_nodes_recursive(graph, other_graph, node_id, parent_id=None):
        # Récupération des informations du nœud
        info = other_graph.nodes[node_id]

        # Ajout du nœud au graphe avec ses attributs
        graph.add_node(node_id, **info)
        # Ajout du libellé du nœud pour l'affichage du graphe
        node_labels[node_id] = info['title']

        # Ajout de l'arc entre le nœud parent et le nœud actuel
        if parent_id is not None:
            graph.add_edge(parent_id, node_id)

        # Parcours récursif des enfants du nœud actuel
        for child_id in other_graph.successors(node_id):
            add_nodes_recursive(graph, other_graph, child_id, parent_id=node_id)

    # On déclare le graphe G comme une copie du graphe de wikipédia
    G = G_wiki.copy()

    if is_wikipedia_found and is_elus_found:
        # Recherche du nœud "Politique et administration" dans le graphe G_wiki
        politique_node_wiki = None
        for node in G_wiki.nodes:
            if G_wiki.nodes[node]['title'] == 'Politique et administration':
                politique_node_wiki = node
                break

        # Si le nœud "Politique et administration" n'existe pas, on le crée
        if politique_node_wiki is None:
            node_id = node_id_counter
            node_id_counter += 1
            politique_node_wiki = node_id
            G.add_node(politique_node_wiki, title='Politique et administration', text='', balise='h2')
            node_labels[politique_node_wiki] = 'Politique et administration'
            # On lie le nœud "Politique et administration" au nœud racine
            G.add_edge(list(G.nodes)[0], politique_node_wiki)
            edge_labels[(list(G.nodes)[0], politique_node_wiki)] = ''

        # Recherche du nœud "Elus municipaux" dans le graphe des élus
        elus_node_id = None
        for elus_node in G_elu.nodes:
            if G_elu.nodes[elus_node]['title'] == 'Elus municipaux':
                elus_node_id = elus_node
                break

        # Vérification si le nœud "Elus municipaux" a été trouvé
        if elus_node_id is not None:
            # Ajout du nœud "Elus municipaux" et de ses enfants dans le graphe final
            add_nodes_recursive(G, G_elu, elus_node_id, parent_id=politique_node_wiki)


    #============Fusion entre le graphe fusionné et les deux graphes de dataTourisme (économique et culturel)==============

    if is_datatourisme_found:
        nodes_to_process = [
            {'source_node_title': 'Culture locale et patrimoine', 'sub_source_node_title': 'Patrimoine culturel', 'target_graph': G_culturel_datatourisme},
            {'source_node_title': 'Économie', 'sub_source_node_title': 'Tourisme et loisir', 'target_graph': G_economique_datatourisme}
        ]

        # Liste des nœuds à traiter
        for node_data in nodes_to_process:
            source_node_title = node_data['source_node_title']
            sub_source_node_title = node_data['sub_source_node_title']
            target_graph = node_data['target_graph']

            # Recherche du nœud source dans le graphe fusionné
            source_node_id_fusion = None
            for node in G.nodes:
                if G.nodes[node]['title'] == source_node_title:
                    source_node_id_fusion = node
                    break

            if source_node_id_fusion:   # Normalement toujours présent
                # Recherche de l'id du nœud cible dans le graphe des établissements touristiques
                target_node_id_tourisme = None
                for node in target_graph.nodes:
                    if target_graph.nodes[node]['title'] == sub_source_node_title:
                        target_node_id_tourisme = node
                        break

                # Recherche de l'id du nœud cible dans les enfants du nœud source du graphe fusionné
                target_node_id_fusion = None
                for child in G.successors(source_node_id_fusion):
                    if G.nodes[child]['title'] == sub_source_node_title:
                        target_node_id_fusion = child
                        break

                # Si le nœud cible n'est pas trouvé dans le graphe fusionné, l'ajouter
                if not target_node_id_fusion:
                    # Ajout du nœud cible dans le graphe fusionné
                    target_node_id_fusion = target_node_id_tourisme
                    G.add_node(target_node_id_fusion, **target_graph.nodes[target_node_id_tourisme])
                    node_labels[target_node_id_fusion] = target_graph.nodes[target_node_id_tourisme]['title']
                    G.add_edge(source_node_id_fusion, target_node_id_fusion)

                else:
                    # S'il est trouvé, on supprime dans node_labels et edge_labels les éléments qui ont été ajoutés lors de la fusion précédente
                    del node_labels[target_node_id_fusion]

                # Ajout des enfants du nœud cible dans le graphe fusionné
                for child in target_graph.successors(target_node_id_tourisme):
                    add_nodes_recursive(G, target_graph, child, parent_id=target_node_id_fusion)

    if is_wikipedia_found and is_datatourisme_found or is_elus_found:
        # Visualisation des données du graphe
        def display_node_info(G, node, depth=0, visited=set()):
            # Ajouter le nœud actuel à l'ensemble des nœuds visités
            visited.add(node)

            # Récupère les informations du nœud
            info = G.nodes[node]

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
                    display_node_info(G, child, depth + 1, visited)

        display_node_info(G, 0)


        # Visualisation du graphe
        # plt.figure(figsize=(12, 8))
        # pos = nx.spring_layout(G)
        # nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=1500, node_color='lightblue', font_size=10,
        #         font_weight='bold')
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
        # plt.title('Graphe final fusionné')
        # plt.show()

        json_file_path = 'graph_data.json'

        # Conversion du graphe en dictionnaire JSON
        data = nx.readwrite.json_graph.tree_data(G, root=0)

        # Enregistrement du graphe fusionné en JSON
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

        print("Le graphe fusionné a été enregistré dans le fichier JSON : " + json_file_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fusion de graphes provenant de différentes sources de données.')
    parser.add_argument('ville', type=str, help='Nom de la ville à traiter')
    parser.add_argument('code_commune', type=str, help='Code de la commune de la ville')
    parser.add_argument('departement', type=str, help='Nom du département de la ville')
    args = parser.parse_args()

    run(args.ville, args.departement, args.code_commune)