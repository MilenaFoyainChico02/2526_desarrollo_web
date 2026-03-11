# clase inventario
from .funcion import funciones as Producto
from .bd import init_db, get_connection

class Inventario:
    def __init__(self):
        self.productos = {}
        self.nombres = set()

    def cargar_desde_db(self):
        with get_connection() as conn:
            cursor = conn.execute('SELECT * FROM productos')
            for row in cursor.fetchall():
                nuevo_p = Producto(row['id'], row['nombre'], row['descripcion'], row['cantidad'], row['precio'])
                self.productos[nuevo_p.id] = nuevo_p
                self.nombres.add(nuevo_p.nombre)

    # listar productos de tuplas
    def listar_productos(self):
        return [self.producto.to_tuple() for producto in self.productos.values()]
   
    # buscar por nombre
    def buscar_por_nombre(self, texto):
        texto = texto.lower().strip()
        resultados = []
        for producto in self.productos.values():
            if texto in producto.nombre.lower() or texto in producto.descripcion.lower():
                resultados.append(producto.to_tuple())

    # agregar productos 
    def agregar_producto(self, nombre, descripcion, cantidad, precio):
        with get_connection() as conn:
            cursor = conn.execute('INSERT INTO productos (nombre, descripcion, cantidad, precio) VALUES (?, ?, ?, ?)',
                                (nombre, descripcion, cantidad, precio))
            conn.commit()
            nuevo_id = cursor.lastrowid
            nuevo_producto = Producto(nuevo_id, nombre, descripcion, cantidad, precio)
            self.productos[nuevo_id] = nuevo_producto
            self.nombres.add(nombre)

    # actualizar los productos en la bd
    def actualizar_producto(self, id, nombre, descripcion, cantidad, precio):
    # Verificamos si el producto existe en la colección POO
     if id in self.productos:
        try:
            with get_connection() as conn:
                # El orden debe ser: nombre(1), descripcion(2), cantidad(3), precio(4) y el ID al final(5)
                conn.execute(
                    'UPDATE productos SET nombre = ?, descripcion = ?, cantidad = ?, precio = ? WHERE id = ?',
                    (nombre, descripcion, cantidad, precio, id)
                )
                conn.commit() # Confirmación obligatoria para SQLite
            
            # Actualizamos también el objeto en memoria (Colección POO)
            producto = self.productos[id]
            producto.nombre = nombre
            producto.descripcion = descripcion
            producto.cantidad = cantidad
            producto.precio = precio
            return True
        except Exception as e:
            print(f"Error en la base de datos: {e}")
            return False
     return False
            
    # eliminar producto
    def eliminar_producto(self, id):
    # Verificamos si existe en nuestra colección POO
     if id in self.productos:
        # Borrado físico en la base de datos
        with get_connection() as conn:
            
            conn.execute('DELETE FROM productos WHERE id = ?', (id,))
            conn.commit() 
        
        del self.productos[id]
        return True
     return False