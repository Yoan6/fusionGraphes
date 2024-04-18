import networkx as nx
import matplotlib.pyplot as plt

# Deuxième graphe
G2 = nx.DiGraph()
G2.add_node("C", text="Ceci est le texte associé au nœud C.")
G2.add_node("D", text="Ceci est le texte associé au nœud D.")
G2.add_edge("C", "D")

# Dessiner le graphe
pos = nx.spring_layout(G2, seed=42)  # Choisir une disposition pour le graphe
plt.figure(figsize=(8, 6))
nx.draw(G2, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10, font_weight="bold")
# Ajouter le texte associé à chaque nœud
node_labels = nx.get_node_attributes(G2, "text")
nx.draw_networkx_labels(G2, pos, labels=node_labels, font_size=8, font_color="black")
plt.title("Graphe avec NetworkX et texte associé aux nœuds")
plt.show()