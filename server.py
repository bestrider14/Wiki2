from flask import Flask, render_template, Response, request, jsonify, session, redirect, url_for, flash, json
from database import Database
from wtforms import StringField, Form
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
        session["userRole"] = 2
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
    if session['userRole'] == 0:
        return redirect(url_for("user"))
    if session['userRole'] == 1:
        return redirect(url_for("moderateur"))
    if session['userRole'] == 2:
        return redirect(url_for("admin"))


@app.route("/creeArticle", methods=['GET'])
def creeArticle():
    categories = database.get_all_categories()
    return render_template("creeArticle.html", categories=categories)

@app.route("/creeArticle", methods=['POST'])
def soumettreArticle():

    titre = request.form["titre"]
    categorie = request.form["categorie"]
    categorieParente = request.form["categorieParente"]
    contenu = request.form["contenuArticle"]
    try:
        compteurReference = int(request.form.get("referenceCount", 0))
    except ValueError:
        compteurReference = 0

    references = []

    if compteurReference:
        for i in range(compteurReference):
            cle = f'auteur[{i}]'
            auteur = request.form[cle]
            cle = f'titre[{i}]'
            titre = request.form[cle]
            cle = f'anneeParution[{i}]'
            anneeParution = request.form[cle]
            cle = f'isbn[{i}]'
            isbn = request.form[cle]
            cle = f'editeur[{i}]'
            editeur = request.form[cle]
            references.append({'auteur': auteur, 'titre': titre, 'anneeParution': anneeParution, 'isbn': isbn, 'editeur': editeur})
    print(references)
    print(len(references))
    #getuserID

    return redirect(url_for('index'))



@app.route("/add_comment", methods=["POST"])
def addComment():
    commentForm = request.form
    reussi = database.add_comment(commentForm["articleId"], commentForm["userId"], commentForm["comment"])
    if not reussi:
        flash("Une erreur est survenue.")
    return redirect(url_for("article") + "?id=" + commentForm["articleId"])


@app.route("/up")
def up():
    try:
        database.up()
        flash("Création de la base de données réussi!")
    except Exception as e:
        flash(str(e))
    return redirect(url_for("admin"))


@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    email = database.get_all_email()
    return Response(json.dumps(email), mimetype='application/json')


@app.route('/update_profile', methods=['POST'])
def update_name():
    try:
        nameForm = request.form
        user = nameForm["username"]
        database.update_profile(user, session["userId"])
    except Exception as e:
        flash(str(e))
    session["userName"] = user
    return redirect(url_for("user"))


@app.route('/update_password', methods=['POST'])
def update_password():
    mdpForm = request.form
    password = mdpForm["password"]
    database.update_password(password, session["userId"])
    return redirect(url_for("user"))

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
