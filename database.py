import pymysql

connection = pymysql.connect(
    host="localhost",
    user="root",
    password="VOTRE MOT DE PASSE",
    db="glo_2005_webapp_2023",
    autocommit=True
)

cursor = connection.cursor()

if __name__ == '__main__':
    print("hello")
