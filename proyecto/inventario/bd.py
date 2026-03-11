# coneción con SQLite
import sqlite3
from sqlite3 import Error
from pathlib import Path

db_path = Path(__file__).parent /"data" / 'inventario.db'

def get_connection():
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn 

def init_db(): 
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT, -- AGREGADO: faltaba esta columna
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL
            )
        ''')
        conn.commit()