from flask import Flask, render_template, Response, request
from database import Database

app = Flask(__name__)
database = Database()


@app.route("/")
def index():
    return render_template("index.html")


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
