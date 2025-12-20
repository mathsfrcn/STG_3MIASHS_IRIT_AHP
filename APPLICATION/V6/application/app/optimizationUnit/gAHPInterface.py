import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.main_utils import get_settings
import csv

def load_settings(base_app_path) :
    ########################################RECUPERATION_DONNEES_CONFIGURATION########################################
    #1. Récupération des paramètres de configuration depuis le fonction get_settings contenue dans le fichier app.py
    settings = get_settings()

    ##Si les données sont conformes, extraction des informations
    if settings is None :
        return None
    else :
        ##Extraction des différentes informations de paramétrage
        company_name = settings["company_name"]
        decideur_list = settings["decideur_list"]
        criteria_list = settings["criteria_list"]
        alternative_list = settings["alternative_list"]
        folder_name = settings["folder_name"]
        folder_date = settings["folder_date"]

        ########################################RECONSTITUTION_NOMS_FICHIERS_A_RECUPERER########################################

        #2. Récupération des outputs critere&preference des décideurs dans le dossier output de l'entreprise
        ##Chemins vers les différents csv
        csv_output_path = os.path.join(base_app_path, f"output/app_output/{folder_name}")
        csv_output_criteria_path = os.path.join(csv_output_path, "critere/")
        csv_output_alternative_path = os.path.join(csv_output_path, "alternative/")

        ##Récupère le nom des fichiers dans les dossiers critere&preference
        ###Permet de vérifier que les fichiers correspondants à l'entrepise sont présents puis de récupérer leur nom
        ###Tous les fichiers sont préfixés de la même façon, on récupère uniquement ceux dont les paramétres correspo
        criteria_list_file = []
        for filename in os.listdir(csv_output_criteria_path) :
            for decideur in decideur_list :
                csv_criteria_prefix = f"preference_criteria_{company_name}_{decideur}_{folder_date}.csv"
                if csv_criteria_prefix == filename :
                    criteria_list_file.append(filename)

        alternative_list_file = []
        for filename in os.listdir(csv_output_alternative_path) :
            for decideur in decideur_list :
                for criteria in criteria_list :
                    csv_alternative_prefix = f"preference_alternative_{company_name}_{decideur}_{criteria}_{folder_date}.csv"
                    if csv_alternative_prefix == filename :
                        alternative_list_file.append(filename)

        return (decideur_list, 
                criteria_list,
                alternative_list,
                criteria_list_file, 
                alternative_list_file, 
                csv_output_criteria_path, 
                csv_output_alternative_path,
                folder_name,)

def write_ranking(base_app_path, folder_name, final_ranking) :
    #1. Reconsitution du chemin d'accès au dossier de sortie
    folder_path = os.path.join(base_app_path, f"output/gAHP_output/{folder_name}/ranking/")
    os.makedirs(folder_path, exist_ok = True)

    #2. Création d'un deuxieme classement arrondi à 3 décimales
    final_ranking_round = [(name, round(float(val), 3)) for name, val in final_ranking]

    #3. Ecriture des classements dans deux fichiers CSV
    with open(folder_path + f"gAHP_output_rank_global_{folder_name}.csv", mode = "w", newline = "") as file_output :
        writer = csv.writer(file_output)
        
        for line in final_ranking :
            writer.writerow(line)
    file_output.close()

    with open(folder_path + f"gAHP_output_rank_round_{folder_name}.csv", mode = "w", newline = "") as file_output :
        writer = csv.writer(file_output)
        
        for line in final_ranking_round :
            writer.writerow(line)
    file_output.close()

########################################PYTHON_TO_JULIA########################################

def get_ranking() :
    #1. Import des différents parametres
    base_path = os.path.dirname(__file__)
    base_app_path = os.path.abspath(os.path.join(base_path, ".."))


    julia_programme_path = base_path + "/gAHPOptimizationUnit.jl"

    #Vérification de la présence du modele Julia
    if os.path.isfile(julia_programme_path) :
        #Vérification de la présence du fichier de parametrage
        if load_settings(base_app_path) is not None :
            #2. Récupération des paramètres
            decideur_list, criteria_list, alternative_list, criteria_list_file, alternative_list_file, csv_output_criteria_path, csv_output_alternative_path, folder_name = load_settings(base_app_path)
            excepted_count_alternative = len(decideur_list) * len(criteria_list)

            #3. Appel du modèle Julia si tout est ok
            if len(criteria_list_file) == len(decideur_list) and len(alternative_list_file) == excepted_count_alternative :
                from julia import Main
                Main.include(julia_programme_path)
                    
                ##Récupération du classement final des alternatives
                final_ranking = Main.ahp_with_multiple_criteria(csv_output_criteria_path, csv_output_alternative_path, decideur_list, criteria_list, alternative_list, criteria_list_file, alternative_list_file)
                
                #Ecriture du classement final dans un fichier CSV
                write_ranking(base_app_path, folder_name, final_ranking)

                return final_ranking
            else :
                print("Impossible : il manque des fichiers.")
                return None
        else :
            print("Impossible : fichier de configuration non trouvé.")
            return None
    else :
        print("Impossible : programme Julia non trouvé.")
        return None

final_ranking = get_ranking()