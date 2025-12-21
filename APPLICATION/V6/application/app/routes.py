from flask import Blueprint, render_template, request, redirect, jsonify, session
from app.utils.main_utils import get_settings, get_rank, generate_alternative_graph
import csv
import numpy as np
import os
import datetime

main_blueprint = Blueprint('main', __name__)

#Page d'accueil : filling.html
@main_blueprint.route('/')
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

        return render_template("filling.html", 
                            decideur_list = decideur_list, 
                            criteria_list = criteria_list, 
                            alternative_list = alternative_list, 
                            company_name = company_name,
                            date = datetime.datetime.today().strftime('%d/%m/%Y'))

#Route pour envoyer : informations sur les KPI du décideur sélectionné,
#                     la liste des critères et des alternatives,
#                     le chemin d'accès au graph de configuration
@main_blueprint.route("/get_data/<decideur>")
def get_data(decideur) :
    #1. Récupération du chemin d'accès au dossier de l'application
    base_path = os.path.dirname(__file__)

    #2. Récupération des paramètres de configuration
    settings = get_settings()

    #Vérification de l'existence du fichier de configuration
    if settings is None :
        return "Impossible : fichier de configuration non trouvé."
    else :
        ##Extraction des différents paramètres
        folder_name = settings["folder_name"]
        #3. Chemin d'accès au dossier des KPI du décideur
        kpi_dir = os.path.join(base_path, "static/app_config/app_config_entreprise/" + folder_name + "/decideur/" + decideur + "/")

        #4. Initialisation du dictionnaire des résultats
        resultat = {"kpis" : [], 
                    "warnings" : [],
                    "criteria_list" : settings["criteria_list"],
                    "alternative_list" : settings["alternative_list"],
                    "graph_path" : f"/static/app_config/app_config_entreprise/{folder_name}/graph/gAHP_config_graph_{folder_name}.png"}
                                    
        #4. Vérification de l'existence du dossier des KPI du décideur
        if not os.path.exists(kpi_dir) :
            print("Impossible : Le dossier n'existe pas.")
            return jsonify(resultat)
        
        #5. Récupération de la liste des img dans le dossier KPI du décideur
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

#Route pour traiter les préférences envoyées par le formulaire     
@main_blueprint.route("/submit_decision", methods = ["POST"])
def submit_decision() :
    if request.method == "POST" :
        #1. Récupération du chemin d'accès au dossier de l'application
        base_path = os.path.dirname(__file__)

        #2. Récupération des paramètres de configuration
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

            #3. Récupérer l'identifiant du décideur
            decideur_name = request.form.get("decideur", None).upper().strip()
            if decideur_name is None :
                return "Aucun décideur n'a été sélectionné."
            else :
                #Stocker le nom du décideur dans la session du décideur
                session['decideur_name'] = decideur_name

                ########################################TRAITEMENT_PREFERENCES_CRITERES########################################
                #4.1. Récupérer les préférences sur les critères
                criteria_list_html = request.form.getlist("preference_critere", type = int)
                
                #Récupérer le nombre de critères
                nb_criteria = len(criteria_list_html)

                #4.2. Création de la matrice des critères
                criteria_matrix = np.zeros((nb_criteria, nb_criteria))

                #Construction de la matrice des préférences sur les critères
                for i in range(nb_criteria) :
                    for j in range(nb_criteria) :
                        criteria_matrix[i, j] = criteria_list_html[i] / criteria_list_html[j]

                #4.3. Configuration du nom des sorties CSV pour les critères
                file_criteria_name = f"preference_criteria_{company_name}_{decideur_name}_{folder_date}.csv"
                file_criteria_base = os.path.join(base_path, f"output/app_output/{folder_name}/critere")
                file_criteria_path = os.path.join(file_criteria_base, file_criteria_name)
                
                #4.4. Sauvegarder dans le fichier CSV
                with open(file_criteria_path, mode = "w", newline = "") as criteria_file :
                    writer = csv.writer(criteria_file)

                    for line in criteria_matrix :
                        writer.writerow(line)
                criteria_file.close()

                ########################################TRAITEMENT DES PREFERENCES ALTERNATIVES########################################
                #Matrice contenant les sous-matrices des alternatives par critère
                alternative_matrix = []

                #5.1. Récupérer les préférences sur les alternatives
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

                    #5.2. Création de la matrice des alternatives pour le critère c
                    alternative_matrix_local = np.zeros((nb_alternative, nb_alternative))

                    #Construction de la matrice des préférences sur les alternatives pour le critère c
                    for i in range(nb_alternative) :
                        for j in range(nb_alternative) :
                            alternative_matrix_local[i, j] = alternative_list_html[i] / alternative_list_html[j]

                    alternative_matrix.append(alternative_matrix_local)
                        
                #5.3. Enregistrement de la matrice des alternatives dans un fichier CSV propre à chaque critère et chaque decideur
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

@main_blueprint.route("/submit_decision_final", methods = ["POST"])
def submit_decision_final() :
    if request.method == "POST" :
        #1. Récupération du chemin d'accès au dossier de l'application
        base_path = os.path.dirname(__file__)

        #2. Récupération des paramètres de configuration
        settings = get_settings()
        
        #Vérification de l'existence du fichier de configuration
        if settings is None :
            return "Impossible : fichier de configuration non trouvé."
        else :
            ##Extraction des différents paramètres
            folder_name = settings["folder_name"]

            #3. Récupération de la décision finale soumise par le superviseur
            decision_final = request.form.get("supervisor_decision", None).strip()

            if decision_final is None :
                return "Aucune décision finale n'a été soumise."
            else :
                #4. Vérification de l'existence du dossier de sortie
                folder_decision_final_path = os.path.join(base_path, "output", "app_output", folder_name, "decision_final")
                os.makedirs(folder_decision_final_path, exist_ok = True)

                #5. Configuration du nom du fichier de décision finale
                file_decision_final_name = f"decision_final_{folder_name}.txt"
                file_decision_final_path = os.path.join(folder_decision_final_path, file_decision_final_name)

                #6. Enregistrement de la décision finale dans le fichier
                with open(file_decision_final_path, mode = "w") as decision_file :
                    decision_file.write(decision_final)
                decision_file.close()

                return "Décision finale enregistrée avec succès."

#Route pour afficher le classement final
@main_blueprint.route("/rank")
def post_order() :
    #1. Récupération des paramètres de configuration
    settings = get_settings()

    #Vérification de l'existence du fichier de configuration
    if settings is None :
        return "Impossible : fichier de configuration non trouvé."
    else :
        folder_name = settings["folder_name"]

        #2. Vérification de l'existence des dossiers de sortie du classement
        base_path = os.path.dirname(__file__)
        #2.1. Chemin d'accès au dossier de sortie du classement
        output_rank_folder = os.path.join(base_path, "output", "gAHP_output", folder_name, "ranking")
        os.makedirs(output_rank_folder, exist_ok = True)
        #Chemin d'accès au fichier de classement
        output_rank_file = os.path.join(output_rank_folder, f"gAHP_output_rank_round_{folder_name}.csv")
        
        #2.2. Chemin d'accès au dossier de sortie du graph
        config_graph_folder = os.path.join(base_path, "static", "app_config", "app_config_entreprise", folder_name, "graph")
        os.makedirs(config_graph_folder, exist_ok = True)   #Création du dossier s'il n'existe pas déjà
        #Chemin d'accès au graph de classement
        config_graph_file = f"gAHP_config_graph_{folder_name}.png"

        #3. Vérification de l'existence du dossier et du fichier du classement
        if not os.path.exists(output_rank_folder) :
            return "Impossible : dossier de sortie du classement introuvable."
        else :
            #4. Récupération du nom du décideur depuis la session
            decideur_name = session.get("decideur_name", None)
            supervisor = settings["supervisor"]

            #Vérification de l'existence du nom du décideur
            if decideur_name is None :
                return "Impossible : nom du décideur non trouvé dans la session."
            else :
                #5. Récupération du classement final
                final_ranking = get_rank(output_rank_file)

                #Vérification de l'existence du classement final
                if final_ranking != [] :
                    #6. Création du graph des alternatives
                    generate_alternative_graph(final_ranking, config_graph_file, config_graph_folder)
                
                #7. Organisation du classement final pour l'affichage
                final_ranking_organized = sorted(final_ranking, key=lambda x: x[1], reverse=True)
                    
                return render_template('ranking.html',
                                        data=final_ranking_organized, 
                                        decideur_name = decideur_name, 
                                        company_name=settings["company_name"],
                                        supervisor=supervisor,
                                        date = datetime.datetime.today().strftime('%d/%m/%Y'))