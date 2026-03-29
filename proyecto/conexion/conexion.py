# clase de conexión a la base de datos my
import mysql.connector
from mysql.connector import Error
def conectar():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            database='cimazon',
            user='root',
            password='Polacasj'
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None