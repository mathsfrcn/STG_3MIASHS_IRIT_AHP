// Internal data for configuration
let configData = {
    company_name: [],
    decideurs: [],
    criteres: [],
    alternatives: [],
    kpis: [],
    supervisorIndex: null
};

/**
 * Adds an item to the configuration lists
 * @param {string} type - 'decideur', 'criteria', 'alternative', or 'kpi'
 */
function addItem(type) {
    const input = document.getElementById(`new-${type}`);
    const value = input.value.trim();

    // Validation of limits
    if (type === 'decideur' && configData.decideurs.length >= 6) return alert("Maximum 6 décideurs.");
    if (type === 'critere' && configData.criteres.length >= 7) return alert("Maximum 7 critères.");
    if (type === 'alternative' && configData.alternatives.length >= 20) return alert("Maximum 20 alternatives.");

    if (value && !configData[`${type}s`].includes(value)) {
        configData[`${type}s`].push(value);
        input.value = '';
        renderList(type);
        generateMatrix(); // Assignment matrix update
    }
}

/**
 * Remove an item from the list
 */
function removeItem(type, index) {
    configData[`${type}s`].splice(index, 1);
    if (type === 'decideur' && configData.supervisorIndex === index) configData.supervisorIndex = null;
    renderList(type);
    generateMatrix();
}

/**
 * Displays the lists in the interface
 */
function renderList(type) {
    const container = document.getElementById(`${type}-list`);
    container.innerHTML = '';

    configData[`${type}s`].forEach((item, index) => {
        const li = document.createElement('li');
        li.className = 'list-item';
        
        let supervisorHtml = '';
        if (type === 'decideur') {
            // Choice of supervisor
            supervisorHtml = `
                <input type="radio" name="supervisor" id="sup-${index}" 
                       ${configData.supervisorIndex === index ? 'checked' : ''} 
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
    configData.supervisorIndex = index;
}

/**
 * Generates the KPI/Decision-maker/Criteria assignment matrix
 */
function generateMatrix() {
    const container = document.getElementById('kpi-assignment-matrix');
    
    if (configData.decideurs.length === 0 || configData.criteres.length === 0) {
        container.innerHTML = '<p class="empty-msg">Ajoutez des décideurs et des critères pour configurer les KPIs.</p>';
        return;
    }

    let tableHtml = `<table><thead><tr><th>Décideur \ Critère</th>`;
    configData.criteres.forEach(c => tableHtml += `<th>${c}</th>`);
    tableHtml += `</tr></thead><tbody>`;

    configData.decideurs.forEach((decideur, dIdx) => {
        tableHtml += `<tr><td><strong>${decideur}</strong></td>`;
        configData.criteres.forEach((critere, cIdx) => {
            tableHtml += `<td>
                <select name="kpi_map_${dIdx}_${cIdx}" required>
                    <option value="">--Choisir KPI--</option>
                    ${configData.kpis.map(k => `<option value="${k}">${k}</option>`).join('')}
                </select>
            </td>`;
        });
        tableHtml += `</tr>`;
    });

    tableHtml += `</tbody></table>`;
    container.innerHTML = tableHtml;
}

/**
 * Check all business constraints before sending to the server
 */
function validateForm(event) {
    // 1. Minimum number verification
    if (configData.decideurs.length < 1) {
        alert("Il faut au moins un décideur.");
        event.preventDefault();
        return false;
    }
    if (configData.criteres.length < 2) {
        alert("La méthode AHP nécessite au moins 2 critères.");
        event.preventDefault();
        return false;
    }
    if (configData.alternatives.length < 2) {
        alert("La méthode AHP nécessite au moins 2 alternatives.");
        event.preventDefault();
        return false;
    }

    // 2. Supervisor verification
    if (configData.supervisorIndex === null) {
        alert("Vous devez désigner un superviseur parmi les décideurs.");
        event.preventDefault();
        return false;
    }

    // 3. KPI Verification
    if (configData.kpis.length < configData.criteres.length) {
        alert(`Il manque des KPIs. Vous avez ${configData.criteres.length} critères, il faut donc au moins autant de KPIs.`);
        event.preventDefault();
        return false;
    }

    // 4. Verification of the assignment matrix
    const selects = document.querySelectorAll('#kpi-assignment-matrix select');
    let allAssigned = true;
    selects.forEach(select => {
        if (select.value === "") allAssigned = false;
    });

    if (!allAssigned) {
        alert("Toutes les cases de la matrice d'affectation KPI/Décideur doivent être remplies.");
        event.preventDefault();
        return false;
    }

    return true;
}

// Linking validation to the form
document.getElementById('config-form').addEventListener('submit', validateForm);