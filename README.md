# 🏭 Aide à la Décision Collaborative - Industrie 5.0 (AHP)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Termin%C3%A9-brightgreen)
![Version](https://img.shields.io/badge/Version-v12.5-blue)

Ce projet implémente une application web interactive dédiée à la prise de décision multicritère en environnement industriel. Il intègre un modèle d'optimisation mathématique en Julia exploitant la méthode AHP (Analytic Hierarchy Process) pour agréger les préférences de plusieurs décideurs. L'objectif est de placer l'humain au cœur du processus de production (Industrie 5.0) en facilitant le consensus via une interface numérique intuitive

## 📋 Table des Matières

-  Fonctionnalités
-  Modélisation et Technologie
-  Installation
-  Utilisation
-  Structure du Projet
-  Auteurs et Encadrement

## ✨ Fonctionnalités

### 1. Configuration Dynamique (Excel/VBA)
Paramétrage complet du serveur via configurationApp.xlsm sans toucher au code. Définition des décideurs, critères, alternatives et indicateurs de performance (KPI).Génération automatique de l'architecture des dossiers pour chaque entreprise.

### 2. Collecte des Préférences (IHM 1)
Interface web permettant à chaque décideur de saisir son niveau d'expertise par critère. Évaluation des alternatives via des curseurs interactifs changeant de couleur selon la valeur. Visualisation des KPIs personnalisés sous forme de graphiques pour éclairer le choix.

### 3. Modèle d'Optimisation Julia
Calcul de la cohérence des données pour assurer la fiabilité des jugements. Agrégation des matrices de décision par moyenne arithmétique pondérée. Calcul du classement final des alternatives à haute performance numérique. 

### 4. Restitution et Validation (IHM 2)
Affichage du classement final et génération d'un graphique des scores via matplotlib. Interface spécifique pour le Superviseur afin de valider l'alternative retenue. Export de la décision finale au format .txt pour archivage et preuve écrite

## 🛠️ Modélisation Physique
L'agrégation des préférences suit la logique hiérarchique de Saaty. Le calcul du vecteur de priorité $w$ est réalisé par le modèle Julia pour résoudre :$$A \cdot w = \lambda_{max} \cdot w$$Où $A$ représente la matrice de comparaison par paires agrégée

## 🚀 Installation

### 0. Cloner le dépôt :
    ```
    git clone [https://github.com/winston2968/Projet-Simulation-Aleatoire.git](https://github.com/winston2968/Projet-Simulation-Aleatoire.git)
    ```

### 1. Prérequis Python
Installez les dépendances via pip :

```Python
  pip install flask numpy pandas matplotlib waitress secrets
```

### 2. Prérequis Julia
Dans le terminal Julia, installez les packages nécessaires : Juliausing Pkg

```Julia
  Pkg.add(["LinearAlgebra", "Statistics", "CSV", "DataFrames"])
````

### 3. Liaison Python-Julia
Configurez PyCall et pyjulia pour permettre la communication entre les deux langages : 
-  Installation de PyCall.jl
-  Installation de pyjulia

## 🎮 Utilisation

### Étape 1 : Paramétrage
Ouvrez configurationApp.xlsm.Modifiez l'adresse locale dans le formulaire UsfCreationEtape3. Renseignez les données (Décideurs, Critères, etc.) et cliquez sur Télécharger pour créer le fichier de configuration CSV.

### Étape 2 : Lancement du serveurBashpython run.py
Le serveur s'exécute via Waitress sur le port 5000.

### Étape 3 : Processus décisionnel
Les décideurs accèdent à l'URL indiquée dans le terminal pour remplir l'IHM 1. Une fois tous les votes reçus, l'IHM 2 s'actualise automatiquement pour afficher les résultats.

## 📂 Structure du Projet

```Bash
├── configurationApp.xlsm     # Interface VBA de paramétrage
├── run.py                    # Point d'entrée du serveur Flask/Waitress
├── app/
│   ├── routes.py             # Gestion des requêtes HTTP (IHM 1, IHM 2)
│   ├── optimizationUnit/
│   │   ├── gAHPInterface.py  # Interface Python vers Julia
│   │   └── gAHPOptimizationUnit.jl # Modèle d'optimisation AHP
│   ├── static/               # CSS, JS, Images des KPIs et Graphes
│   └── templates/            # Pages HTML (Jinja2)
├── output/                   # Résultats (CSV classements, TXT décisions)
└── README.md                 # Documentation
```

## 👥 Auteurs et Encadrement

-  Ce projet a été réalisé en 2025 au sein du laboratoire IRIT (Équipe ADRIA).
-  Auteur : FRANCINE-HABAS Mathis.
-  Tuteurs de Thèse : TRAVERSAC Jérémy & GALASSO François.
-  Tuteur Pédagogique : FERRATY Frédéric (Université Toulouse II).

Note : Cette application est une première version fonctionnelle destinée aux PME/TPE industrielles.
