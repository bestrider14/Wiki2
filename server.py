from flask import Flask, render_template, Response, request, jsonify, session, redirect, url_for, flash, json
from database import Database
from datetime import date
import os

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = os.urandom(24)

database = Database()

# FOR DEBUG ONLY
autologin = True


@app.route("/")
def index():
    # FOR DEBUG ONLY
    if autologin:
        print("auto login")
        session["userId"] = 204
        session["userName"] = "Johny"
        session["userEmail"] = "jb@gmail.com"
        session["userGenre"] = "Masculin"
        session["userRole"] = "moderateur"
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
        database.inscription(data["nomUtilisateur"], data["motDePasse"], data["email"], data["genre"])
        return render_template("index.html")
    else:
        return render_template("inscription.html")


@app.route("/validate_user_registration", methods=["POST"])
def validate_user_registration():
    if request.method == "POST":
        email = request.get_json()["email"]
        userExist = database.check_if_user_exists(email)
        if userExist:
            return jsonify({"user_exists": "True"})
        else:
            return jsonify({"user_exists": "False"})
    return


@app.route("/user")
def user():
    return render_template("user.html")


@app.route("/moderateur")
def moderateur():
    return render_template("moderateur.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


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


@app.route("/checkRole")
def checkRole():
    if "userRole" in session:
        if session['userRole'] == 'utilisateur':
            return redirect(url_for("user"))
        if session['userRole'] == 'moderateur':
            return redirect(url_for("moderateur"))
        if session['userRole'] == 'administrateur':
            return redirect(url_for("admin"))
    return redirect(url_for("login"))


@app.route("/creeArticle", methods=['GET'])
def creeArticle():
    categories = database.get_all_categories()
    return render_template("creeArticle.html", categories=categories)


@app.route("/creeArticle", methods=['POST'])
def soumettreArticle():
    if 'userID' in session:
        userID = session['userID']
    else:
        return redirect(url_for('login'))

    contenuArticle = {
        'titre': request.form["titreArticle"],
        'contenu': request.form["contenuArticle"],
        'dateCreation': date.today().isoformat(),
        # Il faut avoir l'idCategorie, pas juste la catégorie... faire une requête database
        'categorie': request.form["categorie"],
        'categorieParente': request.form["categorieParente"],
        'idCreateur': userID,
    }

    references = {
        'titre': request.form["titreReference"],
        'auteur': request.form["auteur"],
        'annee': request.form["anneeParution"],
        'isbn': request.form["isbn"],
        'editeur': request.form["editeur"]
    }

    # print(contenuArticle)
    # print(references)

    return redirect(url_for('index'))


@app.route("/add_comment", methods=["POST"])
def addComment():
    commentForm = request.form
    reussi = database.add_comment(commentForm["articleId"], commentForm["userId"], commentForm["comment"])
    if not reussi:
        flash("Une erreur est survenue.")
    return redirect(url_for("article") + "?id=" + commentForm["articleId"])


@app.route("/up", methods=["POST"])
def up():
    if 'userRole' not in session:
        flash("Vous devez être connecté pour faire cette action")
        return redirect(url_for("login"))

    if session['userRole'] != 'administrateur':
        flash("Vous devez être administrateur pour faire cette action")
        return redirect(url_for("admin"))

    try:
        database.up()
        flash("Création de la base de données réussi!")
    except Exception as e:
        flash(str(e))
    return redirect(url_for("admin"))


@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    if 'userRole' not in session:
        flash("Vous devez être connecté pour faire cette action")
        return redirect(url_for("login"))

    email = database.get_email(session['userRole'])
    return Response(json.dumps(email), mimetype='application/json')


@app.route('/update_profile', methods=['POST'])
def update_name():
    userName = None
    try:
        nameForm = request.form
        userName = nameForm["username"]
        database.update_profile(userName, session["userId"])
    except Exception as e:
        flash(str(e))
    session["userName"] = userName
    return redirect(url_for("checkRole"))


@app.route('/update_password', methods=['POST'])
def update_password():
    mdpForm = request.form
    password = mdpForm["password"]
    database.update_password(password, session["userId"])
    return redirect(url_for("checkRole"))


@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if "userId" not in session:
        return redirect(url_for("login"))
    user_delete = session["userId"]
    database.delete_account(user_delete)
    session.clear()
    return redirect(url_for("logout"))


@app.route('/deleted_account')
def deleted_account():
    return "Votre compte a bien été supprimé."


if __name__ == '__main__':
    app.run()
