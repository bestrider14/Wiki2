from flask import Flask, render_template, Response, request, jsonify, session, redirect, url_for, flash
from database import Database
import os

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = os.urandom(24)

database = Database()


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
        print(userInfo)
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
    migration_state = database.get_migration_stack_size()
    return render_template("admin.html", migration_state=migration_state)


@app.route("/articles")
def articles():
    letter = request.args.get('letter')
    liste_articles = database.find_article(letter)
    return render_template("articles.html", articles=liste_articles, letter=letter)


@app.route("/article")
def article():
    idArticle = request.args.get('id')
    infoArticle = database.get_article(idArticle)
    return render_template("article.html", article=infoArticle)


@app.route("/random")
def random():
    idArticle = database.random_id()
    infoArticle = database.get_article(idArticle)
    return render_template("article.html", article=infoArticle)


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


@app.route("/up", methods=["POST"])
def up():
    try:
        database.up()
        return Response(status=200)
    except Exception as e:
        print(e)
        return Response(status=406)


if __name__ == '__main__':
    app.run()
