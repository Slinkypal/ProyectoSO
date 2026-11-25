import pymysql

S = 100
H = 6
M = 10
K = 2
B = 3
N = 30
C = 3

ROJO = "\033[1;31m"
RESET = "\033[0m"
ETIQUETA = f"{ROJO}[G1-banco]{RESET}"

DB_CONFIG = {
    "unix_socket": "/var/run/mysqld/mysqld.sock",
    "user": "app_g1",
    "password": "ClaveSeguraG1_2026!",
    "database": "so_g1_banco",
    "autocommit": True
}

def obtener_conexion():
    return pymysql.connect(**DB_CONFIG)
