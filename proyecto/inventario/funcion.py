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


class Boleto:
    def __init__(self, id_boleto, pelicula, codigo_sala, butaca, hora_funcion):
        self.id_boleto = id_boleto
        self.pelicula = pelicula
        self.codigo_sala = codigo_sala
        self.butaca = butaca
        self.hora_funcion = hora_funcion