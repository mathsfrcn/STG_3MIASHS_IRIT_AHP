from flask import Blueprint, render_template, request, redirect, jsonify, session
from app.utils.main_utils import get_settings, get_rank, generate_alternative_graph
import csv
import numpy as np
import os
import datetime

main_blueprint = Blueprint('main', __name__)

########################################################################################################################
# Page redirection
########################################################################################################################

# Home page : home.html
@main_blueprint.route('/')
def home() :
    return render_template("home.html")

# Configuration page : configuration.html
@main_blueprint.route("/redirection_configuration")
def configuration() :
    return render_template("configuration.html")

# Filling page : filling.html
@main_blueprint.route("/redirection_filling")
def filling() :
    # Retrieving configuration settings
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

########################################################################################################################
# Submit decisions
########################################################################################################################
@main_blueprint.route("/submit_configuration", methods=['POST'])
def submit_configuration():
    # Initialisation
    data = {}
    
    if request.is_json:
        data = request.get_json()
        
        # === 1. Lists recovery ===
        raw_company_name = data.get("company_name", "ENTREPRISE")
        company_name = "_".join(raw_company_name.split())
        decideurs_list = data.get("decideurs_list", None)
        criteria_list = data.get("criteria_list", None)
        alternatives_list = data.get("alternatives_list", None)
        kpis_list = data.get("kpis_list", None)
        
        # === 2. Supervisor recovery ===
        supervisor_index = data.get("supervisor_id")
        supervisor_name = decideurs_list[supervisor_index] if supervisor_index is not None else None
        
        # === 3. Matrix recovery ===
        assignments = data.get("assignments", {})
        
        if not company_name :
            return jsonify({"status": "error", "message": "Le nom de l'entreprise est invalide"}), 400
        
        
        
    
        
        
        
        
        
        return jsonify({"status": "success", "message": "Configuration traitée"}), 200

    return jsonify({"status": "error", "message": "Format JSON attendu"}), 400

########################################################################################################################
# Sends decisions
########################################################################################################################

# Path for sending : information on the selected decision-maker's KPIs
#                    the list of criteria and alternatives
#                    the path to the configuration graph
@main_blueprint.route("/get_data/<decideur>")
def get_data(decideur) :
    # === 1. Retrieving the application folder path ===
    base_path = os.path.dirname(__file__)

    # === 2. Retrieving configuration settings ===
    settings = get_settings()

    # Checking for the existence of the configuration file
    if settings is None :
        return "Impossible : fichier de configuration non trouvé."
    else :
        # Extraction of the different parameters
        folder_name = settings["folder_name"]
        
        # === 3. Path to the decision-maker's KPI folder ===
        kpi_dir = os.path.join(base_path, "static/app_config/app_config_entreprise/" + folder_name + "/decideur/" + decideur + "/")

        # === 4. Initializing the results dictionary ===
        resultat = {"kpis" : [], 
                    "warnings" : [],
                    "criteria_list" : settings["criteria_list"],
                    "alternative_list" : settings["alternative_list"],
                    "graph_path" : f"/static/app_config/app_config_entreprise/{folder_name}/graph/gAHP_config_graph_{folder_name}.png"}
                                    
        # === 5. Verification of the existence of the decision-maker's KPI file ===
        if not os.path.exists(kpi_dir) :
            print("Impossible : Le dossier n'existe pas.")
            return jsonify(resultat)
        
        # === 6. Retrieving the list of images from the decision-maker's KPI folder ===
        for filename in os.listdir(kpi_dir) :
            kpi_path = os.path.join(kpi_dir, filename + "/")
            if os.path.isdir(kpi_path) :
                kpi_list = [f for f in os.listdir(kpi_path) if f.lower().endswith((".png", ".jpeg", ".gif", ".jpg")) and f.lower().startswith("kpi_")]
                # Checking for the presence of an image
                ## If there are no images or multiple images, an error message is added.
                if len(kpi_list) != 1 :
                    resultat["warnings"].append(f"Erreur : le dossier { filename } ne contient pas d'image ou plusieurs images.")
                else :
                    chemin_relatif = os.path.join("static", "app_config", "app_config_entreprise", folder_name, "decideur", decideur, filename, kpi_list[0])
                    chemin_web = "/" + chemin_relatif.replace("\\", "/")
                    resultat["kpis"].append({"kpi_name" : filename, "kpi_path" : chemin_web})   #filename.split("_")[0] : returns the name of the criterion contained in the folder name of the decision-maker's KPI
        return jsonify(resultat)

# Path for processing preferences submitted via the form    
@main_blueprint.route("/submit_decision", methods = ["POST"])
def submit_decision() :
    if request.method == "POST" :
        # === 1. Retrieving the application folder path ===
        base_path = os.path.dirname(__file__)

        # === 2. Retrieving configuration settings ===
        settings = get_settings()
        
        # Checking for the existence of the configuration file
        if settings is None :
            return "Impossible : fichier de configuration non trouvé."
        else :
            ## Extraction of the different parameters
            company_name = settings["company_name"]
            criteria_list = settings["criteria_list"]
            altenative_list = settings["alternative_list"]
            folder_name = settings["folder_name"]
            folder_date = settings["folder_date"]

            # === 3. Retrieve the decision-maker's ID ===
            decideur_name = request.form.get("decideur", None).upper().strip()
            if decideur_name is None :
                return "Aucun décideur n'a été sélectionné."
            else :
                # Store the decision-maker's name in the decision-maker's session
                session['decideur_name'] = decideur_name

                ########################################PROCESSING_PREFERENCES_CRITERIA########################################
                # === 4.1. Retrieve preferences based on criteria ===
                criteria_list_html = request.form.getlist("preference_critere", type = int)
                
                #Retrieve the number of criteria
                nb_criteria = len(criteria_list_html)

                # === 4.2. Creation of the criteria matrix ===
                criteria_matrix = np.zeros((nb_criteria, nb_criteria))

                # Construction of the preference matrix based on the criteria
                for i in range(nb_criteria) :
                    for j in range(nb_criteria) :
                        criteria_matrix[i, j] = criteria_list_html[i] / criteria_list_html[j]

                # === 4.3. Configuring CSV output names for criteria ===
                file_criteria_name = f"preference_criteria_{company_name}_{decideur_name}_{folder_date}.csv"
                file_criteria_base = os.path.join(base_path, f"output/app_output/{folder_name}/critere")
                file_criteria_path = os.path.join(file_criteria_base, file_criteria_name)
                
                # === 4.4. Save to CSV file ===
                with open(file_criteria_path, mode = "w", newline = "") as criteria_file :
                    writer = csv.writer(criteria_file)

                    for line in criteria_matrix :
                        writer.writerow(line)
                criteria_file.close()

                ########################################PROCESSING_ALTERNATIVE_PREFERENCES########################################
                #Matrix containing the sub-matrices of alternatives by criterion
                alternative_matrix = []

                # === 5.1. Retrieve preferences for alternatives ===
                ## For each criterion, we retrieve the preferences for the alternatives
                for c_index, _ in enumerate(criteria_list) :
                    # Retrieve preferences for alternatives for criterion c
                    alternative_list_html = []
                    for a_index, _ in enumerate(altenative_list) :
                        # Reconstructing the field name
                        field_name = f"preference_alternative_{c_index}_{a_index}"

                        # Retrieve the value of the field
                        alternative_list_html.append(request.form.get(field_name, type = float))

                    # Retrieve the number of alternatives for criterion c (common to all criteria)
                    nb_alternative = len(alternative_list_html)

                    # === 5.2. Creation of the alternatives matrix for criterion c ===
                    alternative_matrix_local = np.zeros((nb_alternative, nb_alternative))

                    # Construction of the preference matrix for alternatives for criterion c
                    for i in range(nb_alternative) :
                        for j in range(nb_alternative) :
                            alternative_matrix_local[i, j] = alternative_list_html[i] / alternative_list_html[j]

                    alternative_matrix.append(alternative_matrix_local)
                        
                # === 5.3. Saving the alternatives matrix in a CSV file specific to each criterion and each decision-maker
                for c_index, matrix in enumerate(alternative_matrix) :
                    # Retrieving the criterion name
                    criteria_name = criteria_list[c_index]

                    # Configuring CSV output names for alternatives for criterion c
                    file_alternative_name = f"preference_alternative_{company_name}_{decideur_name}_{criteria_name}_{folder_date}.csv"
                    file_alternative_base = os.path.join(base_path, f"output/app_output/{folder_name}/alternative")
                    file_alternative_path = os.path.join(file_alternative_base, file_alternative_name)

                    with open(file_alternative_path, mode = "w", newline = "") as alternative_file :
                        writer = csv.writer(alternative_file)
                        
                        for line in matrix :
                            writer.writerow(line)
                    alternative_file.close()

                # Redirecting to the ranking page
                return redirect('/rank')

########################################################################################################################
# Validate a decision
########################################################################################################################

# Path to view the final ranking
@main_blueprint.route("/rank")
def post_order() :
    # === 1. Retrieving configuration settings ===
    settings = get_settings()

    # Checking for the existence of the configuration file
    if settings is None :
        return "Impossible : fichier de configuration non trouvé."
    else :
        folder_name = settings["folder_name"]

        # === 2. Verification of the existence of the files for exiting the classification ===
        base_path = os.path.dirname(__file__)
        # === 2.1. Path to the ranking exit file ===
        output_rank_folder = os.path.join(base_path, "output", "gAHP_output", folder_name, "ranking")
        os.makedirs(output_rank_folder, exist_ok = True)
        # Path to the classification file
        output_rank_file = os.path.join(output_rank_folder, f"gAHP_output_rank_round_{folder_name}.csv")
        
        # === 2.2. Path to the graph's output folder ===
        config_graph_folder = os.path.join(base_path, "static", "app_config", "app_config_entreprise", folder_name, "graph")
        os.makedirs(config_graph_folder, exist_ok = True)   # Create the folder if it does not already exist
        # Path to the ranking graph
        config_graph_file = f"gAHP_config_graph_{folder_name}.png"

        # === 3. Verification of the existence of the file and the classification file ===
        if not os.path.exists(output_rank_folder) :
            return "Impossible : dossier de sortie du classement introuvable."
        else :
            # === 4. Retrieving the decision-maker's name from the session ===
            decideur_name = session.get("decideur_name", None)
            supervisor = settings["supervisor"]

            # Verification of the existence of the decision-maker's name
            if decideur_name is None :
                return "Impossible : nom du décideur non trouvé dans la session."
            else :
                # === 5. Retrieving the final ranking ===
                final_ranking = get_rank(output_rank_file)

                # Verification of the existence of the final ranking
                if final_ranking != [] :
                    # === 6. Creation of the alternatives graph ===
                    generate_alternative_graph(final_ranking, config_graph_file, config_graph_folder)
                
                # === 7. Organization of the final ranking for display ===
                final_ranking_organized = sorted(final_ranking, key=lambda x: x[1], reverse=True)
                    
                return render_template('ranking.html',
                                        data=final_ranking_organized, 
                                        decideur_name = decideur_name, 
                                        company_name=settings["company_name"],
                                        supervisor=supervisor,
                                        date = datetime.datetime.today().strftime('%d/%m/%Y'))

# Path to submit the final decision
@main_blueprint.route("/submit_decision_final", methods = ["POST"])
def submit_decision_final() :
    if request.method == "POST" :
        # === 1. Retrieving the application folder path ===
        base_path = os.path.dirname(__file__)

        # === 2. Retrieving configuration settings ===
        settings = get_settings()
        
        # Checking for the existence of the configuration file
        if settings is None :
            return "Impossible : fichier de configuration non trouvé."
        else :
            ## Extraction of the different parameters
            folder_name = settings["folder_name"]

            # === 3. Retrieval of the final decision submitted by the supervisor ===
            decision_final = request.form.get("supervisor_decision", None).strip()

            if decision_final is None :
                return "Aucune décision finale n'a été soumise."
            else :
                # === 4. Verification of the existence of the exit file ===
                folder_decision_final_path = os.path.join(base_path, "output", "app_output", folder_name, "decision_final")
                os.makedirs(folder_decision_final_path, exist_ok = True)

                # === 5. Final decision file name configuration ===
                file_decision_final_name = f"decision_final_{folder_name}.txt"
                file_decision_final_path = os.path.join(folder_decision_final_path, file_decision_final_name)

                # === 6. Recording of the final decision in the file ===
                with open(file_decision_final_path, mode = "w") as decision_file :
                    decision_file.write(decision_final)
                decision_file.close()

                return "Décision finale enregistrée avec succès."