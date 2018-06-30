import mysql.connector
from mysql.connector import errorcode
import time

config = {
    'host':'172.18.0.1',
    'port':'3307',
    'user':'root',
    'password':'password',
    'database':'OpenFood'
}

class Client:

    def Catlist(self, cursor):
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT category, id FROM categories")

        time.sleep(3)
        for row in cursor:

            print("{category}: {id}".format(**row))

    def selcat(self, cursor):

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)

        id_sel = int(input("\nVeuillez selectionner une catégorie ou retourner au menu principal (99): "))
        if id_sel == 99:
            self.menu()

        cursor.execute("SELECT * FROM products WHERE cat_id = '%s'", (id_sel, ))
        for row in cursor:
            print("Produit: {name}, Note: {grade}, ID: {prod_id}, Lien: {link}".format(**row))

        choice_menu_find = int(input("\nQue souhaitez vous faire ?\nAjoutez un aliment à votre base (1)\nRetour à "
                                     "la liste des catégories (2)\nRetour au menu principal (3)"))

        if choice_menu_find == 1:
            id_product = int(input("\nVeuillez entrer l'ID du produit que vous souhaitez enregistrer: "))
            print("Enregistrement en cours...")
            cursor.execute("INSERT usr_products SELECT name, store, grade, cat, prod_id, cat_id FROM products WHERE prod_id = %s", (id_product, ))
            cnx.commit()
            self.menu()
        elif choice_menu_find == 2:
            self.Catlist(cursor)
            time.sleep(0.5)
            self.selcat(cursor)
        elif choice_menu_find == 3:
            self.menu()


    def find(self, cursor):

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)

        aliment = (input("\nVeuillez entrer le nom d'un aliment que vous recherchez:"))

        cursor.execute("SELECT * FROM products WHERE name LIKE %(p)s ORDER by grade ASC",  {"p": "%{}%".format(aliment.replace(' ', '%'))})
        for row in cursor:
            print("Produit: {name}, Note: {grade}, ID: {prod_id}, Lien: {link}".format(**row))

        time.sleep(0.5)
        choice_menu_find = int(input("\nQue souhaitez vous faire ?\nRetour au menu des catégories (1)\nRetour au menu"
                                     " principal (2)\nChercher un autre aliment (3)\nEnregistrer un aliment dans la BDD (4)"))
        if choice_menu_find == 1:
            self.Catlist(cursor)
            time.sleep(0.5)
            self.selcat(cursor)
        elif choice_menu_find == 2:
            self.menu()
        elif choice_menu_find == 3:
            self.find(cursor)
        elif choice_menu_find == 4:
            id_product = int(input("\nVeuillez entrer l'ID du produit que vous souhaitez enregistrer: "))
            print("Enregistrement en cours...")
            cursor.execute("INSERT usr_products SELECT name, store, grade, cat, prod_id, cat_id FROM products WHERE prod_id = %s", (id_product, ))
            cnx.commit()
            print("Retour au menu principal...")
            time.sleep(1)
            self.menu()

    def menu(self):

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        print("\nParcourir les catégories (1)\nChercher un aliment (2)\nConsulter les aliments sauvegarder (3)\nQuitter (99)")
        Choice_menu = int(input("Que souhaitez-vous ? "))

        if Choice_menu == 1:
            self.Catlist(cursor)
            time.sleep(0.5)
            self.selcat(cursor)
        elif Choice_menu == 2:
            self.find(cursor)
        elif Choice_menu == 3:
            self.usr_products(cursor)
        elif Choice_menu == 99:
            print("Bye !")
            time.sleep(0.3)
            exit()

    def usr_products(self, cursor):

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("SELECT name, store, grade, prod_id FROM usr_products")
        for row in cursor:
            print("Nom: {name} | Magasin: {store} | Note: {grade} | ID du produit: {prod_id} | lien {link}".format(**row))
        time.sleep(0.5)

        usr_choice = int(input("\nQue souhaitez-vous faire ?\nEffacer un aliment (1)\nRetourner au menu principal (2)"))
        if usr_choice == 1:
            usr_del = int(input("Veuillez entrer l'ID du produit à supprimer: "))
            print("Suppression en cours...")
            time.sleep(0.5)
            cursor.execute("DELETE FROM usr_products WHERE prod_id = %s", (usr_del, ))
            print("Suppression faite !")
            time.sleep(0.5)
            self.usr_products(cursor)

        elif usr_choice == 2:
            self.menu()

