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
    id = request.args.get('id')
    article = database.get_article(id)
    return render_template("article.html", article=article)


@app.route("/migrate", methods=["POST"])
def migrate():
    try:
        database.push_migration()
        return Response(status=200)
    except Exception as e:
        print(e)
        return Response(status=406)


@app.route("/up", methods=["POST"])
def up():
    try:
        database.up()
        return Response(status=200)
    except Exception as e:
        print(e)
        return Response(status=406)


@app.route("/rollback", methods=["POST"])
def rollback():
    try:
        database.rollback()
        return Response(status=200)
    except Exception as e:
        print(e)
        return Response(status=406)


if __name__ == '__main__':
    app.run()