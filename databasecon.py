import mysql.connector
cnx = mysql.connector.connect(
    # host='localhost',
    # port=3307,
    # user='root',
    # password='bhattarai',
    # database='token'
    host='127.0.0.1',
    user='root',
    password='',
    database='token'

)
cursor = cnx.cursor()