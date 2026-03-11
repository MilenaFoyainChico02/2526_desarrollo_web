# clase funciones
class funciones:
    def __init__(self, id, nombre, descripcion, cantidad, precio):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.cantidad = cantidad
        self.precio = precio

    # tuple
    def to_tuple(self):
        return (self.nombre, self.descripcion, self.cantidad, self.precio)
    # dict
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'cantidad': self.cantidad,
            'precio': self.precio
        }
    def mostrar_precio(self):
        return f"${self.precio:.2f}"