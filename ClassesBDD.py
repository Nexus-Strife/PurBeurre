import mysql.connector
# from mysql.connector import errorcode
import time

config = {
    'host': '172.18.0.1',
    'port': '3307',
    'user': 'root',
    'password': 'password',
    'database': 'OpenFood'
}


class Console:  # Main class of the program

    def catlist(self, cursor):  # Method that display the list of categories

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT category, id FROM categories")

        time.sleep(1)
        for row in cursor:
            print("{category}: {id}".format(**row))

    def selcat(self, cursor):  # Method where the user can select a category to explore

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)

        sel_cat = 1

        while sel_cat:

            try:  # A try ... except block that check if the user enter the id of a category rather than the name

                id_sel = int(input("\nVeuillez selectionner une catégorie ou retourner au menu principal (99): "))

                cursor.execute("SELECT id FROM categories WHERE id = %s", (id_sel, ))  # This SQL req check if the id of the category entered before exist
                id_verified = cursor.fetchone()

                if id_sel == 99:
                    self.menu()
                    sel_cat = 0

                elif not id_verified:  # If the category doesn't exist, than reply "The selected category doesn't exist"
                    print("\nVotre catégorie n'existe pas")

                else:  # If the category exist, display all products in
                    sel_cat = 0
                    cursor.execute("SELECT * FROM products WHERE cat_id = '%s'", (id_sel, ))
                    for row in cursor:
                        print("Produit: {name}, Note: {grade}, ID: {prod_id}, Lien: {link}".format(**row))

            except ValueError:  # End of this first try...except block. If there are str in 'id_sel' than reply "You can't use chars"
                print("\nQ.U.E   D.E.S   C.H.I.F.F.R.E.S")

        another_menu = 1

        while another_menu:  # After displayed all products from a category, ask what to do in a new menu

            try:  # Another try...except block that will check if the var 'choice_menu_find' contain only int

                choice_menu_find = int(input("\nQue souhaitez vous faire ?\nAjoutez un aliment à votre base (1)\n"
                                             "Retour à la liste des catégories (2)\nRetour au menu principal (3)"))

                if choice_menu_find > 3:
                    print("\nVeuillez choisir un chiffre entre 1 et 3 !")

                elif choice_menu_find == 1:

                    another_prime_menu = 1

                    while another_prime_menu:

                        try:  # Another try...except block that will check if 'product_id' only contain int

                            ctrl_nbr_products = 1

                            while ctrl_nbr_products:

                                product_id = int(input("\nVeuillez entrer l'ID"
                                                       " du produit que vous souhaitez enregistrer: "))
                                cursor.execute("SELECT * FROM products WHERE prod_id = %s", (product_id, ))  # This cursor.execute check if the product_id exist in the database
                                id_exist = cursor.fetchone()

                                if not id_exist:
                                    print("\nVotre produit n'est pas dans la base de données")  # If not exist, notify it to the user

                                else:
                                    print("Enregistrement en cours...")
                                    cursor.execute("INSERT INTO usr_products (prod_id) VALUES (%s)"  # Otherwise register it into the database
                                                   " ON DUPLICATE KEY UPDATE prod_id = prod_id", (product_id, ))
                                    cnx.commit()
                                    time.sleep(0.2)
                                    ctrl_nbr_products = 0

                                try:  # Another one here to check the value of the next var ( 'go_again' )
                                    go_again = int(input("\nVoulez-vous ajouter un autre produit ?"
                                                        " \nOui (1)\nNon (2)\nUn substitut (3)"))

                                    if go_again == 1:
                                        continue

                                    elif go_again == 2:
                                        another = 0
                                        self.menu()

                                    elif go_again > 3:
                                        print("Veuillez choisir un chiffre entre 1 et 3 !")

                                    elif go_again < 1:
                                        print("Veuillez choisir un chiffre entre 1 et 3 !")

                                    elif go_again == 3:  # The three next cursor.execute put in var the category ID, the grade and the energy per 100g that going to compose the search args to find a substitute
                                        cursor.execute("SELECT cat_id FROM products WHERE prod_id = %(a)s",
                                                       {'a': product_id})
                                        cat_prod_fetch = cursor.fetchone()
                                        cat_prod_id = cat_prod_fetch['cat_id']

                                        cursor.execute("SELECT grade FROM products WHERE prod_id = %(b)s",
                                                       {'b': product_id})
                                        grade_pro_fetch = cursor.fetchone()
                                        grade_prod = grade_pro_fetch['grade']

                                        cursor.execute("SELECT kcal_100g FROM products WHERE prod_id = %(c)s",
                                                       {'c': product_id})
                                        nrg = cursor.fetchone()
                                        enrgy_prod = nrg['kcal_100g']

                                        cursor.execute("SELECT * FROM products"
                                                  " WHERE cat_id = %s AND grade <= %s AND kcal_100g <= %s",(cat_prod_id,
                                                                                                            grade_prod,
                                                                                                            enrgy_prod, ))  # SQl req to search a substitute based on the criteria mentioned previously
                                        for row in cursor:
                                            print("\nID: {prod_id},\nNom: {name},\nDesc: {description},\n"
                                                  "Note: {grade},\nEnergie: {kcal_100g},\nLien: {link}\n".format(**row))  # Then print the results

                                        add_sub = 1

                                        while add_sub:
                                            try:
                                                prod_sub = int(input("Veuillez entrer l'ID du substitut que vous souhaitez: "))
                                                cursor.execute("UPDATE usr_products"
                                                               " SET prod_substitute_id = %s WHERE prod_id = %s", (prod_sub,
                                                                                                               product_id,))  # And finally the req that add the substitute into the database
                                                cnx.commit()
                                                another_prime_menu = 0
                                                add_sub = 0
                                                self.menu()

                                            except ValueError:

                                                print("\nLes lettres ne sont pas autorisées !")

                                except ValueError:
                                     print("\nLes lettres ne sont pas autorisées")

                        except ValueError:
                            print("\nJ'ai dit que des chiffres !")

                elif choice_menu_find == 2:
                    self.catlist(cursor)
                    time.sleep(0.5)
                    self.selcat(cursor)

                elif choice_menu_find == 3:
                    self.menu()

            except ValueError:
                print("\nQue des chiffres !")

    def find(self, cursor):  # Method that give a search fonction

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)

        find_it = 1

        while find_it:

            aliment = (input("\nVeuillez entrer le nom d'un aliment que vous recherchez:"))  # The user enter the name of the product that he is searching

            cursor.execute("SELECT * FROM products"
                    " WHERE name LIKE %(p)s ORDER by grade ASC",  {"p": "%{}%".format(aliment.replace(' ', '%'))})  # SQL req that check every products by name that user entered, using operator "LIKE"

            for row in cursor:
                print("Produit: {name}, Note: {grade}, ID: {prod_id}, Lien: {link}".format(**row))  # Then print the results
                find_it = 0
        time.sleep(0.5)
        self.menu_find(cursor)

    def menu_find(self, cursor):  # Method that display the function to find products or substitute

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)

        menu_find_while = 1

        while menu_find_while:
            try:

                choice_menu_find = int(input("\nQue souhaitez vous faire ?\n"
                                             "Aller au menu des catégories (1)\nRetour au menu principal (2)\n"
                                             "Chercher un autre aliment (3)\nEnregistrer un aliment dans la BDD (4)\nTrouver un substitut (5)"))
                if choice_menu_find == 1:
                    self.catlist(cursor)
                    time.sleep(0.5)
                    self.selcat(cursor)
                    menu_find_while = 0

                elif choice_menu_find == 2:
                    self.menu()
                    menu_find_while = 0

                elif choice_menu_find == 3:
                    self.find(cursor)
                    menu_find_while = 0

                elif choice_menu_find == 4:
                    try:
                        product_id = int(input("\nVeuillez entrer l'ID du produit que vous souhaitez enregistrer: "))

                        print("Enregistrement en cours...")
                        cursor.execute("INSERT INTO usr_products (prod_id) VALUES (%s)"
                                       " ON DUPLICATE KEY UPDATE prod_id = prod_id", (product_id, ))
                        cnx.commit()
                        print("Retour au menu principal...")
                        time.sleep(1)
                        self.menu()
                        menu_find_while = 0
                    except ValueError:
                        print("\nL'ID du produit ne peut être que composer de chiffres")

                elif choice_menu_find == 5:
                    self.find_substitute(cursor)
                    menu_find_while = 0

                elif choice_menu_find <= 0:
                    print("\nVeuillez entrer un chiffre entre 1 et 5")

            except ValueError:
                print("\nVeuillez entrer un chiffre correspondant à votre choix")

    def find_substitute(self, cursor):  # Method that find a substitute for an ID given as product

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)

        find_substitute_while = 1

        while find_substitute_while:

            try:
                substitut = int(input("\nVeuillez entrer l'ID du produit que vous souhaitez substituer: "))  # The user need to enter the product's ID of the one he want to substitute

                cursor.execute("SELECT cat_id, grade, kcal_100g FROM products WHERE prod_id = %s", (substitut, ))  # Select the category's ID, grade and the energy per 100g as criteria to find substitute

                for row in cursor:

                    cursor.execute("SELECT * FROM products"
                                   " WHERE cat_id = {cat_id} AND grade <= '{grade}' AND kcal_100g <= {kcal_100g}"
                                   " ORDER by grade ASC".format(**row))  # Then compare every product of the same category with the grade and the energy per 100g

                    for row in cursor:

                        print("\nID: {prod_id},\nNom: {name},\nDesc: {description},\nNote: {grade},\nEnergie:"
                              " {kcal_100g},\nLien: {link}\n".format(**row))  # And display them



                    cursor.execute("SELECT prod_id, name FROM products WHERE prod_id = %s", (substitut, ))  # Another SQL req to display the product id and the name of the product...

                    for row in cursor:
                        which_one = int(input("Entrez l'ID du produit substituant: ({prod_id}) {name} ?".format(**row)))  # ...Here in case of the user forgot for what he asking a substitute
                        cursor.execute("UPDATE usr_products SET prod_id = %s, prod_substitute_id = %s WHERE prod_id = %s", (substitut, which_one, substitut, ))  # Then update the line whith the substitute ID where the product ID is
                        cnx.commit()
                        self.menu()
                        find_substitute_while = 0

            except ValueError:
                print("\nVeuillez entrer que des chiffres !")

    def menu(self):

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        menu = 1

        while menu:
            print("\nParcourir les catégories (1)\nChercher un aliment (2)\n"
                  "Consulter les aliments sauvegarder (3)\nTrouver un substitut (4)\nQuitter (99)")

            try:
                choice_menu = int(input("\nQue souhaitez-vous ? \n"))

                if choice_menu > 0:
                    if choice_menu == 1:
                        menu = 0
                        self.catlist(cursor)
                        time.sleep(0.5)
                        self.selcat(cursor)
                    elif choice_menu == 2:
                        menu = 0
                        self.find(cursor)
                    elif choice_menu == 3:
                        menu = 0
                        self.usr_products(cursor)
                    elif choice_menu == 4:
                        self.find_substitute(cursor)
                        menu = 0

                    elif choice_menu == 99:
                        print("\nBye !")
                        time.sleep(0.3)
                        exit()
                    elif choice_menu > 4:
                        print("\nVeuillez entrer un chiffre entre 1 et 4 ou 99 !")
                    elif choice_menu < 0:
                        print("\nVeuillez entrer un chiffre entre 1 et 4 ou 99 !")

            except ValueError:
                print("\nLes lettres sont interdites !")

    def usr_products(self, cursor):  # Method that describe how the user_products's database work

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)

        ''' This cursor.execute grab every informations about products and their substitutes. since the products id and the
            substitute id exist in the same table, the program need to create alias from tables and rows to display
            everything'''

        cursor.execute("SELECT p.name AS prod_name, p.grade AS prod_grade, p.store AS prod_store, "
                       "p.kcal_100g AS prod_energy, p.link AS prod_link, p.description AS prod_desc,"
                       " p.prod_id AS produ_id, "
                       "sp.name AS sub_name, sp.grade AS sub_grade, sp.store AS sub_store, sp.kcal_100g AS sub_energy,"
                       " sp.link AS sub_link, sp.description AS sub_desc, sp.prod_id AS sub_prod_id "
                       "FROM usr_products up INNER JOIN products p ON up.prod_id = p.prod_id "
                       "LEFT JOIN products sp ON up.prod_substitute_id = sp.prod_id")

        for row in cursor:
            print("\n                                   \033[4mPRODUIT\033[0m:")  # "\033[4m" display the word with underlines

            print("\n\033[4mID\033[0m: {produ_id},\n\033[4mNom\033[0m: {prod_name},\n\033[4mLien\033[0m: {prod_link},"
                  "\n\033[4mNote\033[0m: {prod_grade},\n\033[4mMagasin\033[0m: {prod_store},"
                  "\n\033[4mValeur energetique\033[0m: {prod_energy},\n\033[4mDescription\033[0m: {prod_desc}".format(**row))


            if ("{sub_prod_id}".format(**row)) != "None":  # If there is not a substitute id for a given id product then don't print anything

                print("\n                                   \033[4mSUBSTITUT DE\033[0m: {prod_name}".format(**row))
                print("\n\033[4mID du substitut\033[0m: {sub_prod_id},\n\033[4mNom du substitut\033[0m: {sub_name},"
                      "\n\033[4mLien\033[0m: {sub_link},\n\033[4mNote\033[0m: {sub_grade},"
                      "\n\033[4mMagasin\033[0m: {sub_store},\n\033[4mValeur energetique\033[0m:"
                      " {sub_energy},\n\033[4mDescription\033[0m: {sub_desc}\n\n\n".format(**row))
            else:
                pass

        time.sleep(0.5)

        check_answer = 1

        while check_answer:

            try:

                usr_choice = int(input("\nQue souhaitez-vous faire ?\nEffacer un aliment (1)\n"
                                       "Retourner au menu principal (2)"))

                if usr_choice == 1:
                    usr_del = int(input("Veuillez entrer l'ID du produit à supprimer: "))
                    print("Suppression en cours...")
                    time.sleep(0.5)
                    cursor.execute("DELETE FROM usr_products WHERE prod_id = %s", (usr_del, ))
                    cnx.commit()
                    print("Suppression faite !")
                    time.sleep(0.5)
                    self.usr_products(cursor)

                elif usr_choice == 2:
                    self.menu()

                elif usr_choice <= 0:
                    print("Veuillez un chiffre entre 1 et 2 ! ( Choix difficile ) !")

                elif usr_choice > 2:
                    print("Veuillez un chiffre entre 1 et 2 ! ( Choix difficile ) !")

            except ValueError:
                print("\nVeuillez entrer un chiffre correspondant à ce que vous souhaitez faire.")
