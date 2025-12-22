from collections import defaultdict
import os
import csv
import subprocess
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#Fonction permettant de récupérer les paramètres de configuration depuis le fichier CSV
def get_settings() :
    #1. Récupération du chemin d'accès au dossier de l'application
    base_path = os.path.dirname(__file__)
    
    #2. Ouverture du fichier CSV contenant la configuration
    csv_configuration_path = os.path.abspath(os.path.join(base_path, "..", "static/app_config/app_config_csv/app_config_csv.csv"))

    #Vérification de l'existence du fichier de configuration
    if not os.path.isfile(csv_configuration_path) :
        return None
    else :
        #3. Lecture du fichier CSV de configuration
        df_configuration = pd.read_csv(csv_configuration_path, delimiter = ";")
        
        ##Extraction des différents paramètres
        decideur_list = [d.upper().strip() for d in df_configuration["decideur"] if pd.notna(d)]
        criteria_list = [c.upper().strip() for c in df_configuration["critere"] if pd.notna(c)]
        alternative_list = [a.upper().strip() for a in df_configuration["alternative"] if pd.notna(a)]
        
        #4. Dictionnaire des paramètres de configuration
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

        #5. Vérification de la présence de tous les paramètres nécessaires
        if any(value is None for value in dict_settings.values()) :
            return None
        else:
            return dict_settings

#Fonction permettant de récupérer le classement final depuis le fichier CSV
##Le fichier CSV est généré par le script gAHP_output.py
def get_rank(output_rank_file):
    ##########################A MODIFIER##########################
    ########################VERIFIER QU ON A TOUS LES FIHCIERS
    #1. Lancement du script gAHPInterface.py pour générer le classement
    subprocess.run(["python", "gAHPInterface.py"], cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "optimizationUnit")))

    #2. Vérification de l'existence du fichier de classement
    final_ranking = []
    try:
        #3. Lecture du fichier de classement
        with open(output_rank_file, mode = "r") as file_output_rank:
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

#Fonction permettant de générer le graphique des alternatives
def generate_alternative_graph(final_ranking, config_graph_file, config_graph_folder):
    #Trier par score décroissant
    final_ranking.sort(key = lambda x: x[1], reverse = False)

    #Extraction des scores des alternatives
    scores = [score for _, score in final_ranking]

    #Création de la figure et de son axe
    ##Utilisation de figsize pour ajuster la taille du graphique
    fig, ax = plt.subplots(figsize = (10, 2))

    #Configuration du titre et des labels
    fig.suptitle("Classement des alternatives", fontsize = 14, fontweight = 'bold', color = '#333333')
    
    #Tracer la droite de 0 à 1
    ax.hlines(y = 1, xmin = 0, xmax = 1, color = "#000000", linewidth = 2)

    #Tracer les points
    #zorder=3 pour que les points soient au-dessus de la ligne
    colors = [
        "#e42b2b" if score < 0.3 else
        "#ffa500" if score < 0.6 else 
        "#24b300"
        for score in scores]
    ax.scatter(scores, [1] * len(scores), color = colors, s = 100, zorder = 3)

    #Affichage des noms des alternatives
    ##Utilisation de defaultdict pour regrouper les scores proches
    ###1 : Regrouper les scores proches
    grouped_positions = defaultdict(list)
    for name, score in final_ranking :
        found_group = False
        for key in grouped_positions :
            if abs(score - key) <= 0.01 :  #Vérifier si le score est proche d'un groupe existant
                grouped_positions[key].append((name, score))
                found_group = True
                break
        if not found_group :    #Si le score n'est pas proche d'un groupe existant, on crée un nouveau groupe
            grouped_positions[score].append((name, score))

    ###2 : Afficher les noms + scores avec décalage Y progressif
    for group in grouped_positions.values() :
        for i, (name, score) in enumerate(group) :
            vertical_offset = 1.08 + i * 0.07  #Empilement clair, 0.07 d'écart
            color = (
                "#e42b2b" if score < 0.3 else
                "#ffa500" if score < 0.6 else
                "#24b300"
            )
            ax.text(score, vertical_offset, name, ha = 'center', va = 'bottom', color = color, rotation = 45, fontsize = 9)

    #Marger les axes
    ax.set_xlim(-0.05, 1.05)  #Marge pour être sûr de voir les extrémités
    ax.set_ylim(0.9, 1.3)     #Marge verticale pour bien voir les noms

    #Affichage des ticks pour 0 et 1
    ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    ax.set_xticklabels(['0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1'])
    ax.set_yticks([])         #Pas de ticks en y

    ax.grid(True, linestyle = '--', alpha = 0.5)  #Grille en arrière-plan
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    #Reconstitution du chemin d'accès au dossier de stockage du graphique
    base_main_utils_path = os.path.dirname(__file__)
    config_graph_folder_formated = os.path.abspath(os.path.join(base_main_utils_path, "..", config_graph_folder))
    if not os.path.exists(config_graph_folder_formated):
        os.makedirs(os.path.dirname(config_graph_folder_formated), exist_ok = True)

    config_graph_file_formated = config_graph_folder_formated + "/" + config_graph_file
    config_graph_file_formated = config_graph_file_formated.replace("\\", "/")  #Pour éviter les problèmes de chemin sous Windows
    
    plt.tight_layout()
    plt.savefig(config_graph_file_formated, dpi = 150)
    plt.close(fig)


import datetime

def export_config(company_name:str, decideurs_list:list, criteria_list:list, alternatives_list:list, kpis_list:list, assignements:dict):
    now = datetime.nom()
    folder_date = now.strftime("%d_%m_%y")
    folder_name = f"{company_name}_{folder_date}"
    
    base_path = os.path.dirname(__file__)
    config_dir = os.path.join(base_path, "static", "app_config", "app_config_entreprise")
    
    pass