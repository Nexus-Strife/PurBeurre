import mysql.connector
from mysql.connector import errorcode
import time
from math import ceil
import json
import requests

config = {  # Args used to create the database
    'host': '172.18.0.1',
    'port': '3307',
    'user': 'root',
    'password': 'password'
}

config_table = {  # Args used to create the tables
    'host': '172.18.0.1',
    'port': '3307',
    'user': 'root',
    'password': 'password',
    'database': 'OpenFood'
}

DB_NAME = 'OpenFood'


class NewDB:  # Class that create the database

    def __init__(self):
        self.db = 'OpenFood'  # Name of the database

    def create_database(cursor):  # That method create the database
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))  # Create the database only if it doesn't exist
        except mysql.connector.Error as err:
            print("Impossible de créer la BDD: {}".format(err))
            exit(1)

    def create_tb(cursor):  # Method that create tables
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
                           "foreign key (prod_substitute_id) REFERENCES products(prod_id))")

        except mysql.connector.Error as err:
            print(err)
            exit(1)

    def write_in(self):  # Method that write (n) page of (n) categories
        cnx = mysql.connector.connect(**config_table)
        cursor = cnx.cursor(buffered=True)


        print("Veuillez patienter...")
        r = requests.get('https://fr.openfoodfacts.org/categories.json')  # Using the Requests lib to read the *.json that contain the list of the categories on opendfoodfacts
        categories = r.json()

        nbr_categories = categories["count"]
        nbr_of_cats = int(input("Combien de catégories voulez vous injecter dans la BDD ? "))
        nbr_pages = int(input("Combien de page par catégorie voulez-vous ? "))

        ''' Each 3 next loop ( for ) are used to parse every categories and every pages to add each product in
            the database. '''

        for i in range(nbr_of_cats):
            print(i + 1, " - ", end=" ")
            category = (categories["tags"][i]["name"])
            print(category)
            nbr_products = int(categories["tags"][i]["products"])
            nbr_of_pages = ceil(nbr_products / 20)
            print("\t Nombre de produits :", nbr_products, end=" ")
            print("\t Nombre de pages :", nbr_of_pages)
            adresse = categories["tags"][i]["url"] + "/1.json"
            print("\t", adresse)
            cursor.execute("INSERT INTO categories (category) VALUES (%s)", (category, ))
            cnx.commit()

            for page in range(nbr_pages):
                page = page + 1
                addr = categories["tags"][i]["url"] + "/" + str(page) + ".json"
                p = requests.get(addr)
                products = p.json()

                for Prod in range(20):   # range(20) because there are 20 products per page
                    try:

                        grade_prod = (products["products"][Prod]["nutrition_grades"])
                        store_prod = (products["products"][Prod]["stores"])
                        name_prod = (products["products"][Prod]["product_name"])
                        energy_prod = (products["products"][Prod]["nutriments"]["energy_100g"])
                        url_prod = (products["products"][Prod]["url"])
                        desc_prod = (products["products"][Prod]["generic_name"])

                        cursor.execute("SELECT id FROM categories WHERE category = %(cats)s", {'cats': category})

                        currentCategory = cursor.fetchone()
                        cate_id = currentCategory[0]

                        # Then replace every blank informations by " unknown "

                        if store_prod == "":
                            store_prod = "Inconnu"
                        elif grade_prod == "":
                            grade_prod = "-"
                        elif energy_prod == "":
                            energy_prod = "Inconnu"
                        elif url_prod == "":
                            url_prod = "Inconnue"
                        elif desc_prod == "":
                            desc_prod = "Non communiquée"

                        #  And add everything into the products table

                        cursor.execute("INSERT INTO products (name, store, grade, kcal_100g, cat_id, link,"
                                       "description) VALUES (%s,"
                                       "%s, %s, %s, %s, %s, %s)", (name_prod, store_prod, grade_prod, energy_prod, cate_id, url_prod, desc_prod))

                        cnx.commit()

                    except KeyError:
                        continue
                    time.sleep(0.1)
