import requests

# Fonction pour récupérer les données JSON de la page Wikipédia
def get_wikipedia_data(page_title):
    url = f"https://fr.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&titles={page_title}&rvslots=*&rvprop=content"
    response = requests.get(url)
    data = response.json()
    return data

# Fonction pour extraire les valeurs des modèles de crochets et accolades à partir des données JSON
def extract_template_values(json_data):
    page_id = next(iter(json_data['query']['pages']))  # Obtient l'ID de la page
    page_data = json_data['query']['pages'][page_id]   # Obtient les données de la page
    content = page_data['revisions'][0]['slots']['main']['*']  # Obtient le contenu de la page
    return content

# Page Wikipédia à analyser
page_title = "Vourey"

# Récupère les données JSON de la page Wikipédia
wikipedia_data = get_wikipedia_data(page_title)

# Extrait les valeurs des modèles de crochets et accolades
content = extract_template_values(wikipedia_data)

# Affiche le contenu de la page
print(content)