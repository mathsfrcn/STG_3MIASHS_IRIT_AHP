//Récupération des données passées depuis le backend
document.getElementById("decideur").addEventListener("change", function () {
    const decideur = this.value;

    //Récupération et traitement de chaque KPI en fonction du décideur sélectionné
    fetch(`/get_data/${decideur}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("preference-columns-container");

            container.innerHTML = "";

            //Vérification que la liste des critères est valide
            const criteriaList = data.criteria_list;
            if (!criteriaList || criteriaList.length === 0) {
                container.innerHTML = `
                <div class="warning-message">
                    <strong>Attention :</strong>    
                    <p>Aucun critère disponible pour ce décideur.</p>
                </div>
                `;
                return;
            }

            //Vérification que la liste des alternatives est valide
            const alternativeList = data.alternative_list;
            if (!alternativeList || alternativeList.length === 0) {
                container.innerHTML = `
                    <div class="warning-message">
                        <strong>Attention :</strong>
                        <p>Aucune alternative disponible pour ce décideur.</p>
                    </div>
                    `;
                return;
            }

            //Création des colonnes pour chaque critère et KPI
            data.kpis.forEach((kpi, kpi_index) => {
                const critereName = kpi.kpi_name.split('_')[0]; //Format attendu : NOM-CRITERE_NOM-KPI
                            
                if (criteriaList.includes(critereName)) {   //Vérification que le critère est bien dans la liste des critères
                    const col = document.createElement("div");
                    col.classList.add("criteria-colomns");   //Chaque critère sera regroupé dans une div
                                
                    const critereId = `preference_critere_${critereName}_${kpi_index}`;

                    //En-tête de la colonne et slider pour le critère
                    col.innerHTML = `
                        <div class="criteria-title">
                            <h3>Critère ${critereName}</h3>
                        </div>
                        <div class="preference-criteria">
                            <label for="preference_critere_${critereId}">${critereName}</label>
                            <input
                                type="range"
                                id="${critereId}" 
                                name="preference_critere" 
                                min="1"
                                max="9"
                                step="1"
                                value="5"
                                data-target="val_${critereId}"
                                class="colored-slider"
                            >
                            <span id="val_${critereId}">5</span>
                        </div>
                        <br>
                    `;

                    //KPI
                    col.innerHTML += `
                        <div class="kpi-card">
                            <img src="${kpi.kpi_path}" alt="${kpi.kpi_name}">
                        </div>
                    `;

                    //Sliders pour chaque alternative
                    alternativeList.forEach((alt, a_index) => {
                        const alternativeId = `preference_alternative_${kpi_index}_${a_index}`;
                        col.innerHTML += `
                            <div class="preference-alternative">
                                <label for="${alternativeId}">${alt}</label>
                                <input 
                                    type="range" 
                                    id="${alternativeId}"
                                    name="${alternativeId}" 
                                    min="1" 
                                    max="9" 
                                    value="5" 
                                    step="1" 
                                    data-target="val_${alternativeId}"
                                    class="colored-slider"
                                >
                                <span id="val_${alternativeId}">5</span>
                            </div>
                        `;
                    });
                    //Ajout de la colonne au conteneur
                    container.appendChild(col);
                }
            });

            //Ajout d'un message d'erreur si un dossier ne contient pas le bon nombre de KPI
            if (data.warnings && data.warnings.length > 0) {
                let warning = document.createElement("div");
                warning.classList.add("warning-message");
                warning.innerHTML = `
                    <div class="warning-message">
                        <strong>Problèmes détectés :</strong>
                        <p>${data.warnings.join("<br>")}</p>
                    </div>
                `;
                container.appendChild(warning);
            }

            //Traitement des objets range
            //Renvoie pour affichage de la valeur de l'objet sélectionné
            const sliders = document.querySelectorAll("input[type='range']");
            sliders.forEach(slider => {
                slider.addEventListener("input", function () {
                    const targetId = this.getAttribute("data-target");  //Chaque range est reconnue par son id
                    const targetSpan = document.getElementById(targetId);
                    if (targetSpan) {
                        targetSpan.textContent = this.value;
                    }
                });

                //Mise à jour de la couleur des objets range en fonction de sa valeur
                function updateColor() {
                    const val = parseInt(slider.value);
                    slider.classList.remove('red', 'orange', 'green');
                    if (val < 3) {
                        slider.classList.add('red');
                    } else if (val <= 6) {
                        slider.classList.add('orange');
                    } else {
                        slider.classList.add('green');
                    }
                }

                updateColor();
                slider.addEventListener("input", updateColor);
            });
        });
});

//Déclenche une première fois au chargement pour afficher les données par défaut
window.addEventListener("DOMContentLoaded", function () {
    document.getElementById("decideur").dispatchEvent(new Event("change"));
});