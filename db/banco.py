# db/banco.py
import mysql.connector
from db.config import DB_CONFIG

def conectar():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        raise ConnectionError(f"Erro ao conectar ao banco: {e}")
