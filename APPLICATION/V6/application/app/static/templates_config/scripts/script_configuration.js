// Données internes pour la configuration (Vos nouveaux noms de variables)
let configData = {
    decideurs_list : [],
    criteria_list : [],
    alternatives_list : [],
    kpis_list : [],
    supervisor_id : null
};

// Correspondance entre le "type" envoyé par les boutons et vos variables
const keyMap = {
    'decideur': 'decideurs_list',
    'criteria': 'criteria_list',
    'alternative': 'alternatives_list',
    'kpi': 'kpis_list'
};

/**
 * Ajoute un élément aux listes de configuration
 * @param {string} type - 'decideur', 'critere', 'alternative', ou 'kpi'
 */
function addItem(type) {
    const input = document.getElementById(`new-${type}`);
    if (!input) return;

    const value = input.value.trim();
    const listKey = keyMap[type]; // On récupère le nom de la variable (ex: decideurs_list)

    // Validation des limites (Source: Rapport )
    if (type === 'decideur' && configData.decideurs_list.length >= 6) return alert("Maximum 6 décideurs.");
    if (type === 'critere' && configData.criteria_list.length >= 7) return alert("Maximum 7 critères.");
    if (type === 'alternative' && configData.alternatives_list.length >= 20) return alert("Maximum 20 alternatives.");

    // Vérification de doublon et ajout
    if (value && !configData[listKey].includes(value)) {
        configData[listKey].push(value);
        input.value = '';
        renderList(type);
        generateMatrix(); 
    }
}

/**
 * Supprime un élément de la liste
 */
function removeItem(type, index) {
    const listKey = keyMap[type];
    configData[listKey].splice(index, 1);

    // Si on supprime le superviseur, on réinitialise l'ID 
    if (type === 'decideur' && configData.supervisor_id === index) {
        configData.supervisor_id = null;
    }
    
    renderList(type);
    generateMatrix();
}

/**
 * Affiche les listes dans l'interface
 */
function renderList(type) {
    const container = document.getElementById(`${type}-list`);
    const listKey = keyMap[type];
    container.innerHTML = '';

    configData[listKey].forEach((item, index) => {
        const li = document.createElement('li');
        li.className = 'list-item';
        
        let supervisorHtml = '';
        if (type === 'decideur') {
            // Gestion du rôle de superviseur unique [cite: 214]
            supervisorHtml = `
                <input type="radio" name="supervisor" id="sup-${index}" 
                       ${configData.supervisor_id === index ? 'checked' : ''} 
                       onclick="setSupervisor(${index})">
                <label for="sup-${index}">Sup.</label>
            `;
        }

        li.innerHTML = `
            <span>${item}</span>
            <div class="actions">
                ${supervisorHtml}
                <button type="button" class="btn-delete" onclick="removeItem('${type}', ${index})">×</button>
            </div>
        `;
        container.appendChild(li);
    });
}

function setSupervisor(index) {
    configData.supervisor_id = index;
}

/**
 * Génère la matrice d'affectation
 */
function generateMatrix() {
    const container = document.getElementById('kpi-assignment-matrix');
    
    if (configData.decideurs_list.length === 0 || configData.criteria_list.length === 0) {
        container.innerHTML = '<p class="empty-msg">Ajoutez des décideurs et des critères pour configurer les kpis.</p>';
        return;
    }

    let tableHtml = `<table><thead><tr><th>Décideur \\ Critère</th>`;
    configData.criteria_list.forEach(c => tableHtml += `<th>${c}</th>`);
    tableHtml += `</tr></thead><tbody>`;

    configData.decideurs_list.forEach((decideur, dIdx) => {
        tableHtml += `<tr><td><strong>${decideur}</strong></td>`;
        configData.criteria_list.forEach((critere, cIdx) => {
            tableHtml += `<td>
                <select name="kpi_map_${dIdx}_${cIdx}" required>
                    <option value="">--Choisir KPI--</option>
                    ${configData.kpis_list.map(k => `<option value="${k}">${k}</option>`).join('')}
                </select>
            </td>`;
        });
        tableHtml += `</tr>`;
    });

    tableHtml += `</tbody></table>`;
    container.innerHTML = tableHtml;
}

/**
 * Validation finale avant envoi
 */
async function validateForm(event) {
    event.preventDefault(); // Bloque l'envoi classique pour utiliser fetch

    // Validations existantes...
    if (configData.decideurs_list.length < 1 || configData.criteria_list.length < 2) {
        alert("Configuration incomplète.");
        return false;
    }
    if (configData.supervisor_id === null) {
        alert("Désignez un superviseur.");
        return false;
    }

    // Récupération du nom de l'entreprise
    const companyName = document.getElementById('company-name').value;

    // Récupération de la matrice d'affectation (kpi_map_...)
    const assignments = {};
    const selects = document.querySelectorAll('#kpi-assignment-matrix select');
    selects.forEach(select => {
        assignments[select.name] = select.value;
    });

    // Construction du pack de données complet [cite: 394, 395, 396]
    const payload = {
        company_name: companyName,
        decideurs_list: configData.decideurs_list,
        criteria_list: configData.criteria_list,
        alternatives_list: configData.alternatives_list,
        kpis_list: configData.kpis_list,
        supervisor_id: configData.supervisor_id,
        assignments: assignments
    };

    // Envoi au serveur Flask [cite: 278, 286]
    try {
        const response = await fetch('/submit_configuration', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("Configuration enregistrée avec succès !");
            window.location.href = "/"; // Redirection vers l'accueil
        } else {
            alert("Erreur lors de l'enregistrement.");
        }
    } catch (error) {
        console.error("Erreur:", error);
    }
}

document.getElementById('config-form').addEventListener('submit', validateForm);