from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange

class carteleraForm(FlaskForm):
    nombre = StringField('Nombre de la película', validators=[DataRequired(), Length(min=2, max=200)])
    descripcion = StringField('Descripción de la película', validators=[DataRequired(), Length(min=10, max=1000)])
    cantidad = DecimalField('Cantidad disponible', validators=[DataRequired(), NumberRange(min=0)], places=0)
    precio = DecimalField('Precio por entrada', validators=[DataRequired(),NumberRange(min=0.00)], places=2)
    submit = SubmitField('Agregar película')


class BoletoForm(FlaskForm):
    id_producto = SelectField('Película', coerce=int, validators=[DataRequired()])
    id_funcion = SelectField('Hora de la función', coerce=int, validators=[DataRequired()])
    cantidad = SelectField('Cantidad de boletos', choices=[(i, str(i)) for i in range(1, 11)], coerce=int, default=1)
    codigo_sala = SelectField('Código de sala', choices=[('Sala 1', 'Sala 1 - Tradicional'), ('Sala 2', 'Sala 2 - Tradicional'), ('Sala 3', 'Sala 3 - 3D'), ('Sala 4D', 'Sala 4 - 4D Experiencia'), ('Sala VIP', 'Sala VIP - Lounge')], validate_choice=False)
    butaca = StringField('Butaca', validators=[DataRequired(), Length(min=1, max=100)])
    
    submit = SubmitField('Guardar boleto')


class FuncionForm(FlaskForm):
    descripcion = StringField('Descripción', validators=[DataRequired(), Length(min=5, max=500)])
    fecha_hora = StringField('Fecha y hora', validators=[DataRequired(), Length(min=5, max=100)])
    total = DecimalField('Total', validators=[DataRequired(), NumberRange(min=0)], places=2)
    metodo_pago = StringField('Método de pago', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Guardar función')
