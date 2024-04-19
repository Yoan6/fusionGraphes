import networkx as nx
import matplotlib.pyplot as plt

# Créer un graphe dirigé
G = nx.DiGraph()

# Ajouter des nœuds avec du texte
G.add_node("A", text="Ceci est le texte associé au nœud A.")
G.add_node("B", text="Ceci est le texte associé au nœud B.")
G.add_node("C", text="Ceci est le texte associé au nœud C.")

# Ajouter des arêtes entre les nœuds
G.add_edge("A", "B")
G.add_edge("B", "C")

# Deuxième graphe
G2 = nx.DiGraph()
G2.add_node("D", text="Ceci est le texte associé au nœud D.")
G2.add_edge("C", "D")

# Fusionner les deux graphes
merged_graph = nx.compose(G, G2)

# Dessiner le graphe fusionné
pos = nx.spring_layout(merged_graph, seed=42)
plt.figure(figsize=(10, 8))
nx.draw(merged_graph, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10, font_weight="bold")
# Ajouter le texte associé à chaque nœud
node_labels = nx.get_node_attributes(merged_graph, "text")
nx.draw_networkx_labels(merged_graph, pos, labels=node_labels, font_size=8, font_color="black")
plt.title("Graphe fusionné avec NetworkX")
plt.show()