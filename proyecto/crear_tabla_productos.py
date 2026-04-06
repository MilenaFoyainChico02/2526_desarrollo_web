import sys
import os
sys.path.append(os.getcwd())
from conexion.conexion import conectar

def crear_tabla_productos():
    conn = conectar()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    descripcion TEXT,
                    cantidad INT NOT NULL,
                    precio DECIMAL(10, 2) NOT NULL
                )
            ''')
            conn.commit()
            print("Tabla 'productos' creada exitosamente o ya existía.")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
    else:
        print("No se pudo conectar a la base de datos.")

if __name__ == "__main__":
    crear_tabla_productos()
