#from waitress import serve #serveur sur lequel lancer le site
from flask import Flask, render_template, request, redirect, jsonify, session    #serveur de test
import csv
import numpy as np
import pandas as pd
import os
import datetime
import subprocess
import secrets
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict

app = Flask(__name__, template_folder = "templates")
app.secret_key = secrets.token_hex(32)  # Clé secrète générée pour chaque session

def generate_alternative_graph(final_ranking, config_graph_file):
    
    final_ranking.sort(key=lambda x: x[1], reverse=False)  # Trier par score décroissant

    names = [name for name, _ in final_ranking]
    scores = [score for _, score in final_ranking]

    #Création de la figure et de son axe
    ##Utilisation de figsize pour ajuster la taille du graphique
    fig, ax = plt.subplots(figsize = (10, 2))

    #Configuration du titre et des labels
    fig.suptitle("Classement des alternatives", fontsize = 14, fontweight = 'bold', color = '#333333')
    
    #Tracer la droite de 0 à 1
    ax.hlines(y = 1, xmin = 0, xmax = 1, color = '#56c49b', linewidth = 2)

    #Tracer les points
    #zorder=3 pour que les points soient au-dessus de la ligne
    colors = ['#1f77b4' if i % 2 == 0 else '#9467bd' for i in range(len(scores))]   #Alternance de couleurs pour les points
    ax.scatter(scores, [1] * len(scores), color = colors, s = 100, zorder = 3)

    #Affichage des noms des alternatives
    ##Utilisation de defaultdict pour regrouper les scores proches
    ###1 : Regrouper les scores proches
    grouped_positions = defaultdict(list)
    for name, score in final_ranking :
        found_group = False
        for key in grouped_positions :
            if abs(score - key) <= 0.01 :  # Vérifier si le score est proche d'un groupe existant
                grouped_positions[key].append((name, score))
                found_group = True
                break
        if not found_group :    # Si le score n'est pas proche d'un groupe existant, on crée un nouveau groupe
            grouped_positions[score].append((name, score))

    ###2 : Afficher les noms + scores avec décalage Y progressif
    for group in grouped_positions.values() :
        for i, (name, score) in enumerate(group) :
            vertical_offset = 1.08 + i * 0.07  # Empilement clair, 0.07 d'écart
            color = '#1f77b4' if i % 2 == 0 else '#9467bd'  # Alternance de couleurs pour les textes
            ax.text(score, vertical_offset, f"{name}-({score:.2f})", ha='center', va='bottom', color=color, rotation=45, fontsize=9)

    #Marger les axes
    ax.set_xlim(-0.05, 1.05)  #Marge pour être sûr de voir les extrémités
    ax.set_ylim(0.9, 1.3)     #Marge verticale pour bien voir les noms

    #Affichage des ticks pour 0 et 1
    ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    ax.set_xticklabels(['0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1'])
    ax.set_yticks([])         #Pas de ticks en y

    ax.grid(True, linestyle='--', alpha=0.5)  #Grille en arrière-plan
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    plt.tight_layout()
    plt.savefig(config_graph_file, dpi=150)
    plt.close(fig)

#Fonction permettant de récupérer les paramètres de configuration depuis le fichier CSV
def get_settings() :
    #Récupération du chemin d'accès au dossier de l'application
    base_path = os.path.dirname(__file__)
    
    #Ouverture du fichier CSV contenant la configuration
    csv_configuration_path = os.path.join(base_path, "static/app_config/app_config_csv/app_config_csv.csv")
    
    #Vérification de l'existence du fichier de configuration
    if not os.path.isfile(csv_configuration_path) :
        return None
    else :
        #Lecture du fichier CSV de configuration
        df_configuration = pd.read_csv(csv_configuration_path, delimiter = ";")
        
        ##Extraction des différents paramètres
        decideur_list = [d.upper().strip() for d in df_configuration["decideur"] if pd.notna(d)]
        criteria_list = [c.upper().strip() for c in df_configuration["critere"] if pd.notna(c)]
        alternative_list = [a.upper().strip() for a in df_configuration["alternative"] if pd.notna(a)]
        
        #Dictionnaire des paramètres de configuration
        ##Si une liste est vide, on la met à None pour éviter les erreurs dans le template
        dict_settings = {
            "decideur_list" : decideur_list if decideur_list else None,
            "criteria_list" : criteria_list if criteria_list else None,
            "alternative_list" : alternative_list if alternative_list else None,
            "company_name" : df_configuration["nomEntreprise"].values[0].upper().strip() if pd.notna(df_configuration["nomEntreprise"].values[0]) else None,
            "folder_name" : df_configuration["nomDossier"].values[0].upper().strip() if pd.notna(df_configuration["nomDossier"].values[0]) else None,
            "folder_date" : df_configuration["dateDossier"].values[0].upper().strip() if pd.notna(df_configuration["dateDossier"].values[0]) else None,
            "supervisor" : df_configuration["superviseur"].values[0].upper().strip() if pd.notna(df_configuration["superviseur"].values[0]) else None
        }

        #Vérification de la présence de tous les paramètres nécessaires
        if any(value is None for value in dict_settings.values()):
            return None
        else:
            return dict_settings

#Fonction permettant de récupérer le classement final depuis le fichier CSV
##Le fichier CSV est généré par le script gAHP_output.py
def get_rank(output_rank_file):
    ##########################A MODIFIER##########################
    ########################VERIFIER QU ON A TOUS LES FIHCIERS
    #Lancement du script gAHPInterface.py pour générer le classement
    subprocess.run(["python", "gAHPInterface.py"], cwd=os.path.dirname(__file__))

    final_ranking = []
    try:
        with open(output_rank_file, mode="r") as file_output_rank:
            reader = csv.reader(file_output_rank)
            for row in reader :
                name = row[0].strip()
                score = float(row[1].strip())   #Conversion du score en float
                final_ranking.append((name, score))
        file_output_rank.close()
        return final_ranking
    except FileNotFoundError:
        print("Erreur : fichier de classement introuvable.")
        return []
    except Exception as e:
        print("Erreur lors de la lecture du classement :", e)
        return []

#Page d'accueil : index.html
@app.route("/")
def index() :
    #Récupération des paramètres de configuration
    settings = get_settings()

    if settings is None :
        return "Impossible : fichier de configuration non trouvé."
    else :
        decideur_list = settings["decideur_list"]
        criteria_list = settings["criteria_list"]
        alternative_list = settings["alternative_list"]
        company_name = settings["company_name"]

        return render_template("index.html", 
                            decideur_list = decideur_list, 
                            criteria_list = criteria_list, 
                            alternative_list = alternative_list, 
                            company_name = company_name,
                            date = datetime.datetime.today().strftime('%d/%m/%Y'))

#Route pour envoyer : informations sur les KPI du décideur sélectionné,
#                     la liste des critères et des alternatives,
#                     le chemin d'accès au graph de configuration                      
@app.route("/get_data/<decideur>")
def get_data(decideur) :
    #Récupération du chemin d'accès au dossier de l'application
    base_path = os.path.dirname(__file__)

    print(decideur)
    #Récupération des paramètres de configuration
    settings = get_settings()

    #Vérification de l'existence du fichier de configuration
    if settings is None :
        return "Impossible : fichier de configuration non trouvé."
    else :
        ##Extraction des différents paramètres
        folder_name = settings["folder_name"]
        #Chemin d'accès au dossier des KPI du décideur
        kpi_dir = os.path.join(base_path, "static/app_config/app_config_entreprise/" + folder_name + "/decideur/" + decideur + "/")

        #Initialisation du dictionnaire des résultats
        resultat = {"kpis" : [], 
                    "warnings" : [],
                    "criteria_list" : settings["criteria_list"],
                    "alternative_list" : settings["alternative_list"],
                    "graph_path" : f"/static/app_config/app_config_entreprise/{folder_name}/graph/gAHP_config_graph_{folder_name}.png"}
                                    
        #Vérification de l'existence du dossier
        if not os.path.exists(kpi_dir) :
            print("Impossible : Le dossier n'existe pas.")
            return jsonify(resultat)
        
        #Récupération de la liste des img dans le dossier KPI du décideur
        for filename in os.listdir(kpi_dir) :
            kpi_path = os.path.join(kpi_dir, filename + "/")
            if os.path.isdir(kpi_path) :
                kpi_list = [f for f in os.listdir(kpi_path) if f.lower().endswith((".png", ".jpeg", ".gif", ".jpg")) and f.lower().startswith("kpi_")]
                #Vérification de la présence d'une image
                ##Si pas d'image ou plusieurs images, on ajoute un message d'erreur
                if len(kpi_list) != 1 :
                    resultat["warnings"].append(f"Erreur : le dossier { filename } ne contient pas d'image ou plusieurs images.")
                else :
                    chemin_relatif = os.path.join("static", "app_config", "app_config_entreprise", folder_name, "decideur", decideur, filename, kpi_list[0])
                    chemin_web = "/" + chemin_relatif.replace("\\", "/")
                    resultat["kpis"].append({"kpi_name" : filename, "kpi_path" : chemin_web})   #filename.split("_")[0] : retourne le nom du critere contenu dans le nom du dossier du kpi du décideur
        return jsonify(resultat)

@app.route("/submit_decision_final", methods = ["POST"])
def submit_decision_final() :
    if request.method == "POST" :
        #Récupération du chemin d'accès au dossier de l'application
        base_path = os.path.dirname(__file__)

        #Récupération des paramètres de configuration
        settings = get_settings()
        
        #Vérification de l'existence du fichier de configuration
        if settings is None :
            return "Impossible : fichier de configuration non trouvé."
        else :
            ##Extraction des différents paramètres
            folder_name = settings["folder_name"]

            decision_final = request.form.get("supervisor_decision", None).strip()

            if decision_final is None :
                return "Aucune décision finale n'a été soumise."
            else :
                #Vérification de l'existence du dossier de sortie
                folder_decision_final_path = os.path.join(base_path, "output", "app_output", folder_name, "decision_final")
                os.makedirs(folder_decision_final_path, exist_ok = True)

                #Configuration du nom du fichier de décision finale
                file_decision_final_name = f"decision_final_{folder_name}.txt"
                file_decision_final_path = os.path.join(folder_decision_final_path, file_decision_final_name)

                #Enregistrement de la décision finale dans le fichier
                with open(file_decision_final_path, mode = "w") as decision_file :
                    decision_file.write(decision_final)
                decision_file.close()

                return "Décision finale enregistrée avec succès."

#Route pour traiter les préférences envoyées par le formulaire
@app.route("/submit_decision", methods = ["POST"])
def submit_decision() :
    if request.method == "POST" :
        #Récupération du chemin d'accès au dossier de l'application
        base_path = os.path.dirname(__file__)

        #Récupération des paramètres de configuration
        settings = get_settings()
        
        #Vérification de l'existence du fichier de configuration
        if settings is None :
            return "Impossible : fichier de configuration non trouvé."
        else :
            ##Extraction des différents paramètres
            company_name = settings["company_name"]
            criteria_list = settings["criteria_list"]
            altenative_list = settings["alternative_list"]
            folder_name = settings["folder_name"]
            folder_date = settings["folder_date"]

            #Récupérer l'identifiant du décideur
            decideur_name = request.form.get("decideur", None).upper().strip()
            if decideur_name is None :
                return "Aucun décideur n'a été sélectionné."
            else :
                #Stocker le nom du décideur dans la session du décideur
                session['decideur_name'] = decideur_name

                ########################################TRAITEMENT_PREFERENCES_CRITERES########################################
                #Récupérer les préférences sur les critères
                criteria_list_html = request.form.getlist("preference_critere", type = int)
                
                #Récupérer le nombre de critères
                nb_criteria = len(criteria_list_html)

                #Création de la matrice des critères
                criteria_matrix = np.zeros((nb_criteria, nb_criteria))

                #Construction de la matrice des préférences sur les critères
                for i in range(nb_criteria) :
                    for j in range(nb_criteria) :
                        criteria_matrix[i, j] = criteria_list_html[i] / criteria_list_html[j]

                #Configuration du nom des sorties CSV pour les critères
                file_criteria_name = f"preference_criteria_{company_name}_{decideur_name}_{folder_date}.csv"
                file_criteria_base = os.path.join(base_path, f"output/app_output/{folder_name}/critere")
                file_criteria_path = os.path.join(file_criteria_base, file_criteria_name)
                
                #Sauvegarder dans le fichier CSV
                with open(file_criteria_path, mode = "w", newline = "") as criteria_file :
                    writer = csv.writer(criteria_file)

                    for line in criteria_matrix :
                        writer.writerow(line)
                criteria_file.close()

                ########################################TRAITEMENT DES PREFERENCES ALTERNATIVES########################################
                #Matrice contenant les sous-matrices des alternatives par critère
                alternative_matrix = []

                #Récupérer les préférences sur les alternatives
                ##Pour chaque critère, on récupère les préférences sur les alternatives
                for c_index, _ in enumerate(criteria_list) :
                    #Récupérer les préférences sur les alternatives pour le critère c
                    alternative_list_html = []
                    for a_index, _ in enumerate(altenative_list) :
                        #Reconstruction du nom du champ
                        field_name = f"preference_alternative_{c_index}_{a_index}"

                        #Récupérer la valeur du champ
                        alternative_list_html.append(request.form.get(field_name, type = float))

                    #Récupérer le nombre d'alternatives pour le critère c (commun à tous les critères)
                    nb_alternative = len(alternative_list_html)

                    #Création de la matrice des alternatives pour le critère c
                    alternative_matrix_local = np.zeros((nb_alternative, nb_alternative))

                    #Construction de la matrice des préférences sur les alternatives pour le critère c
                    for i in range(nb_alternative) :
                        for j in range(nb_alternative) :
                            alternative_matrix_local[i, j] = alternative_list_html[i] / alternative_list_html[j]

                    alternative_matrix.append(alternative_matrix_local)
                        
                #Enregistrement de la matrice des alternatives dans un fichier CSV propre à chaque critère et chaque decideur
                for c_index, matrix in enumerate(alternative_matrix) :
                    #Récupération du nom du critère
                    criteria_name = criteria_list[c_index]

                    #Configuration du nom des sorties CSV pour les alternatives pour le critère c
                    file_alternative_name = f"preference_alternative_{company_name}_{decideur_name}_{criteria_name}_{folder_date}.csv"
                    file_alternative_base = os.path.join(base_path, f"output/app_output/{folder_name}/alternative")   #Accès au dossier app_output de l'entreprise
                    file_alternative_path = os.path.join(file_alternative_base, file_alternative_name)

                    with open(file_alternative_path, mode = "w", newline = "") as alternative_file :
                        writer = csv.writer(alternative_file)
                        
                        for line in matrix :
                            writer.writerow(line)
                    alternative_file.close()

                #Redirection vers la page de classement
                return redirect('/rank')

#Route pour afficher le classement final
@app.route('/rank')
def post_order() :
    #Récupération des paramètres de configuration
    settings = get_settings()

    if settings is None :
        return "Impossible : fichier de configuration non trouvé."
    else :
        folder_name = settings["folder_name"]

        base_path = os.path.dirname(__file__)
        #Chemin d'accès au dossier de sortie du classement
        output_rank_folder = os.path.join(base_path, "output", "gAHP_output", folder_name, "ranking")
        os.makedirs(output_rank_folder, exist_ok = True)
        #Chemin d'accès au fichier de classement
        output_rank_file = os.path.join(output_rank_folder, f"gAHP_output_rank_round_{folder_name}.csv")
        
        #Chemin d'accès au dossier de sortie du graph
        config_graph_folder = os.path.join(base_path, "static", "app_config", "app_config_entreprise", folder_name, "graph")
        os.makedirs(config_graph_folder, exist_ok = True)   #Création du dossier s'il n'existe pas déjà
        #Chemin d'accès au graph de classement
        config_graph_file = os.path.join(config_graph_folder, f"gAHP_config_graph_{folder_name}.png")

        #Vérification de l'existence du dossier et du fichier du classement
        if not os.path.exists(output_rank_folder) :
            return "Impossible : dossier de sortie du classement introuvable."
        else :
            decideur_name = session.get("decideur_name", None)
            supervisor = settings["supervisor"]

            if decideur_name is None :
                return "Impossible : nom du décideur non trouvé dans la session."
            else :
                #Récupération du classement final
                final_ranking = get_rank(output_rank_file)

                if final_ranking == [] :
                    return "Impossible : classement final introuvable ou vide."
                else :
                    #Création du graph des alternatives
                    generate_alternative_graph(final_ranking, config_graph_file)

                    final_ranking_organized = sorted(final_ranking, key=lambda x: x[1], reverse=True)  # Trier par score décroissant
                    return render_template('ranking.html',
                                            data=final_ranking_organized, 
                                            decideur_name = decideur_name, 
                                            company_name=settings["company_name"],
                                            supervisor=supervisor,
                                            date = datetime.datetime.today().strftime('%d/%m/%Y'))

if __name__ == '__main__' :
    app.run(debug = True, host = '0.0.0.0', port = 5000)

#############A UTILISER UNE FOIS EN PRODUCTION#############
#if __name__ == "__main__":
#    serve(app, host="0.0.0.0", port=5000)