import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

G = nx.DiGraph()

G.add_node("A", role="Manager", salary=3000)
G.add_node("B", role="Developer", salary=1800)
G.add_node("C", role="RH", salary=2000)
G.add_node("D", role="Developer", salary=4000)
G.add_node("E", role="Developer", salary=3200)

G.add_edge("A", "B", relation="Collaborator")
G.add_edge("A", "C", relation="Collaborator")
G.add_edge("B", "D", relation="Collaborator")
G.add_edge("B", "E", relation="Collaborator")
G.add_edge("C", "E", relation="Collaborator")
G.add_edge("D", "E", relation="Collaborator")

# Voir les données des noeuds
print("Noeuds et attributs:")
for node, attrs in G.nodes(data=True):
    print(node, attrs)

nx.draw(G, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold')
plt.title('Graphe des employés')
plt.show()