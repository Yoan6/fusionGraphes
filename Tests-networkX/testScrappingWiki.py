import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def extract_sections_recursive(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    root = {'title': 'Root', 'children': []}
    current_node = root
    parents = [root]

    for tag in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(tag.name[1])
        title = tag.text.strip().split('[')[0]

        # Move up the hierarchy if necessary
        while len(parents) >= level:
            parents.pop()

        # Create new node
        new_node = {'title': title, 'children': []}
        if len(parents) == level - 1:
            parents[-1]['children'].append(new_node)

        # Update current node and parents
        current_node = new_node
        parents.append(current_node)

    return root['children']


def build_graph(sections):
    G = nx.DiGraph()
    node_labels = {}
    edge_labels = {}

    def add_nodes(section, parent_node=None):
        title = section['title']
        node = len(G.nodes)
        G.add_node(node)
        node_labels[node] = title
        if parent_node is not None:
            G.add_edge(parent_node, node)
            edge_labels[(parent_node, node)] = ''  # Empty label for the edge
        for child in section['children']:
            add_nodes(child, parent_node=node)

    add_nodes({'title': 'Root', 'children': sections})  # Start from the root

    return G, node_labels, edge_labels


def assign_node_colors(G):
    color_palette = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']  # Define color palette for different levels
    node_colors = []
    for node in G.nodes:
        level = len(nx.shortest_path(G, 0, node)) - 1  # Compute level of the node
        color_index = min(level, len(color_palette) - 1)  # Ensure index is within range
        node_colors.append(color_palette[color_index])
    return node_colors


def create_legend(color_palette):
    legend_elements = []
    for i, color in enumerate(color_palette):
        legend_elements.append(
            Line2D([0], [0], marker='o', color='w', label=f'Level {i + 1}', markerfacecolor=color, markersize=10))
    return legend_elements


def main():
    # URL de la page Wikipedia à scraper
    url_wikipedia = 'https://fr.wikipedia.org/wiki/Vourey'

    sections = extract_sections_recursive(url_wikipedia)
    print("Sections: ", sections)

    G, node_labels, edge_labels = build_graph(sections)

    # Assign node colors based on hierarchy level
    node_colors = assign_node_colors(G)

    # Draw the graph
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=1500, node_color=node_colors, font_size=10,
            font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    # Add legend
    color_palette = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']  # Define color palette for different levels
    legend_elements = create_legend(color_palette)
    plt.legend(handles=legend_elements, loc='upper left')

    plt.title('Section Graph with Node Colors and Legend')
    plt.show()


if __name__ == "__main__":
    main()
