from flask import Flask, render_template, request, redirect, url_for
import csv
import numpy as np
import pandas as pd
import os

app = Flask(__name__, template_folder = "templates")

#Page d'accueil : index.html
@app.route("/")
def index() :
    #Ouverture du fichier CSV contenant la configuration
    df_configuration = pd.read_csv("C:\\Users\\Mathis\\OneDrive\\Documents\\STAGE\\APPLICATION\\test_serveur_site\\V3\\decideurs.csv", delimiter = ",")
    ##Extraction des différentes listes de décideurs, critères, alternatives et le nom de l'entreprise
    decideur_list_html = [d.upper().strip() for d in df_configuration["decideur"] if pd.notna(d)]
    criteria_list_html = [c.upper().strip() for c in df_configuration["critere"] if pd.notna(c)]
    altenative_list_html = [a.upper().strip() for a in df_configuration["alternative"] if pd.notna(a)]
    nomEntreprise = df_configuration["nomEntreprise"].values[0].upper().strip()
    ##Extraction des images KPI
    ###Chemin d'accès aux images
    image_path = os.path.join(app.static_folder, "C:\\Users\\Mathis\\OneDrive\\Documents\\STAGE\\APPLICATION\\test_serveur_site\\V3\\static\\images")
    ###Création de la liste d'images KPI
    ####Filtre pour ne garder que les images qui commencent par "kpi_"
    image_prefix = "kpi_"
    image_list_kpi_html = [f"images/{filename}" for filename in os.listdir(image_path) if filename.startswith(image_prefix) and filename.endswith((".png", ".jpeg", ".gif", ".jpg"))]

    #Tests
    print(decideur_list_html)
    print(criteria_list_html)
    print(altenative_list_html)
    print(nomEntreprise)
    print(image_list_kpi_html)
    
    return render_template("index.html", 
                           decideur_list_html = decideur_list_html, 
                           criteria_list_html = criteria_list_html, 
                           alternative_list_html = altenative_list_html, 
                           nomEntreprise = nomEntreprise,
                           image_list_kpi_html = image_list_kpi_html)

#Route pour traiter les préférences envoyées par le formulaire
@app.route("/submit", methods = ["POST"])
def submit() :
    if request.method == "POST" :
        #Récupérer l'identifiant du décideur
        nom_decideur = request.form.get("decideur", "").upper().strip()
        #Récupérer les préférences sur les critères et les alternatives du décideur
        criteria_list = request.form.getlist("preference_critere", type = int)
        alternative_list = request.form.getlist("preference_alternative", type = int)
        #Tests
        print(criteria_list)
        print(alternative_list)
        #Récupérer le nombre de critères et d'alternatives
        criteria_list_n = len(criteria_list)
        alternative_list_n = len(alternative_list)

        #Création de la matrice des critères/alternatives
        criteria_matrix = np.zeros((criteria_list_n,criteria_list_n))
        alternative_matrix = np.zeros((alternative_list_n,alternative_list_n))

        #Construction de la matrice des préférences sur les critères et les alternatives
        for i in range(criteria_list_n) :
            for j in range(criteria_list_n) :
                criteria_matrix[i, j] = criteria_list[i] / criteria_list[j]

        print(criteria_list)
        print(criteria_matrix)

        for i in range(alternative_list_n) :
            for j in range(alternative_list_n) :
                alternative_matrix[i, j] = alternative_list[i] / alternative_list[j]

        print(alternative_list)
        print(alternative_matrix)

        #Configuration du nom des sorties CSV
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