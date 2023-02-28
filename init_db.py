import os
import sqlite3

dirname = os.path.dirname(__file__)
dbname = os.path.join(dirname, "db\calendlyke.db")
schemafile = os.path.join(dirname, "db\schema.sql")

connection = sqlite3.connect(dbname)

with open(schemafile, "r") as file:
    # print(file.read())
    try:
        connection.executescript(file.read())
    except sqlite3.Error as e:
        print(e)
    
cur = connection.cursor()

connection.commit()
connection.close()