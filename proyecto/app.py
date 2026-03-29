from flask import Flask, render_template, url_for, request, redirect, flash
from form import carteleraForm
from inventario.bd import init_db
from inventario.inventario import Inventario
from inventario.funcion import funciones as Producto, Boleto
from flask_sqlalchemy import SQLAlchemy
from inventario.inv_persistencia import guardar_txt, leer_txt, guardar_json, leer_json, guardar_csv, leer_csv
from inventario import inv_persistencia as persistencia
from conexion.conexion import conectar

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_llave_secreta'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invent.db'
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

# ruta para listar productos con sqlite
@app.route('/funciones')
def funciones_listar():
    inventario.cargar_desde_db()
    Lista_productos = inventario.productos.values()
    return render_template('cartelera.html', productos=Lista_productos)

# ruta para editar funciones con sqlite
@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def producto_editar(id):
    producto = inventario.productos.get(id)
    if producto is None:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('funciones_listar'))

    form = carteleraForm()

    if request.method == 'GET':
        form.nombre.data = producto.nombre
        form.descripcion.data = producto.descripcion
        form.cantidad.data = producto.cantidad
        form.precio.data = producto.precio

    if form.validate_on_submit():
        inventario.actualizar_producto(
            id,
            form.nombre.data,
            form.descripcion.data,
            int(form.cantidad.data),
            float(form.precio.data)
        )
        flash('Película actualizada exitosamente', 'success')
        return redirect(url_for('funciones_listar'))

    if request.method == 'POST' and not form.validate():
        flash('Errores de validación en el formulario', 'danger')

    return render_template('producto_editar.html', form=form, producto=producto)

# ruta para eliminar funciones con sqlite
@app.route('/productos/eliminar/<int:id>', methods=['GET', 'POST'])
def producto_eliminar(id):
    if inventario.eliminar_producto(id):
        flash('Película eliminada correctamente', 'warning')
    else:
        flash('No se pudo encontrar la película', 'danger')
    return redirect(url_for('funciones_listar'))

# ruta para listar productos con mysql
@app.route('/funciones_mysql')
def funciones_mysql():
    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            flash('Conexión a la base de datos fallida', 'danger')
            return redirect(url_for('inicio'))

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        cursor.execute('SELECT id, nombre, descripcion, cantidad, precio FROM productos')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        productos_mysql = [Producto(row[0], row[1], row[2], row[3], row[4]) for row in rows]
        return render_template('cartelera.html', productos=productos_mysql)
    except Exception as e:
        flash(f'Error al conectar a la base de datos: {e}', 'danger')
        return redirect(url_for('inicio'))
    
# ruta para la boleteria con mysql
@app.route('/boleteria')
def boleteria():
    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            flash('Conexión a la base de datos fallida', 'danger')
            return redirect(url_for('inicio'))

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        cursor.execute('SELECT id_boleto, pelicula, codigo_sala, butaca, hora_funcion FROM boleto')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        boletos_mysql = [Boleto(row[0], row[1], row[2], row[3], row[4]) for row in rows]
        return render_template('boleteria.html', boletos=boletos_mysql)
    except Exception as e:
        flash(f'Error al conectar a la base de datos: {e}', 'danger')
        return redirect(url_for('inicio'))


# ruta para los datos persistentes
@app.route('/datos', methods=['GET', 'POST'])
def datos():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        cantidad = request.form.get('cantidad')
        precio = request.form.get('precio')

        dic = {
            'nombre': nombre,
            'descripcion': descripcion,
            'cantidad': cantidad,
            'precio': precio
        }

        guardar_txt(f"{nombre}, {descripcion}, {cantidad}, {precio}")
        guardar_json(dic)
        guardar_csv(dic)
        flash('Datos guardados exitosamente', 'success')
        return redirect(url_for('datos'))

    datos_txt = leer_txt()
    datos_json = leer_json()
    datos_csv = leer_csv()
    return render_template('datos.html', datos_txt=datos_txt, datos_json=datos_json, datos_csv=datos_csv)

# ruta para conexión a la base de datos
@app.route('/conexion')
def conexion():
    error = None
    rows = None
    columns = None
    table = 'usuario'

    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            error = 'Conexión a la base de datos fallida'
            return render_template('conexion.html', error=error, rows=rows, columns=columns, table=table)

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        cursor.execute('SELECT * FROM usuario')
        rows = cursor.fetchall()
        columns = cursor.column_names
        cursor.close()
        conn.close()
        return render_template('conexion.html', error=error, rows=rows, columns=columns, table=table)
    except Exception as e:
        error = f'Error al conectar a la base de datos: {e}'
        return render_template('conexion.html', error=error, rows=rows, columns=columns, table=table)

if __name__ == '__main__':
    app.run(debug=True)
