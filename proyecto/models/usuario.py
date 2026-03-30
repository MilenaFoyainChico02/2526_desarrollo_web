from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, correo, password):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.correo = correo
        self.email = correo
        self.password = password

    def get_id(self):
        return str(self.id_usuario)