import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from networkx.drawing.nx_pydot import write_dot
import graphviz
from IPython.display import display_png

#Création graphe non orienté représentant les liens de parentés entre les chevaliers de la table ronde.
G = nx.Graph()
#Ajout des noeuds
G.add_nodes_from([(i,{"color":"blue"}) for i in range(16)])
#Ajout des arêtes des liens d'amour
G.add_edges_from([(0, 15), (2, 3),(1,9),(1,3)], color="pink")
#Ajout des arêtes des liens familiaux
G.add_edges_from([(2, 10), (3, 11),(1,8),(8,9),(4,13),(2,5),(1,6),(6,7),(6,8),(7,9)], color="green")
#Renommage les noeuds
names = {0:"Merlin",1:"Arthur",2:"Lancelot",3:"Guenievre",4:"Perceval",5:"Galaad",6:"Gauvain",7:"Yvain",8:"Mordred",9:"Morgane",
        10:"Bohort",11:"Leodagan",12:"Bedivere",13:"Lamorak",14:"Tristan",15:"Dame du Lac"}
Table_ronde=nx.relabel_nodes(G,names)

#Affichage avec les méthodes de networkx
pos = nx.fruchterman_reingold_layout(Table_ronde)

plt.figure(figsize = (20, 10))
nx.draw_networkx_nodes(Table_ronde, pos, node_color ="#4169E1")
#les arêtes correspondant aux liens d'amour sont en rose :
nx.draw_networkx_edges(Table_ronde, pos,edgelist= [("Merlin","Dame du Lac"), ("Lancelot", "Guenievre"),
                                                   ("Arthur","Morgane"),("Arthur","Guenievre")], edge_color = "pink")
#et celles correspondant aux liens d'amitié sont en vert :
nx.draw_networkx_edges(G, pos, edgelist =[("Lancelot", "Bohort"), ("Guenievre", "Leodagan"),
                                          ("Arthur","Mordred"),("Mordred","Morgane"),("Perceval","Lamorak"),
                                          ("Lancelot","Galaad"),("Arthur","Gauvain"),("Gauvain","Yvain"),
                                          ("Gauvain","Mordred"),("Yvain","Morgane")],
                       edge_color='green')

nx.draw_networkx_labels(Table_ronde, pos)
plt.show();