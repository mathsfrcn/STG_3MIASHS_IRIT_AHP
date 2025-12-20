from flask import Flask, render_template, request, redirect, url_for
import csv

app = Flask(__name__)

# Page d'accueil de l'IHM
@app.route('/')
def index():
    return render_template('index.html')

# Route pour traiter les préférences
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Récupérer les préférences du formulaire
        preferences = {
            'nom': request.form['nom'],
            'pref_1': request.form['pref_1'],
            'pref_2': request.form['pref_2'],
            # Ajoutez d'autres préférences ici
        }

        # Sauvegarder dans un fichier CSV
        with open('preferences.csv', mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['nom', 'pref_1', 'pref_2'])
            writer.writerow(preferences)

        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)