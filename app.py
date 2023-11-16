from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
import json
import os

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète'
bcrypt = Bcrypt(app)

# Chemin vers les fichiers JSON
users_data_file = 'users_data.json'
profiles_data_file = 'profiles_data.json'

# Si les fichiers JSON n'existent pas, créez-les avec une liste vide
if not os.path.exists(users_data_file):
    with open(users_data_file, 'w') as f:
        json.dump([], f)

if not os.path.exists(profiles_data_file):
    with open(profiles_data_file, 'w') as f:
        json.dump([], f)

# Page d'accueil
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/sign', methods=['GET', 'POST'])
def sign():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        name = request.form['name']
        email = request.form['email']
        raw_password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(raw_password).decode('utf-8')
        dob = request.form['dob']

        # Créer un dictionnaire avec les données d'inscription
        signup_data = {'name': name, 'email': email, 'password': hashed_password, 'dob': dob}

        # Stocker temporairement les données dans la session
        session['signup_data'] = signup_data

        # Charger les utilisateurs existants depuis le fichier JSON
        with open(users_data_file, 'r') as f:
            users_data = json.load(f)

        # Ajouter le nouvel utilisateur
        users_data.append(signup_data)

        # Enregistrer les utilisateurs mis à jour dans le fichier JSON
        with open(users_data_file, 'w') as f:
            json.dump(users_data, f)

        return redirect(url_for('profile'))

    return render_template('sign.html')

# Page de profil
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        # Récupérer les données du formulaire d'inscription depuis la session
        signup_data = session.get('signup_data', {})

        # Ajouter d'autres données du formulaire au dictionnaire
        signup_data.update({
            'phone': request.form.get('phone'),
            'category': request.form['category'],
            'description': request.form['description'],
            'diplomes': request.form['diplomes'],
            'photo': request.form['photo'],
            'pretention': request.form['pretention'],
            'logement': request.form['logement'],
            'region': request.form['region']
        })

        # Charger les profils existants depuis le fichier JSON
        with open(profiles_data_file, 'r') as f:
            profiles_data = json.load(f)

        # Ajouter le nouveau profil
        profiles_data.append(signup_data)

        # Enregistrer les profils mis à jour dans le fichier JSON
        with open(profiles_data_file, 'w') as f:
            json.dump(profiles_data, f)

        return redirect(url_for('login'))

    elif request.method == 'GET':
        # Récupérer les données de l'utilisateur depuis users_data.json s'il existe
        with open(users_data_file, 'r') as f:
            users_data = json.load(f)

        # Pré-remplir le formulaire si l'utilisateur existe
        if 'email' in session.get('signup_data', {}):
            user_email = session['signup_data']['email']
            existing_user = next((user for user in users_data if user['email'] == user_email), None)

            if existing_user:
                # Pré-remplir les champs du formulaire avec les données de l'utilisateur
                session['signup_data'].update({
                    'name': existing_user['name'],
                    'dob': existing_user['dob'],
                    'email': existing_user['email']
                })

    return render_template('profile.html', signup_data=session.get('signup_data', {}))

# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Charger les utilisateurs depuis le fichier JSON
        with open(users_data_file, 'r') as f:
            users_data = json.load(f)

        # Vérifier si l'utilisateur existe et les informations de connexion sont correctes
        for user in users_data:
            if user['email'] == email and bcrypt.check_password_hash(user['password'], password):
                session['user'] = user
                return redirect(url_for('dashboard'))

    return render_template('connexion.html')

# Page de tableau de bord
@app.route('/dashboard')
def dashboard():
    # Vérifier si l'utilisateur est connecté
    if 'user' not in session:
        return redirect(url_for('login'))

    # Récupérer les informations de profil de l'utilisateur à partir du fichier JSON
    with open(profiles_data_file, 'r') as f:
        profiles_data = json.load(f)

    # Récupérer l'e-mail de l'utilisateur connecté
    user_email = session['user']['email']

    # Trouver le profil correspondant à l'e-mail de l'utilisateur
    user_profile = next((profile for profile in profiles_data if profile['email'] == user_email), None)

    if user_profile is None:
        # Gérer le cas où le profil de l'utilisateur n'est pas trouvé
        return "Profil non trouvé."

    return render_template('dashboard.html', user=session['user'], user_profile=user_profile)

if __name__ == '__main__':
    app.run(debug=True)
