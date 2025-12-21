import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.main_utils import get_settings
import csv

def load_settings(base_app_path) :
    ########################################DATA_RECOVERY_CONFIGURATION########################################
    # === 1. Retrieving configuration settings from the get_settings function contained in the app.py file ===
    settings = get_settings()

    ## If the data is compliant, information extraction
    if settings is None :
        return None
    else :
        ## Extracting the various configuration details
        company_name = settings["company_name"]
        decideur_list = settings["decideur_list"]
        criteria_list = settings["criteria_list"]
        alternative_list = settings["alternative_list"]
        folder_name = settings["folder_name"]
        folder_date = settings["folder_date"]

        ########################################RECOVERING_FILE_NAMES_TO_RECOVER########################################

        # === 2. Retrieving outputs based on decision-makers' preferences from the company's output folder ===
        ## Paths to the different CSV files
        csv_output_path = os.path.join(base_app_path, f"output/app_output/{folder_name}")
        csv_output_criteria_path = os.path.join(csv_output_path, "critere/")
        csv_output_alternative_path = os.path.join(csv_output_path, "alternative/")

        ## Retrieves the file names from the preference criteria folders
        ### This allows you to check that the files corresponding to the company are present and then retrieve their name.
        ### All files are prefixed in the same way; we only retrieve those whose parameters match.
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
    # === 1. Reconstructing the path to the exit folder ===
    folder_path = os.path.join(base_app_path, f"output/gAHP_output/{folder_name}/ranking/")
    os.makedirs(folder_path, exist_ok = True)

    # === 2. Creation of a second ranking rounded to 3 decimal places ===
    final_ranking_round = [(name, round(float(val), 3)) for name, val in final_ranking]

    # === 3. Writing the rankings to two CSV files ===
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
    # === 1. Importing the various parameters ===
    base_path = os.path.dirname(__file__)
    base_app_path = os.path.abspath(os.path.join(base_path, ".."))

    julia_programme_path = base_path + "/gAHPOptimizationUnit.jl"

    # Checking for the presence of the Julia model
    if os.path.isfile(julia_programme_path) :
        # Checking for the presence of the configuration file
        if load_settings(base_app_path) is not None :
            # === 2. Retrieving settings ===
            decideur_list, criteria_list, alternative_list, criteria_list_file, alternative_list_file, csv_output_criteria_path, csv_output_alternative_path, folder_name = load_settings(base_app_path)
            excepted_count_alternative = len(decideur_list) * len(criteria_list)

            # === 3. Model Julia will call if everything is OK ===
            if len(criteria_list_file) == len(decideur_list) and len(alternative_list_file) == excepted_count_alternative :
                from julia import Julia
                Julia(compiled_modules=False)
                
                from julia import Main
                Main.include(julia_programme_path)
                    
                ## Retrieving the final ranking of alternatives
                final_ranking = Main.ahp_with_multiple_criteria(csv_output_criteria_path, csv_output_alternative_path, decideur_list, criteria_list, alternative_list, criteria_list_file, alternative_list_file)
                
                # Writing the final ranking to a CSV file
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