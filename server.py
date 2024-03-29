from flask import Flask, render_template, Response, request, url_for, redirect
import bcrypt
from database import Database
from Utilisateur import Utilisateur

app = Flask(__name__)
database = Database()
user = Utilisateur()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        # récupérer les données de la form
        nom = request.form.get("nomUtilisateur")
        email = request.form.get("email")
        genre = request.form.get("choixGenre")

        # hasher le mot de passe de l'utilisateur
        motDePasseForm = request.form.get("motDePasse")
        motPasseEnBytes = motDePasseForm.encode('utf-8')
        motDePasseHash = bcrypt.hashpw(motPasseEnBytes, bcrypt.gensalt())

        msg = database.inscription(nom, motDePasseHash, email, genre)

        return redirect(url_for('inscription') + f'?message={msg}')

    else:
        return render_template('inscription.html')


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    if request.method == 'POST':
        data = request.get_json()
        nom = data['username']
        motDePasse = data['password']
        if database.connexion(nom, motDePasse, user):
            print(user.getInfoUtilisateur())
            return render_template('index.html', logIn=True)
        else:
            return render_template('connexion.html', error=True)
    return render_template('connexion.html', error=False)


@app.route("/admin")
def admin():
    migration_state = database.get_migration_stack_size()
    return render_template("admin.html", migration_state=migration_state)


@app.route("/articles", methods=["GET"])
def articles():
    letter = request.args.get('letter')
    liste_articles = database.get_liste_articles_starting_with(letter)
    return render_template("articles.html", articles=liste_articles, letter=letter)


@app.route("/article", methods=["GET"])
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
    keyword = request.json
    listeArticle = database.find_article(keyword["text"])
    #    infoArticle = database.get_article(idArticle)
    print(listeArticle)
    return render_template("article.html", article=1)


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
