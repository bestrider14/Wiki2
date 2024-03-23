import os
import sqlparse

def run_sql_file(cursor, filename, accept_empty=False):
    """
    Exécute chaque instruction d'un fichier .sql

    :param cursor: un curseur pymysql.cursor ouvert
    :param filename: le fichier .sql à exécuter
    :param accept_empty: si faux, lance une exception si le fichier est vide
    """

    current_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(current_dir, filename)

    data = open(abs_file_path, 'r').read()

    sql_statements = sqlparse.split(data)

    if len(sql_statements) == 0 and not accept_empty:
        raise IOError(f"File '{filename}' is empty.")

    for statement in sql_statements:
        cursor.execute(statement)
