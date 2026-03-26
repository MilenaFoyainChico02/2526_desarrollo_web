from pathlib import Path
import json
import csv

DATA_DIR = Path(__file__).parent / "data"
TXT_FILE = DATA_DIR / "datos.txt"
CSV_FILE = DATA_DIR / "datos.csv"
JSON_FILE = DATA_DIR / "datos.json"

def asegurar_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

# TXT
def guardar_txt(registro: str):
    asegurar_data()
    with open(TXT_FILE, 'a', encoding="utf-8") as f:
        f.write(registro + '\n')

def leer_txt():
    asegurar_data()
    if not TXT_FILE.exists():
        return []
    with open(TXT_FILE, 'r', encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# JSON
def guardar_json(datos_peli: dict):
    asegurar_data()
    data = leer_json()
    data.append(datos_peli)
    with open(JSON_FILE, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def leer_json():
    asegurar_data()
    if not JSON_FILE.exists():
        return []
    with open(JSON_FILE, 'r', encoding="utf-8") as f:
        return json.load(f)
    
# CSV
def guardar_csv(datos_peli: dict):
    asegurar_data()
    existe = CSV_FILE.exists()
    # Para CSV, convertimos el diccionario en una lista de valores
    with open(CSV_FILE, 'a', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            # Ponemos los encabezados de Cimazon
            writer.writerow(['Nombre', 'Descripcion', 'Cantidad', 'Precio'])
        # Guardamos solo los valores del diccionario
        writer.writerow(datos_peli.values())

def leer_csv():
    asegurar_data()
    if not CSV_FILE.exists():
        return []
    
    with open(CSV_FILE, 'r', encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        return [row for row in reader if row]