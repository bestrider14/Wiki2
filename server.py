import pymysql
from flask import Flask, render_template, Response, request, url_for, redirect
import bcrypt
from database import Database

app = Flask(__name__)
database = Database()


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
        # avoir un choix d'utilisateur sous format 1 pour modérateur, 0 pour utilisateur
        choixTypeUtilisateur = request.form.get("choixTypeUtilisateur")
        typeUtilisateur = 1 if choixTypeUtilisateur == 'moderateur' else 0
        # hasher le mot de passe de l'utilisateur
        motDePasseForm = request.form.get("motDePasse")
        motPasseEnBytes = motDePasseForm.encode('utf-8')
        motDePasseHash = bcrypt.hashpw(motPasseEnBytes, bcrypt.gensalt())

        # ouvrir une connection
        connection = database.get_connection()
        cursor = connection.cursor()

        # Préparer la requête SQL
        requete = "INSERT INTO utilisateurs (nom, motDePasse, email, genre, role) VALUES (%s, %s, %s, %s, %s)"
        data = (nom, motDePasseHash, email, genre, typeUtilisateur)

        # Envoyer la requete
        try:
            cursor.execute(requete, data)
            connection.commit()
            return redirect(url_for('index') + '?message=Inscription réussie !')

        except pymysql.MySQLError as e:
            print(e)
            connection.rollback()
            return redirect(url_for('inscription') + f'?message=Erreur à l inscription ${e}')

        finally:
            cursor.close()
    else:
        return render_template('inscription.html')


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
