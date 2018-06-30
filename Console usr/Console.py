from ClassesBDD import *
import requests
import mysql.connector
from mysql.connector import errorcode
import time

config = {
    'host': '172.18.0.1',
    'port': '3307',
    'user': 'root',
    'password': 'password',
    'database': 'OpenFood'
}

read = Client()

running = 1

read.menu()
