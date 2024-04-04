from datetime import datetime
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

    def get_info_commentaires(self, idarticle):
        statement = (f"SELECT messages.contenu, messages.horodatage, utilisateurs.nom "
                     f"FROM messages INNER JOIN utilisateurs ON messages.idUtilisateur = utilisateurs.idUtilisateur "
                     f"WHERE messages.idArticle = %s ORDER BY messages.horodatage DESC;")
        data = idarticle
        self.cursor.execute(statement, data)

        liste = [list(x) for x in self.cursor.fetchall()]

        for x in liste:
            seconds = (datetime.today() - x[1]).total_seconds()
            x[1] = f"1 seconde"
            if seconds > 31536000:
                time = seconds // 31536000
                if time == 1:
                    x[1] = f"{time:.0f} an"
                else:
                    x[1] = f"{time:.0f} ans"
            elif seconds > 86400:
                time = seconds // 86400
                if time == 1:
                    x[1] = f"{time:.0f} jour"
                else:
                    x[1] = f"{time:.0f} jours"
            elif seconds > 3600:
                time = seconds // 3600
                if time == 1:
                    x[1] = f"{time:.0f} heure"
                else:
                    x[1] = f"{time:.0f} heures"
            elif seconds > 60:
                time = seconds // 60
                if time == 1:
                    x[1] = f"{time:.0f} minute"
                else:
                    x[1] = f"{time:.0f} minutes"
            elif seconds > 1:
                time = seconds
                if time == 1:
                    x[1] = f"{time:.0f} seconde"
                else:
                    x[1] = f"{time:.0f} secondes"
        return liste

    def add_comment(self, articleid, userid, comment):
        statement = f"INSERT INTO messages (contenu, horodatage, idArticle, idUtilisateur) VALUES (%s, NOW(), %s, %s);"
        data = comment, articleid, userid

        try:
            self.cursor.execute(statement, data)
            return True

        except pymysql.MySQLError as e:
            print(e)
            return False

    def get_all_email(self):
        statement = f"SELECT utilisateurs.email FROM utilisateurs;"
        self.cursor.execute(statement)
        liste = []
        for email in self.cursor.fetchall():
            liste.append(email[0])
        return liste

    def update_profile(self, nom, id):
        statement = f"UPDATE utilisateurs SET nom = %s WHERE idUtilisateur = %s;"
        data = nom, id
        self.cursor.execute(statement, data)
        return "Modification du nom d'utilisateur réussi"

    def update_password(self, motDePasse, id):
        statement = "UPDATE utilisateurs SET motDePasse = md5(%s) WHERE idUtilisateur = %s;"
        data = motDePasse, id
        self.cursor.execute(statement, data)
        return "Modification du mot de passe réussi"

    def delete_account(self, id):
        statement = "DELETE FROM utilisateurs WHERE idUtilisateur = %s;"
        data = id
        self.cursor.execute(statement, data)
        return "Suppression du compte réussi"