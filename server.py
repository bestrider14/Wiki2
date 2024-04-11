import os

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_mail import Mail, Message
from datetime import datetime

from database import Database

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = os.urandom(24)

database = Database()


app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


mail = Mail(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET"])
def login():
    return render_template("connexion.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/validate_login", methods=["POST"])
def validate_login():
    form = request.form
    valideMDP = database.checkMDP(form["email"], form["motDePasse"])
    if valideMDP:
        userInfo = database.getUserInfo(form["email"])
        session["userId"] = userInfo[0]
        session["userName"] = userInfo[1].capitalize()
        session["userEmail"] = userInfo[2]
        session["userGenre"] = userInfo[3]
        session["userRole"] = userInfo[4]
        return redirect(url_for('index'))
    else:
        flash("Le nom d'utilisateur ou le mot de passe est invalide.")
        return redirect(url_for('login'))


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        data = request.form
        status = database.inscription(data["nomUtilisateur"], data["motDePasse"], data["email"], data["genre"])
        if status:  # si pas erreur
            flash("Inscription réussi")
            userInfo = database.getUserInfo(data["email"])
            session["userId"] = userInfo[0]
            session["userName"] = userInfo[1].capitalize()
            session["userEmail"] = userInfo[2]
            session["userGenre"] = userInfo[3]
            session["userRole"] = userInfo[4]
            return redirect(url_for('index'))
        else:
            flash("Une erreur est survenue lors de l'inscription.")
            return redirect(url_for('register'))
    else:
        return render_template("inscription.html")


@app.route("/get_user_role", methods=["POST"])
def get_user_role():
    email = request.get_json()["email"]
    role = database.getRole(email)
    return jsonify({"user_role": role})


@app.route("/findCatParent", methods=["POST"])
def findCatParent():
    childCat = request.get_json()["childCat"]
    parentCat = database.getCatParent(childCat)
    return jsonify({"parentCat": parentCat})


@app.route("/validate_user_registration", methods=["POST"])
def validate_user_registration():
    email = request.get_json()["email"]
    userExist = database.check_if_user_exists(email)
    if userExist:
        return jsonify({"user_exists": "True"})
    else:
        return jsonify({"user_exists": "False"})


@app.route('/privacy')
def privacy():
    return render_template('include/privacy.html')


@app.route("/articles")
def articles():
    letter = request.args.get('letter')
    liste_articles = database.find_article(letter)
    return render_template("articles.html", articles=liste_articles, letter=letter)


@app.route("/article")
def article():
    idArticle = request.args.get('id')

    if idArticle == "Random":
        idArticle = database.random_id()

    infoArticle = database.get_article(idArticle)
    infoCommentaires = database.get_info_commentaires(idArticle)

    return render_template("article.html", article=infoArticle, commentaires=infoCommentaires)


@app.route("/search", methods=["POST"])
def search():
    searchForm = request.form
    liste_articles = database.find_article(searchForm["keyword"])
    return render_template("resultats.html", articles=liste_articles, keyword=searchForm["keyword"])


@app.route("/setting")
def setting():
    if "userRole" in session:

        categories = database.get_all_categories()

        if session['userRole'] == 'utilisateur':
            return render_template("user.html")
        if session['userRole'] == 'moderateur':
            return render_template("moderateur.html", categories=categories)
        if session['userRole'] == 'administrateur':
            return render_template("admin.html", categories=categories)
    return redirect(url_for("login"))


@app.route("/creeArticle", methods=['GET'])
def creeArticle():
    categories = database.get_all_categories()
    return render_template("creeArticle.html", categories=categories)


@app.route("/soumettreArticle", methods=['POST'])
def soumettreArticle():
    # Récupérer l'ID de l'utilisateur
    if 'userId' in session:
        userID = session['userId']
    else:
        flash("Vous devez être connecté pour faire cette action")
        return redirect(url_for('login'))

    reference = {
        'auteur': request.form["auteur"],
        'titre': request.form["titreReference"],
        'anneeParution': request.form["anneeParution"],
        'isbn': request.form["isbn"],
        'editeur': request.form["editeur"]
    }

    article = {
        'titre': request.form["titreArticle"],
        'contenu': request.form["contenuArticle"],
        'nomCategorie': request.form["categorie"],
        'userID': userID,
    }

    # Récupérer l'id de la catégorie de l'article
    article['idCategorie'] = database.get_categorie_id(article['nomCategorie'])

    # ajout d'une référence
    try:
        result = database.add_reference(reference['auteur'], reference['titre'], reference['anneeParution'],
                                        reference['isbn'], reference['editeur'])
        if result:
            reference['idReference'] = result
        else:
            reference['idReference'] = None
    except Exception as e:
        flash("L'ajout de la référence à la base de donnée a échoué.", "error")
        print(f"Échec l'ajout de la référence à la base de donnée a échoué: {e}")
        return render_template('creeArticle.html')

    # ajout d'un article
    try:
        database.add_article(article['titre'], article['contenu'], article['idCategorie'], article['userID'],
                             reference['idReference'])
    except Exception as e:
        flash("L'ajout de l article a échoué.", "error")
        print(f"Échec l'ajout de la référence à la base de donnée a échoué: {e}")
        return render_template('creeArticle.html')

    flash("Insertion de l'article dans la base de donnée réussie !", "success")
    return redirect(url_for('index'))


@app.route("/addComment", methods=["POST"])
def addComment():
    commentForm = request.form
    reussi = database.add_comment(commentForm["articleId"], commentForm["userId"], commentForm["comment"])
    if not reussi:
        flash("Une erreur est survenue.")
    return redirect(url_for("article") + "?id=" + commentForm["articleId"])


@app.route("/up", methods=["POST"])
def up():
    if 'userRole' not in session:
        flash("Vous devez être connecté pour faire cette action.")
        return redirect(url_for("login"))

    if session['userRole'] != 'administrateur':
        flash("Vous devez être administrateur pour faire cette action.")
        return redirect(url_for("setting"))

    try:
        database.up()
        flash("Création de la base de données réussi!")
    except Exception as e:
        flash(str(e))
    return redirect(url_for("setting"))


@app.route('/_autocomplete_email', methods=['GET'])
def autocomplete_email():
    if 'userRole' not in session:
        flash("Vous devez être connecté pour faire cette action.")
        return redirect(url_for("login"))

    keyword = request.args.get('q')
    results = database.getEmailLike(keyword, session['userRole'])
    return jsonify(matching_results=results)


@app.route('/autocomplete_cat', methods=['GET'])
def autocomplete_cat():
    keyword = request.args.get('q')
    results = database.getCatLike(keyword)
    return jsonify(matching_results=results)


@app.route('/update_user_admin', methods=['POST'])
def update_user_admin():
    delete = request.form.get("delete_user") is not None
    data = request.form
    email = data["email"]
    role = data["role"]
    existe = database.check_if_user_exists(email)
    if not existe:
        flash("Le email n'existe pas.")
    if len(email) > 0 and existe:
        if delete:
            status = database.delete_account(email)
            if status:
                flash("Compte suprimer.")
            else:
                flash("Erreur lors de la suppression.")
            return redirect(url_for("setting"))
        if database.getRole(email) != role:
            status = database.update_role(role, email)
            if status:
                flash("Le role a bien été mis à jour.")
            else:
                flash("Erreur: Le role n'a pas été mis a jour.")
            return redirect(url_for("setting"))


@app.route('/update_profile', methods=['POST'])
def update_profile():
    userName = None
    try:
        nameForm = request.form
        userName = nameForm["username"]
        database.update_profile(userName, session["userId"])
    except Exception as e:
        flash(str(e))
    session["userName"] = userName
    return redirect(url_for("setting"))


@app.route('/update_password', methods=['POST'])
def update_password():
    mdpForm = request.form
    password = mdpForm["password"]
    database.update_password(password, session["userId"])
    return redirect(url_for("setting"))


@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if "userEmail" not in session:
        return redirect(url_for("login"))
    user_delete = session["userEmail"]
    status = database.delete_account(user_delete)

    if status:
        flash("Compte supprimer.")
        session.clear()
    else:
        flash("Une erreur est survenue.")

    return redirect(url_for("logout"))


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        if database.check_if_user_exists(email):

            password = database.reset_password_by_email(email)
            username = database.getUserInfo(email)[1]

            context = {
                "username": username,
                "password": password,
                "year": datetime.now().year
            }

            msg = Message('Votre nouveau mot de passe', sender='mailtrap@demomailtrap.com', recipients=[email],
                          html=render_template(template_name_or_list="email/emailNewPwd.html", **context))
            mail.send(msg)
            flash("Un nouveau mot de passe à été générer et envoyer à votre email.")
            return redirect(url_for("login"))
        else:
            flash("Ce email n'existe pas dans notre base de données.")
    return render_template("forgot_password.html")


if __name__ == '__main__':
    app.run()
