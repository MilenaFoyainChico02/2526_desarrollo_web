class funciones:
    def __init__(self, id_funcion, id_usuario, descripcion, fecha_hora, total, metodo_pago):
        self.id_funcion = id_funcion
        self.id_usuario = id_usuario
        self.descripcion = descripcion
        self.fecha_hora = fecha_hora
        self.total = total
        self.metodo_pago = metodo_pago

    def to_tuple(self):
    
        return (self.id_funcion, self.id_usuario, self.descripcion, self.fecha_hora, self.total, self.metodo_pago)

    def to_dict(self):
        return {
            'id_funcion': self.id_funcion,
            'id_usuario': self.id_usuario,
            'descripcion': self.descripcion,
            'fecha_hora': self.fecha_hora,
            'total': self.total,
            'metodo_pago': self.metodo_pago
        }

    def mostrar_total(self):
        return f"${self.total:.2f}"


class Boleto:
    def __init__(self, id_boleto, pelicula, codigo_sala, butaca, hora_funcion):
        self.id_boleto = id_boleto
        self.pelicula = pelicula
        self.codigo_sala = codigo_sala
        self.butaca = butaca
        self.hora_funcion = hora_funcion