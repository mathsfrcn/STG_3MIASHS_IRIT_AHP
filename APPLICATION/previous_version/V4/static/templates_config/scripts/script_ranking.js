window.addEventListener("DOMContentLoaded", function () {
    const decideur = document.body.getAttribute("data-decideur");
    if (!decideur) {
        console.error("Aucun décideur trouvé.");
        return;
    }

    fetch(`/get_data/${decideur}`)
        .then(response => response.json())
        .then(data => {
            //Ajout du graph.png dans le container
            const containerGraph = document.getElementById("ranking-graph-container");
            containerGraph.innerHTML = "";
            const graphPath = data.graph_path;
            if (graphPath) {
                const graphLabel = document.createElement("label");
                graphLabel.setAttribute("for", "ranking-graph-image");
                graphLabel.textContent = "Graphique de classement :";
                containerGraph.appendChild(graphLabel);

                const graphImage = document.createElement("img");
                graphImage.src = graphPath;
                graphImage.alt = "Graphique de classement";
                graphImage.id = "ranking-graph-image";
                containerGraph.appendChild(graphImage);
            }

            //Récupération et affichage des KPI en fonction du décideur sélectionné
            const container = document.getElementById("kpi-group-container");
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

            data.kpis.forEach((kpi) => {
                const critereName = kpi.kpi_name.split('_')[0];

                if (criteriaList.includes(critereName)) {
                    const col = document.createElement("div");
                    col.classList.add("criteria-colomns");

                    col.innerHTML = `
                        <div class="criteria-title">
                            <h3>Critère ${critereName}</h3>
                        </div>
                        <div class="kpi-card">
                            <img src="${kpi.kpi_path}" alt="${kpi.kpi_name}">
                        </div>
                    `;
                    container.appendChild(col);
                }
            });

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
        });
});