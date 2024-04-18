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

# Dessiner le graphe
pos = nx.spring_layout(G, seed=42)  # Choisir une disposition pour le graphe
plt.figure(figsize=(8, 6))
nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10, font_weight="bold")
# Ajouter le texte associé à chaque nœud
node_labels = nx.get_node_attributes(G, "text")
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color="black")
plt.title("Graphe avec NetworkX et texte associé aux nœuds")
plt.show()