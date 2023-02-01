import mysql.connector
cnx = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='token'
)
cursor = cnx.cursor()