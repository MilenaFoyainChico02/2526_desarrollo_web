# formulario de cartelera

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange

class carteleraForm(FlaskForm):
    nombre = StringField('Nombre de la película', validators=[DataRequired(), Length(min=2, max=200)])
    descripcion = StringField('Descripción de la película', validators=[DataRequired(), Length(min=10, max=1000)])
    cantidad = DecimalField('Cantidad disponible', validators=[DataRequired(), NumberRange(min=0)], places=0)
    precio = DecimalField('Precio por entrada', validators=[DataRequired(),NumberRange(min=0.00)], places=2)
    submit = SubmitField('Agregar película')


class BoletoForm(FlaskForm):
    pelicula = StringField('Película', validators=[DataRequired(), Length(min=2, max=200)])
    codigo_sala = StringField('Código de sala', validators=[DataRequired(), Length(min=1, max=50)])
    butaca = StringField('Butaca', validators=[DataRequired(), Length(min=1, max=50)])
    hora_funcion = StringField('Hora de la función', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Guardar boleto')


class FuncionForm(FlaskForm):
    descripcion = StringField('Descripción', validators=[DataRequired(), Length(min=5, max=500)])
    fecha_hora = StringField('Fecha y hora', validators=[DataRequired(), Length(min=5, max=100)])
    total = DecimalField('Total', validators=[DataRequired(), NumberRange(min=0)], places=2)
    metodo_pago = StringField('Método de pago', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Guardar función')
