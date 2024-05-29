# Fusion de graphe

Ce code contient un algorithme de fusion d'arborescence de graphe et un site web qui utilise l'algorithme à partir d'une ville de France métropolitaine donnée en reçensant les informations de la ville automatiquement. Les données proviennent de 3 sites plus ou moins fournis et plus ou moins fiables : 

- Wikipédia (assez fiable et très fournis)
- Plateforme nationale du tourisme en France OPENDATA (très fiable et très fournis)
- Répertoire national des élus municipaux (très fiable, très fournis mais peu pour ce qui nous intéresse : les élus d'une ville)

L'algorithme de fusion de graphe est codé avec la version Python3 et le site web est codé en Angular avec du TypeScript et du html/css.

## Création de graphe avec NetworkX

### Création d'un graphe

Pour créer un graphe il faut utiliser la librarie python 'NetworkX' qui permet de générer des graphes en créant des noeuds, des arcs entre les noeuds et des labels aux noeuds. Il est possible de voir la documentation officielle de NetworkX [ici](https://networkx.org/documentation/stable/reference/introduction.html).

Pour créer un graphe dirigé il faut l'initialiser comme cela : 

```python
G = nx.DiGraph()
```

Pour ajouter un noeud il faut utiliser la fonction add_node avec un id et les attributs du noeud comme cela : 

```python
G.add_node(node_id, title="Titre du noeud", text="Texte du noeud", balise="h3")
```

Un noeud a toujours les trois mêmes attributs :
- title : le titre du noeud (par exemple le titre d'une page ou d'un titre de section)
- text : le texte du noeud (par exemple le texte d'un paragraphe)
- balise : la balise du noeud (par exemple h1, h2, h3, p, ul, li, etc)

Pour ajouter un arc entre deux noeud il faut indiquer de quel id de noeud part cet arc et à quel id de noeud il est relié. Exemple avec un noeud parent et un noeud actuel : 

```python
G.add_edge(parent_node, node_id)
```

### Affichage d'un graphe

Pour chacun des graphes il faut utiliser une liste 'node_labels' mentionnant les labels des noeuds à partir de leur id de noeud. Cette liste permet d'afficher les labels des noeuds pour l'affichage du graphe :

```python
# Ajout du titre du nœud dans le libellé pour l'affichage du graphe
node_labels[node_id] = "Pierre"
```

Chacun des noeuds a un id unique qui est généré grâce à une variable 'node_id_compteur' qu'il faut incrémenter après chaque attribution à un noeud :

```python
global node_id_counter
node_id = node_id_compteur
G.add_node(node_id, title="Pierre", text="Texte du noeud", balise="h3")
node_id_compteur += 1

```

De même que pour les labels des noeuds, il y a une liste pour les arcs nommée 'edge_labels' qui permet d'afficher les arcs entre les noeuds pour le graphe :

```python
edge_labels[(parent_node, node_id)] = ''  # Label vide pour l'arc
```

Pour afficher le graphe il faut d'abord renseigner la taille de la fenêtre contenant le futur graphe :

```python
plt.figure(figsize=(12, 8))
```

Ensuite, il faut renseigner le type de représentation, il en existe diverse mais le plus utilisé est **spring_layout** :

```python
pos = nx.spring_layout(G)
```

Pour définir le graphe, il faut fournir les listes des labels et arcs du graphe, la taille des noeuds, la couleur des noeuds, et le titre du graphe. Il est possible d'afficher ou non les labels avec l'option **with_labels**.

```python
nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=1500, node_color='lightblue', font_size=10,
        font_weight='bold')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
plt.title('Graphe des élus municipaux')
```

Enfin, pour afficher le graphe, il faut utiliser la fonction show : 

```python
plt.show()
```

### Affichage des données d'un graphe

Pour afficher les données d'un graphe, la méthode est différente selon le graphe. Généralement, il faut faire une boucle qui va traiter tous les noeuds du graphes et va regarder les détails du noeud en passant par la liste node_details avec l'id du noeud. 

Ensuite, il faut traiter tous les cas de balise qu'il peut y avoir et faire un affichage en fonction. Pour l'instant, il n'y a que les balises suivantes : 

- h1 (représente le titre de la page)
- h2 (représente un titre de rang inférieur au niveau h1)
- h3 (représente un titre de rang inférieur au niveau h2)
- h4 (représente un titre de rang inférieur au niveau h3)
- table (représente un tableau de donnée)
- tr (représente une ligne de tableau)
- p (représente un paragraphe)
- ul (représente une liste)
- li (représente une ligne de liste)

Il est possible d'aller plus dans les détails et d'aller récupérer plus d'information et donc de balise différentes notamment sur le scrapping des pages web de Wikipédia.

## Création de graphe pour Wikipédia
Pour la création de graphe pour Wikipédia il faut utiliser du scrapping à partir d'un url incluant la ville et récupérant les données html de la page wikipédia de la ville en question. Pour cela il faut utiliser un scrapper en python via la librairie [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) et la librairie [requests](https://realpython.com/python-requests/). On l'utilise comme cela pour récupérer le contenu html d'un site à partir de son url :

``` python
# Récupération de la réponse HTTP
response = requests.get(url)
# Analyse du contenu HTML de la page
soup = BeautifulSoup(response.text, 'html.parser')
```

### Extraction des données

C'est la fonction **extract_sections_recursive()** qui s'occupe de faire l'extraction des données depuis l'url de la page Wikipédia. Elle récupère toutes les balises qui nous intéresse pour l'instant (citées au dessus dans 'Affichage des données d'un graphe'), et à partir de ces donnée va faire des dictionnaires nommés 'section'. Chaque section est sous cette forme : 

```python
{'title': '', 'text': '', 'balise': '', 'children': []}
```

avec d'autre section dans children si il y a des balises filles de la balise de la section.

### Création du graphe

Ensuite, il y a une fonction **build_graph()** qui permet de créer un graphe à partir des données extraites de la fonction extract_sections_recursive().

**Remarque** : avant de faire l'appel à la fonction build_graph() il faut supprimer quelques sections inintéressantes comme le sommaires, les références, etc : 

```python
sections['children'] = sections['children'][0:1] + sections['children'][2:-2]
```

## Création de graphe pour le répertoire nationnal des élus municipaux

### Extraction des données

C'est la fonction **extract_csv()** qui se charge de faire l'extraction des données à partir de l'url de la page contenant le fichier csv des élus municiapux (https://www.data.gouv.fr/fr/datasets/repertoire-national-des-elus-1/). Elle se charge de récupérer le lien de téléchargement du fichier csv des élus municipaux en passant par des classes et id de balise. Ensuite, elle utilise la fonction **read_csv()** pour charger les données du fichier csv dans un dataframe :

```python
data = pd.read_csv(download_link, dtype=str, sep=';', encoding='utf-8')
```

Ensuite, pour limiter les données on fait un filtre sur la ville qui nous intéresse en utilisant la colonne 'Libellé de la ville'.

### Création du graphe

Pour créer le graphe, il faut utiliser la fonction **build_graph()** qui génére un graphe à partir des données filtrées sur la ville qui nous intéresse. Elle utilise une autre fonction **add_nodes()** qui va être appellée pour chaque ligne concernant la ville dans le fichier csv : 

```python
for _, row in csv_data.iterrows():
    add_nodes()
```

## Création de graphe pour dataTourisme

### Création d'un flux

Avant de faire quoique ce soit il faut tout d'abord se créer un compte diffuseur sur le site de [dataTourisme](https://diffuseur.datatourisme.fr/fr/) qui va permettre de créer un flux de donnée. Il faut ensuite créer un flux de donnée en renseignant les départements de France et les classes de points d'intérêts qui nous intéressent, puis de finaliser la création du flux en indiquant le type de fichier que l'on veut (il faut choisir jsonLD). A partir de celui-ci il faudra attendre le lendemain à 9h du matin pour pouvoir avoir accès au fichier car les fichiers sont mis à jour et peuvent être rechargé chaque matin à 9h. 

Pour automatiser l'accès aux données du fichier il faut créer une application sur le site dataTourisme en indiquant l'url que l'on veut et cela va nous donner une clé API qu'il faudra fournir pour accéder aux fichier automatiquement.

### Points d'intérêts

Le site de dataTourisme est un peu spécial et suis une logique d'ontologie avec des points d'intérêts. Un point d'intérêt est un élément touristique qui est géré par un Agent et qui peut être consommé via des produits et services. Chaque élément de dataTourisme est un point d'intérêt mais il existe de nombreuse classes et sous-classes de points d'intérêt. L'ontologie des points d'intérêts est décrite précisément [ici](https://gitlab.adullact.net/adntourisme/datatourisme/ontology/-/blob/master/Documentation/Doc-ontologie-3.1.0-FR.pdf?ref_type=heads).

## Site web

Le site web est codé avec Angular et propose 2 services et un component en plus du component principal. 

### Service city

Ce service permet de faire de l'autocomplétion pour la sélection de ville en utilisant une API du gouvernement disponible à l'url : https://geo.api.gouv.fr/communes. Il permet aussi de déterminer si la ville existe à partir de l'API.

### Service graph

Ce service permet de faire les appels à l'API Flask en fonction de ce que l'on veut faire (extraction des données et exportation du site)

### Component graph-display

Ce component sert à afficher le graphe en fonction d'une variable contenant les données json récupérées de l'API Flask.

### Component principal : app
Ce component permet de sélectionner une ville et d'afficher le component graph-display dès que l'algorithme de fusion de graphe a envoyé ses données via l'API Flask. Il y a un temps de chargement d'une dizaine de secondes dû à l'extraction des données du graphe des élus municipaux.

## API Flask

Pour faire le lien entre l'algorithme de fusion de graphe et le site web en Angular il y a une API Flask codé en Python (il est possible de trouver la documentation [ici](https://pythonbasics.org/flask-rest-api/)). Cette API doit être lancé avant de faire une recherche sur le site étant donné qu'elle fait le lien avec l'algorithme. Pour la lancer il faut lancer l'exécutable app.py : 

```python
python3 app.py
```

L'API fonctionne sur le port 5000 (localhost:5000) et propose pour l'instant deux routes : 
- /extract (POST)
  Cette route permet de lancer l'algorithme de fusion de graphe et d'envoyer les données récupérées
- /export (POST)
  Cette route permet d'extraire la page web afin d'avoir le site d'une ville en local et de pouvoir l'afficher postérieurement sans passer par le site Angular.

## Utilisation de l'environnement

Pour récupérer le code il faut générer un fichier git : 

```bash
git init
```

Ensuite, il faut cloner le répertoire sur Github après avoir copié le lien en utilisant http ou ssh :

```bash
git clone <code-de-clonage-http-ou-ssh>
```

Après avoir fait cela, il faut créer un environnement virtuel :

```bash
python -m venv venv
source venv/bin/activate
```
 Il faut installer les librairies et dépendances :
 
```bash
pip install -r requirements.txt
```

Il faut par la suite lancer l'API Flask : 
```bash
python3 app.py
```

Pour la première utilisation du site, il faut installer les dépendances nécessaires. Pour cela, placez-vous dans le dossier racine du site et installer les dépendances :

```bash
cd Site-ville
npm install
```

Après, il faut lancer le site Angular : 
```bash
ng serve --open
```

Info : l'option --open n'est pas obligatoire mais permet d'ouvrir le site en local dès le build fini du code

Normalement, le site devrait s'ouvrir dans votre navigateur mais si ce n'est pas le cas, il est possible de le lancer en allant à l'url : localhost:5200.

Sur le site web vous pouvez désormais sélectionner une ville et vous allez voir les informations sur celle-ci. Il est possible par la suite de sélectionner une autre ville ou d'exporter le site pour cette ville via deux bouton différents.











