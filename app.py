#!/usr/bin/env python3

from flask import Flask, request, jsonify, send_file
import subprocess
import os
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route('/extract', methods=['POST'])
def extract():
    # Récupération des données JSON de la requête
    data = request.json
    ville = data.get('ville')
    code_commune = data.get('code_commune')
    departement = data.get('departement')

    # Chemin du script Python pour extraire les données
    script_path = 'Fusions/fusionGraphes.py'

    print(f"Executing script: {script_path} with arguments: {ville}, {code_commune}, {departement}")

    # Commande pour exécuter le script Python
    result = subprocess.run(['python3', script_path, ville, code_commune, departement], capture_output=True, text=True)

    print(f"Script stdout: {result.stdout}")
    print(f"Script stderr: {result.stderr}")

    # Vérification de la réussite de l'exécution du script
    if result.returncode == 0:
        # Récupération du chemin du fichier JSON généré
        json_file = 'graph_data.json'
        # Vérification de l'existence du fichier JSON
        if os.path.exists(json_file):
            print(f"Fichier json trouvé : {json_file}")
            # Lecture du contenu du fichier JSON
            with open(json_file, 'r', encoding='utf-8') as file:
                graph_data = json.load(file)
            # Suppression du fichier JSON
            os.remove(json_file)
            # Retourne les données du graphe sous forme de réponse JSON
            return jsonify({'status': 'success', 'data': graph_data})
        else:
            return jsonify({'status': 'error', 'message': 'Fichier JSON non trouvé'})
    else:
        return jsonify({'status': 'error', 'message': result.stderr})

# @app.route('/export', methods=['POST'])
# def export():
#     data = request.json
#     ville = data.get('ville')
#     code_commune = data.get('code_commune')
#     departement = data.get('departement')
#
#     script_path = 'Fusions/fusionGraphes.py'
#     result = subprocess.run(['python3', script_path, ville, code_commune, departement], capture_output=True, text=True)
#
#     if result.returncode == 0:
#         zip_file = 'Fusions/site_local.zip'
#         if os.path.exists(zip_file):
#             return send_file(zip_file, as_attachment=True)
#         else:
#             return jsonify({'status': 'error', 'message': 'Fichier ZIP non trouvé'}), 404
#     else:
#         return jsonify({'status': 'error', 'message': result.stderr}), 500


if __name__ == '__main__':
    app.run(debug=True)
