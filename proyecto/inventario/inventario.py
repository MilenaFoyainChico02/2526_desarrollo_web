from .funcion import funciones as Funcion
from .bd import init_db, get_connection

class Inventario:
    def __init__(self):
        self.funciones = {} # Cambiado de productos a funciones

    def cargar_desde_db(self):
        with get_connection() as conn:
            # Seleccionamos de la tabla 'funcion'
            cursor = conn.execute('SELECT id_funcion, id_usuario, descripcion, fecha_hora, total, metodo_pago FROM funcion')
            for row in cursor.fetchall():
                # Creamos el objeto Funcion con las columnas de tu imagen
                nueva_f = Funcion(
                    row['id_funcion'], 
                    row['id_usuario'], 
                    row['descripcion'], 
                    row['fecha_hora'], 
                    row['total'], 
                    row['metodo_pago']
                )
                self.funciones[nueva_f.id_funcion] = nueva_f

    def listar_funciones(self):
        return [f.to_tuple() for f in self.funciones.values()]
    
    # Buscar por descripción
    def buscar_por_descripcion(self, texto):
        texto = texto.lower().strip()
        resultados = []
        for f in self.funciones.values():
            if texto in f.descripcion.lower():
                resultados.append(f.to_tuple())
        return resultados

    # Agregar función 
    def agregar_funcion(self, id_usuario, descripcion, fecha_hora, total, metodo_pago):
        query = '''
            INSERT INTO funcion (id_usuario, descripcion, fecha_hora, total, metodo_pago) 
            VALUES (?, ?, ?, ?, ?)
        '''
        with get_connection() as conn:
            cursor = conn.execute(query, (id_usuario, descripcion, fecha_hora, total, metodo_pago))
            conn.commit()
            nuevo_id = cursor.lastrowid
            
            nueva_f = Funcion(nuevo_id, id_usuario, descripcion, fecha_hora, total, metodo_pago)
            self.funciones[nuevo_id] = nueva_f

    # Actualizar función
    def actualizar_funcion(self, id_funcion, id_usuario, descripcion, fecha_hora, total, metodo_pago):
        if id_funcion in self.funciones:
            try:
                with get_connection() as conn:
                    conn.execute(
                        '''UPDATE funcion SET id_usuario = ?, descripcion = ?, fecha_hora = ?, total = ?, metodo_pago = ? 
                           WHERE id_funcion = ?''',
                        (id_usuario, descripcion, fecha_hora, total, metodo_pago, id_funcion)
                    )
                    conn.commit() 
                
                # Actualizar objeto en memoria
                f = self.funciones[id_funcion]
                f.id_usuario = id_usuario
                f.descripcion = descripcion
                f.fecha_hora = fecha_hora
                f.total = total
                f.metodo_pago = metodo_pago
                return True
            except Exception as e:
                print(f"Error en la base de datos: {e}")
                return False
        return False
            
    # Eliminar función
    def eliminar_funcion(self, id_funcion):
        if id_funcion in self.funciones:
            with get_connection() as conn:
                conn.execute('DELETE FROM funcion WHERE id_funcion = ?', (id_funcion,))
                conn.commit() 
            
            del self.funciones[id_funcion]
            return True
        return False