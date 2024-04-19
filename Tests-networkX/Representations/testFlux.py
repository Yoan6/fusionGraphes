import json
import networkx as nx
import matplotlib.pyplot as plt

# Charge les données JSON-LD depuis un fichier
with open("flux-test.jsonld", "r") as f:
    data = json.load(f)

# Crée un graphe dirigé
G = nx.DiGraph()

# Analyse les données JSON-LD et ajoute des nœuds et des arêtes au graphe
for node in data["@graph"]:
    print(node)
    if "@type" in node and node["@type"] == "http://schema.org/Person":
        G.add_node(node["@id"], type=node["@type"], name=node["http://schema.org/name"][0]["@value"])
    elif "@type" in node and node["@type"] == "http://schema.org/Book":
        G.add_node(node["@id"], type=node["@type"], name=node["http://schema.org/name"][0]["@value"])
        if "http://schema.org/author" in node:
            for author in node["http://schema.org/author"]:
                G.add_edge(author["@id"], node["@id"], relationship="author")

# Dessiner le graphe
plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10, font_weight="bold")
plt.title("Graphe à partir de données JSON-LD")
plt.show()