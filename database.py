import bcrypt
import pymysql
import os
from dotenv import load_dotenv
from sql_utils import run_sql_file


class Database:
    def __init__(self):

        load_dotenv()

        self.host = os.environ.get('HOST')
        self.port = int(os.environ.get("PORT"))
        self.database = os.environ.get("DATABASE")
        self.user = os.environ.get("USER")
        self.password = os.environ.get("PASSWORD")

        self._open_sql_connection()
        self.migration_counter = 0
        self.liste_articles = []

    def _open_sql_connection(self):
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.database,
            autocommit=True
        )
        self.cursor = self.connection.cursor()

    def push_migration(self):
        migration_to_push = self.migration_counter + 1
        migration_file = f"db_scripts/migrate_{migration_to_push}.sql"

        run_sql_file(self.cursor, migration_file, accept_empty=False)
        self.migration_counter += 1

    def rollback(self):
        if self.migration_counter < 1:
            raise ValueError("There are no rollbacks in the rollback stack.")

        rollback_file = f"db_scripts/rollback_{self.migration_counter}.sql"

        run_sql_file(self.cursor, rollback_file)
        self.migration_counter -= 1

    def up(self):
        self.drop()
        run_sql_file(self.cursor, "db_scripts/up.sql")

    def drop(self):
        run_sql_file(self.cursor, "db_scripts/drop.sql")
        self.migration_counter = 0

    def get_cursor(self):
        return self.cursor

    def get_connection(self):
        return self.connection

    def get_migration_stack_size(self):
        return self.migration_counter

    def find_article(self, keyword):
        statement = (f"SELECT articles.titre, articles.dateCreation, utilisateurs.nom, articles.idArticle "
                     f"FROM articles INNER JOIN utilisateurs ON articles.idCreateur = utilisateurs.idUtilisateur "
                     f"WHERE articles.titre LIKE %s ORDER BY articles.titre;")

        if len(keyword) > 1:
            data = '%' + keyword + '%'
        else:
            data = keyword + '%'

        self.cursor.execute(statement, data)

        liste = [x for x in self.cursor.fetchall()]
        return liste

    def get_article(self, idarticle):
        statement = f"call infoArticle('{idarticle}')"
        self.cursor.execute(statement)

        return self.cursor.fetchone()

    def random_id(self):
        statement = f"SELECT articles.idArticle FROM articles ORDER BY RAND() LIMIT 1;"
        self.cursor.execute(statement)

        return self.cursor.fetchone()[0]

    def checkMDP(self, email, password):
        statement = f"CALL compMDP(%s, %s);"
        data = (email, password)
        self.cursor.execute(statement, data)
        return self.cursor.fetchone()[0]

    def check_if_user_exists(self, email):
        statement = f"SELECT COUNT(*) FROM utilisateurs WHERE utilisateurs.email = %s;"
        data = email
        self.cursor.execute(statement, data)
        return self.cursor.fetchone()[0]

    def inscription(self, nom, mdp, email, genre):
        # Préparer la requête SQL
        requete = "INSERT INTO utilisateurs (nom, motDePasse, email, genre, role) VALUES (%s, MD5(%s), %s, %s, %s)"
        data = (nom, mdp, email, genre, 0)

        # Envoyer la requete
        try:
            self.cursor.execute(requete, data)
            return "Inscription réussie"

        except pymysql.MySQLError as e:
            print(e)
            return "Erreur à l inscription"

    def getUserInfo(self, email):
        statement = f"SELECT utilisateurs.idUtilisateur, utilisateurs.nom, utilisateurs.email, utilisateurs.genre, utilisateurs.role FROM utilisateurs WHERE utilisateurs.email = %s;"
        data = email
        self.cursor.execute(statement, data)
        return self.cursor.fetchone()

