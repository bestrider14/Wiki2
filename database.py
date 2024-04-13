import os
import string
from datetime import datetime, date
import random

import pymysql
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

    def get_all_categories(self):
        statement = f"SELECT nom FROM categories;"
        self.cursor.execute(statement)

        liste = []
        for cat in self.cursor.fetchall():
            liste.append(cat[0])
        return liste

    def get_titres_refs(self):
        statement = f"SELECT refs.titreDocument FROM refs;"
        self.cursor.execute(statement)
        liste = []
        for email in self.cursor.fetchall():
            liste.append(email[0])
        return liste

    def get_categorie_id(self, nom):
        self.cursor.execute("SELECT idCategorie FROM categories WHERE nom = %s;", nom)
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def set_categorie(self, nom, idCategorieParent):
        try:
            assert idCategorieParent is not None
            assert nom is not None
            assert self.get_categorie_id(nom) is None
            self.cursor.execute("INSERT INTO categories (nom, idCategorieParent) VALUE (%s, %s)",
                                (nom, idCategorieParent))
        except AssertionError as e:
            print(f"Erreur d'insertion d'une nouvelle catégorie {e}")
        finally:
            return self.cursor.lastrowid

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

    # ajoute un nouveau membre
    def inscription(self, nom, mdp, email, genre):
        # Préparer la requête SQL
        requete = "INSERT INTO utilisateurs (nom, motDePasse, email, genre, role) VALUES (%s, MD5(%s), %s, %s, %s)"
        data = (nom, mdp, email, genre, 'utilisateur')

        # Envoyer la requete
        try:
            self.cursor.execute(requete, data)
            return True

        except pymysql.MySQLError as e:
            print(e)
            return False

    # Retourne les infos de l'utilisateur avec son email
    def getUserInfo(self, email):
        statement = f"SELECT utilisateurs.idUtilisateur, utilisateurs.nom, utilisateurs.email, utilisateurs.genre, utilisateurs.role FROM utilisateurs WHERE utilisateurs.email = %s;"
        data = email
        self.cursor.execute(statement, data)
        return self.cursor.fetchone()

    # Retourne le role de l'utilisateur avec son email
    def getRole(self, email):
        statement = f"SELECT utilisateurs.role FROM utilisateurs WHERE utilisateurs.email = %s;"
        data = email
        self.cursor.execute(statement, data)
        return self.cursor.fetchone()

    # Get les infos sur un commentaire et transforme son timestamp en interval (Il y a X temps)
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

    # Ajoute un commentaire a un article via son Id
    def add_comment(self, articleid, userid, comment):
        statement = f"INSERT INTO messages (contenu, horodatage, idArticle, idUtilisateur) VALUES (%s, NOW(), %s, %s);"
        data = comment, articleid, userid

        try:
            self.cursor.execute(statement, data)
            return True

        except pymysql.MySQLError as e:
            print(e)
            return False

    def add_reference(self, nomAuteur, titreDocument, anneeParution, ISBN, editeur):
        statement = "SELECT * FROM refs WHERE refs.nomAuteur = %s AND refs.titreDocument = %s AND refs.anneeParution = %s AND refs.ISBN = %s AND refs.editeur = %s;"
        data = (nomAuteur, titreDocument, anneeParution, ISBN, editeur)
        self.cursor.execute(statement, data)
        entry = self.cursor.fetchone()

        if entry:
            idReference = entry[0]
            return idReference
        else:
            statement = f"INSERT INTO `refs` (`nomAuteur`, `titreDocument`, `anneeParution`, `ISBN`, `editeur`) VALUES (%s, %s, %s, %s, %s);"
            data = (nomAuteur, titreDocument, anneeParution, ISBN, editeur)
            try:
                self.cursor.execute(statement, data)
                self.connection.commit()
                return self.cursor.lastrowid
            except Exception as e:
                raise

    def add_article(self, titre, contenu, idCategorie, idCreateur, idreference):
        statement = ("INSERT INTO `articles` (`titre`, `contenu`, `dateCreation`, "
                     "`idCategorie`, `idCreateur`, `idRef`) VALUES (%s, %s, %s, %s, %s, %s);")
        data = (titre, contenu, date.today().isoformat(), idCategorie, idCreateur, idreference)
        try:
            self.cursor.execute(statement, data)
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(e)
            return None

    # Get les emails des utilisateur pouvant exclure les admins
    def getEmailLike(self, keyword, role):
        statement = f"SELECT utilisateurs.email FROM utilisateurs WHERE utilisateurs.email LIKE %s "
        if role != 'administrateur':
            statement += f"AND utilisateurs.role != 'administrateur'"
        statement += f";"
        data = '%' + keyword + '%'
        self.cursor.execute(statement, data)
        liste = []
        for email in self.cursor.fetchall():
            liste.append(email[0])
        return liste

    def update_profile(self, nom, id):
        statement = f"UPDATE utilisateurs SET nom = %s WHERE idUtilisateur = %s;"
        data = nom, id

        try:
            self.cursor.execute(statement, data)
            return True
        except pymysql.MySQLError as e:
            print(e)
            return False

    def update_password(self, motdepasse, id):
        statement = "UPDATE utilisateurs SET motDePasse = md5(%s) WHERE idUtilisateur = %s;"
        data = motdepasse, id
        try:
            self.cursor.execute(statement, data)
            return True
        except pymysql.MySQLError as e:
            print(e)
            return False

    def update_role(self, role, email):
        statement = f"UPDATE utilisateurs SET utilisateurs.role = %s WHERE utilisateurs.email = %s;"
        data = role, email

        try:
            self.cursor.execute(statement, data)
            return True
        except pymysql.MySQLError as e:
            print(e)
            return False

    def delete_account(self, email):
        statement = "DELETE FROM utilisateurs WHERE utilisateurs.email = %s;"
        data = email
        try:
            self.cursor.execute(statement, data)
            return True
        except pymysql.MySQLError as e:
            print(e)
            return False

    def getCatLike(self, search):
        statement = f"SELECT categories.nom FROM categories WHERE categories.nom LIKE %s;"
        data = '%' + search + '%'
        self.cursor.execute(statement, data)
        liste = []
        for cat in self.cursor.fetchall():
            liste.append(cat[0])
        return liste

    def getCatParent(self, cat):
        statement = f"SELECT p.nom FROM categories c JOIN categories p ON p.idCategorie = c.idCategorieParent WHERE c.nom = %s;"
        data = cat
        self.cursor.execute(statement, data)

        return self.cursor.fetchone()

    def reset_password_by_email(self, email):
        all_characters = string.ascii_letters + string.digits + string.punctuation
        length = 10
        password = ''.join(random.choices(all_characters, k=length))

        statement = "UPDATE utilisateurs SET motDePasse = MD5(%s) WHERE email = %s;"
        data = password, email
        try:
            self.cursor.execute(statement, data)
            return password
        except pymysql.MySQLError as e:
            print(e)
            return None

    def delete_article(self, article_id, user_id):
        statement = "DELETE FROM articles WHERE idArticle = %s AND idCreateur = %s;"
        data = (article_id, user_id)
        try:
            self.cursor.execute(statement, data)
            self.connection.commit()
            return True
        except pymysql.MySQLError as e:
            print(e)
            return False

    def get_articles_by_user(self, user_id):
        statement = "SELECT idArticle, titre, contenu, dateCreation FROM articles WHERE idCreateur = %s;"
        data = (user_id,)
        self.cursor.execute(statement, data)
        articles = []
        for row in self.cursor.fetchall():
            article = {
                "id": row[0],
                "title": row[1],
            }
            articles.append(article)
        return articles
