from conexion.conexion import conectar
from models.usuario import Usuario


def get_usuario_email_column(cursor):
    try:
        cursor.execute("SHOW TABLES LIKE 'usuario'")
        if cursor.fetchone() is None:
            return 'correo'

        cursor.execute("SHOW COLUMNS FROM usuario LIKE 'correo'")
        if cursor.fetchone():
            return 'correo'

        cursor.execute("SHOW COLUMNS FROM usuario LIKE 'email'")
        if cursor.fetchone():
            return 'email'
    except Exception:
        pass
    return 'correo'


def crear_tabla_usuario():
    conn = conectar()
    if conn is None or not conn.is_connected():
        return

    cursor = conn.cursor()
    
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS usuario (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            correo VARCHAR(150) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            rol VARCHAR(50) NOT NULL DEFAULT 'usuario',
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    conn.commit()
    cursor.close()
    conn.close()


def obtener_usuario_por_email(email):
    conn = conectar()
    if conn is None or not conn.is_connected():
        return None

    cursor = conn.cursor()
    column = get_usuario_email_column(cursor)
    cursor.execute(f'SELECT id_usuario, nombre, {column}, password, rol FROM usuario WHERE {column} = %s', (email,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return Usuario(*row)
    return None


def obtener_usuario_por_id(user_id):
    conn = conectar()
    if conn is None or not conn.is_connected():
        return None

    cursor = conn.cursor()
    column = get_usuario_email_column(cursor)
    cursor.execute(f'SELECT id_usuario, nombre, {column}, password, rol FROM usuario WHERE id_usuario = %s', (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return Usuario(*row)
    return None


def registrar_usuario(nombre, email, password_hash):
    conn = conectar()
    if conn is None or not conn.is_connected():
        raise Exception('No se pudo conectar a la base de datos')

    cursor = conn.cursor()
    column = get_usuario_email_column(cursor)
    cursor.execute(
        f'INSERT INTO usuario (nombre, {column}, password) VALUES (%s, %s, %s)',
        (nombre, email, password_hash)
    )
    conn.commit()
    cursor.close()
    conn.close()
