from flask import Flask, render_template, request, redirect, url_for
import csv
import os
import numpy as np

app = Flask(__name__, template_folder = "templates")

#Page d'accueil : index.html
@app.route("/")
def index() :
    return render_template("index.html")

@app.route("/")
def reponse() :
    return render_template("validation.html")

#Route pour traiter les préférences envoyées par le formulaire
@app.route("/submit", methods = ["POST"])
def submit() :
    if request.method == "POST" :
        #Récupérer l'identifiant du décideur et les critères/alternatives
        nom_decideur = request.form.get("decideur", "").upper().strip()

        #Récupérer la valeur des critères/alternatives
        criteria_list = [int(request.form.get("critere1", "")), int(request.form.get("critere2", "")), int(request.form.get("critere3", ""))]
        alternative_list = [int(request.form.get("alternative1", "")), int(request.form.get("alternative2", "")), int(request.form.get("alternative3", ""))]
        #Nbr critères et alternatives
        criteria_n = len(criteria_list)
        alternative_n = len(alternative_list)
        #Création de la matrice des critères/alternatives
        criteria_matrix = np.zeros((criteria_n,criteria_n))
        alternative_matrix = np.zeros((alternative_n,alternative_n))

        for i in range(criteria_n) :
            for j in range(criteria_n) :
                criteria_matrix[i, j] = criteria_list[i] / criteria_list[j]

        print(criteria_list)
        print(criteria_matrix)

        for i in range(alternative_n) :
            for j in range(alternative_n) :
                alternative_matrix[i, j] = alternative_list[i] / alternative_list[j]

        print(alternative_list)
        print(alternative_matrix)

        preferences = {
            'decideur': request.form.get('decideur', ''),
            'critere1': request.form.get('critere1', ''),
            'critere2': request.form.get('critere2', ''),
            'critere3': request.form.get('critere3', ''),
            'alternative1': request.form.get('alternative1', ''),
            'alternative2': request.form.get('alternative2', ''),
            'alternative3': request.form.get('alternative3', '')
        }

        #Configuration du nom du fichier CSV
        criteria_file_path = f"preference_criteria_{nom_decideur}.csv"
        alternative_file_path = f"preference_alternative_{nom_decideur}.csv"

        #Sauvegarder dans le fichier CSV
        with open(criteria_file_path, mode = "w", newline = "") as criteria_file :
            criteria_writer = csv.writer(criteria_file)

            for c in criteria_matrix :
                criteria_writer.writerow(c)
        criteria_file.close()

        with open(alternative_file_path, mode="w", newline="") as alternative_file :
            alternative_writer = csv.writer(alternative_file)

            for a in alternative_matrix :
                alternative_writer.writerow(a)
        alternative_file.close()

        return redirect(url_for('index'))
    
if __name__ == '__main__' :
    app.run(debug = True, host = '0.0.0.0', port = 5000)
