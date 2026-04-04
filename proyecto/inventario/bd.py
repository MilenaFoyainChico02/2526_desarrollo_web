import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "data" / 'inventario.db'

def get_connection():
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn 

def init_db(): 
    with get_connection() as conn:
        # Creamos la tabla 'funcion' según tu diagrama
        conn.execute('''
            CREATE TABLE IF NOT EXISTS funcion (
                id_funcion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                descripcion TEXT,
                fecha_hora TEXT,
                total REAL,
                metodo_pago TEXT
            )
        ''')
        conn.commit()