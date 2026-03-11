from flask import Flask, render_template, url_for, request, redirect, flash
from form import carteleraForm
from inventario.bd import init_db
from inventario.inventario import Inventario
from inventario.funcion import funciones as Producto
from flask_sqlalchemy import SQLAlchemy
from inventario.inv_persistencia import guardar_txt, leer_txt, guardar_json, leer_json, guardar_csv, leer_csv
from inventario import inv_persistencia as persistencia

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_llave_secreta'

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite=///invent.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

init_db()
inventario = Inventario()
inventario.cargar_desde_db()

# ruta principal
@app.route('/')
def inicio():
    return render_template('index.html')

# rutas de navegación
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cartelera/nuevo', methods=['GET', 'POST'])
def cartelera_nuevo():
    form = carteleraForm()
    if form.validate_on_submit():
        
        nombre = form.nombre.data
        descripcion = form.descripcion.data
        cantidad = int(form.cantidad.data)
        precio = float(form.precio.data)

        inventario.agregar_producto(nombre, descripcion, cantidad, precio)
        flash('Película agregada exitosamente', 'success')
        return redirect(url_for('funciones_listar'))
    return render_template('cartelera_form.html', form=form)

# ruta para listar productos
@app.route('/funciones')
def funciones_listar():
    inventario.cargar_desde_db() 
    Lista_productos =inventario.productos.values()
    return render_template('cartelera.html', productos=Lista_productos)

# ruta para editar funciones
@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def producto_editar(id):
    producto = inventario.productos.get(id)
    form = carteleraForm()
    if form.validate_on_submit():
        print("¡El formulario es válido! Intentando guardar...") 
        inventario.actualizar_producto(id, form.nombre.data, form.descripcion.data, 
                                      int(form.cantidad.data), float(form.precio.data))
        return redirect(url_for('funciones_listar'))
    
    if request.method == 'POST':
        print("Errores de validación:", form.errors) 
    
    return render_template('producto_editar.html', form=form, producto=producto)

# ruta para eliminar funciones
@app.route('/productos/eliminar/<int:id>', methods=['GET', 'POST'])
def producto_eliminar(id):

    if inventario.eliminar_producto(id):
        flash('Película eliminada correctamente', 'warning')
    else:
        flash('No se pudo encontrar la película', 'danger')
    
    return redirect(url_for('funciones_listar'))


# ruta para los datos persistentes 
@app.route('datos')
def datos():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        cantidad = request.form.get('cantidad')
        precio = request.form.get('precio')

        # registrar en base de datos
        dic = {
            'nombre': nombre,
            'descripcion': descripcion,
            'cantidad': cantidad,
            'precio': precio
        }

        # guardar en los tres formatos
        guardar_txt(f"{nombre}, {descripcion}, {cantidad}, {precio}")
        guardar_json(dic)
        flash('Datos guardados exitosamente', 'success')
        return redirect(url_for('datos'))
    
    # leer en los tres formatos
    datos_txt = leer_txt()
    datos_json = leer_json()
    datos_csv = leer_csv()
    return render_template('datos.html', datos_txt=datos_txt, datos_json=datos_json, datos_csv=datos_csv)

if __name__ == '__main__':
    app.run(debug=True)