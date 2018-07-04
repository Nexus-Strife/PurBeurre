import mysql.connector
from mysql.connector import errorcode
import time
from math import ceil
import json
import requests

config = {  # Config permettant de créer la base
    'host': '172.18.0.1',
    'port': '3307',
    'user': 'root',
    'password': 'password'
}

config_table = {  # Config permettant de créer la table
    'host': '172.18.0.1',
    'port': '3307',
    'user': 'root',
    'password': 'password',
    'database': 'OpenFood'
}

DB_NAME = 'OpenFood'


class NewDB:  # Class permettant de créer la bdd

    def __init__(self):
        self.db = 'OpenFood'

    def create_database(cursor):
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
        except mysql.connector.Error as err:
            print("Impossible de créer la BDD: {}".format(err))
            exit(1)

    """    try:
            cnx.database = DB_NAME
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                time.sleep(3)
                create_database(cursor)
                cnx.database = DB_NAME
            else:
                print(err)
                exit(1)"""

    def create_tb(cursor):
        cnx = mysql.connector.connect(**config_table)
        cursor = cnx.cursor()

        try:

            cursor.execute("CREATE TABLE IF NOT EXISTS categories(id INT AUTO_INCREMENT PRIMARY KEY,"
                           "category VARCHAR(50))")
            time.sleep(2)

            cursor.execute("CREATE TABLE IF NOT EXISTS products(prod_id INT AUTO_INCREMENT PRIMARY KEY,"
                           "name VARCHAR(255), store VARCHAR(255),"
                           "grade VARCHAR(1), kcal_100g INT,"
                           "cat_id INT, foreign key (cat_id) REFERENCES categories(id), link VARCHAR(255),"
                           "description TEXT)")

            time.sleep(2)

            cursor.execute("CREATE TABLE IF NOT EXISTS usr_products(id INT AUTO_INCREMENT PRIMARY KEY, prod_id INT "
                           "NOT NULL, UNIQUE (prod_id),"
                           "foreign key (prod_id) REFERENCES products(prod_id), prod_substitute_id INT,"
                           "foreign key (prod_id) REFERENCES products(prod_id))")

        except mysql.connector.Error as err:
            print(err)
            exit(1)

    def write_in(self):
        cnx = mysql.connector.connect(**config_table)
        cursor = cnx.cursor(buffered=True)


        print("Veuillez patienter...")
        r = requests.get('https://fr.openfoodfacts.org/categories.json')
        categories = r.json()

        nombre_categories = categories["count"]
        nombre_a_afficher = int(input("Combien de catégories voulez vous injecter dans la BDD ? "))

        for i in range(nombre_a_afficher):
            print(i + 1, " - ", end=" ")
            Category = (categories["tags"][i]["name"])
            print(Category)
            nombre_produits = int(categories["tags"][i]["products"])
            nombre_pages = ceil(nombre_produits / 20)
            print("\t Nombre de produits :", nombre_produits, end=" ")
            print("\t Nombre de pages :", nombre_pages)
            adresse = categories["tags"][i]["url"] + "/1.json"
            print("\t", adresse)
            cursor.execute("INSERT INTO categories (category) VALUES (%s)", (Category,))
            cnx.commit()



            for Page in range(3):
                Page = Page + 1
                Addr = categories["tags"][i]["url"] + "/" + str(Page) + ".json"
                p = requests.get(Addr)
                products = p.json()


                for Prod in range(20):
                    try:

                        Grade = (products["products"][Prod]["nutrition_grades"])
                        Store = (products["products"][Prod]["stores"])
                        Name = (products["products"][Prod]["product_name"])
                        Energy = (products["products"][Prod]["nutriments"]["energy_100g"])
                        Url = (products["products"][Prod]["url"])
                        Desc = (products["products"][Prod]["generic_name"])

                        cursor.execute("SELECT id FROM categories WHERE category = %(cats)s", {'cats': Category})

                        currentCategory = cursor.fetchone()
                        cate_id = currentCategory[0]

                        if Store == "":
                            Store = "Inconnu"
                        elif Grade == "":
                            Grade = "-"
                        elif Energy == "":
                            Energy = "Inconnu"
                        elif Url == "":
                            Url = "Inconnue"


                        cursor.execute("INSERT INTO products (name, store, grade, kcal_100g, cat_id, link,"
                                       "description) VALUES (%s,"
                                       "%s, %s, %s, %s, %s, %s)", (Name, Store, Grade, Energy, cate_id, Url, Desc))


                        cnx.commit()



                    except KeyError:
                        continue
                    time.sleep(0.1)
