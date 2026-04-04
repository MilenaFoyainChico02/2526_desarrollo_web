from flask import Flask, render_template, url_for, request, redirect, flash
from form import carteleraForm, BoletoForm, FuncionForm
from inventario.bd import init_db
from inventario.inventario import Inventario
from inventario.funcion import funciones as Producto, Boleto
from flask_sqlalchemy import SQLAlchemy
from inventario.inv_persistencia import guardar_txt, leer_txt, guardar_json, leer_json, guardar_csv, leer_csv
from inventario import inv_persistencia as persistencia
from conexion.conexion import conectar
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms.login_form import LoginForm
from forms.registro_form import RegistroForm
from services.usuario_service import crear_tabla_usuario, obtener_usuario_por_id, obtener_usuario_por_email, registrar_usuario

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

from flask import make_response

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_llave_secreta'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Debes iniciar sesión para acceder a esta página'
login_manager.login_message_category = 'warning'

crear_tabla_usuario()

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invent.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)

"""
db.init_app(app)

with app.app_context():
    db.create_all()

inventario = Inventario()
inventario.cargar_desde_db()
"""
@login_manager.user_loader
def load_user(user_id):
    return obtener_usuario_por_id(user_id)


def listar_productos():
    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            return []

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        cursor.execute('SELECT id, nombre, descripcion, cantidad, precio FROM productos')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return [
            {
                'id_producto': row[0],
                'nombre': row[1],
                'precio': row[4],
                'cantidad': row[3]
            }
            for row in rows
        ]
    except Exception:
        return []


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistroForm()

    if form.validate_on_submit():
        nombre = form.nombre.data
        email = form.email.data
        password = request.form['password']

        usuario_existente = obtener_usuario_por_email(email)
        if usuario_existente:
            flash('Ya existe un usuario con ese correo', 'danger')
            return redirect(url_for('registro'))

        password_hash = generate_password_hash(password)

        registrar_usuario(nombre, email, password_hash)

        flash('Usuario registrado correctamente', 'success')
        return redirect(url_for('login'))

    return render_template('auth/registro.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        usuario = obtener_usuario_por_email(email)

        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')

    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('inicio'))

# ruta de exportar PDF 
@app.route('/exportar/pdf')
@login_required
def exportar_pdf():
    if FPDF is None:
        flash('La librería FPDF no está instalada. Instala el paquete fpdf y reinicia la aplicación.', 'danger')
        return redirect(url_for('inicio'))

    productos = listar_productos()

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte de funciones", ln=True, align="C")

    pdf.ln(10)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(20, 10, "ID", 1)
    pdf.cell(60, 10, "Nombre", 1)
    pdf.cell(30, 10, "Precio", 1)
    pdf.cell(30, 10, "Cantidad", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)

    for p in productos:
        pdf.cell(20, 10, str(p['id_producto']), 1)
        pdf.cell(60, 10, p['nombre'], 1)
        pdf.cell(30, 10, f"${p['precio']}", 1)
        pdf.cell(30, 10, str(p['cantidad']), 1)
        pdf.ln()

    output_data = pdf.output(dest='S')
    if isinstance(output_data, str):
        output_bytes = output_data.encode('latin-1')
    elif isinstance(output_data, (bytes, bytearray)):
        output_bytes = bytes(output_data)
    else:
        output_bytes = str(output_data).encode('latin-1')

    response = make_response(output_bytes)
    response.headers.set('Content-Disposition', 'attachment', filename='productos.pdf')
    response.headers.set('Content-Type', 'application/pdf')

    return response

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

        try:
            conn = conectar()
            if conn is None or not conn.is_connected():
                flash('Conexión a la base de datos fallida', 'danger')
                return redirect(url_for('funciones_mysql'))

            cursor = conn.cursor()
            cursor.execute('USE cimazon')
            cursor.execute(
                'INSERT INTO productos (nombre, descripcion, cantidad, precio) VALUES (%s, %s, %s, %s)',
                (nombre, descripcion, cantidad, precio)
            )
            conn.commit()
            cursor.close()
            conn.close()

            flash('Función agregada exitosamente', 'success')
            return redirect(url_for('funciones_mysql'))
        except Exception as e:
            flash(f'Error al guardar la función: {e}', 'danger')
            return redirect(url_for('funciones_mysql'))

    return render_template('cartelera_form.html', form=form, titulo='Agregar nueva función')

@app.route('/funciones')
@login_required
def funciones():
    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            flash('Conexión a la base de datos fallida', 'danger')
            return redirect(url_for('inicio'))

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        cursor.execute('SELECT id_funcion, descripcion, fecha_hora, total, metodo_pago FROM funcion')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        funciones = [
            {
                'id_funcion': row[0],
                'descripcion': row[1],
                'fecha_hora': row[2],
                'total': float(row[3]) if row[3] is not None else 0,
                'metodo_pago': row[4]
            }
            for row in rows
        ]

        return render_template('funciones.html', funciones=funciones)
    except Exception as e:
        flash(f'Error al cargar funciones: {e}', 'danger')
        return redirect(url_for('inicio'))

@app.route('/funciones/nuevo', methods=['GET', 'POST'])
@login_required
def funciones_nuevo():
    form = FuncionForm()
    if form.validate_on_submit():
        try:
            conn = conectar()
            if conn is None or not conn.is_connected():
                flash('Conexión a la base de datos fallida', 'danger')
                return redirect(url_for('funciones'))

            cursor = conn.cursor()
            cursor.execute('USE cimazon')
            cursor.execute(
                'INSERT INTO funcion (descripcion, fecha_hora, total, metodo_pago) VALUES (%s, %s, %s, %s)',
                (form.descripcion.data, form.fecha_hora.data, float(form.total.data), form.metodo_pago.data)
            )
            conn.commit()
            cursor.close()
            conn.close()

            flash('Función registrada correctamente', 'success')
            return redirect(url_for('funciones'))
        except Exception as e:
            flash(f'Error al guardar la función: {e}', 'danger')
            return redirect(url_for('funciones'))

    return render_template('funciones_form.html', form=form, titulo='Nueva función')

@app.route('/funciones/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def funciones_editar(id):
    form = FuncionForm()
    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            flash('Conexión a la base de datos fallida', 'danger')
            return redirect(url_for('funciones'))

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        cursor.execute('SELECT descripcion, fecha_hora, total, metodo_pago FROM funcion WHERE id_funcion = %s', (id,))
        row = cursor.fetchone()

        if row is None:
            cursor.close()
            conn.close()
            flash('Función no encontrada', 'danger')
            return redirect(url_for('funciones'))

        if request.method == 'GET':
            form.descripcion.data = row[0]
            form.fecha_hora.data = row[1]
            form.total.data = float(row[2]) if row[2] is not None else 0
            form.metodo_pago.data = row[3]

        if form.validate_on_submit():
            cursor.execute(
                'UPDATE funcion SET descripcion = %s, fecha_hora = %s, total = %s, metodo_pago = %s WHERE id_funcion = %s',
                (form.descripcion.data, form.fecha_hora.data, float(form.total.data), form.metodo_pago.data, id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Función actualizada correctamente', 'success')
            return redirect(url_for('funciones'))

        cursor.close()
        conn.close()
        return render_template('funciones_form.html', form=form, titulo='Editar función')
    except Exception as e:
        flash(f'Error al editar la función: {e}', 'danger')
        return redirect(url_for('funciones'))

@app.route('/funciones/eliminar/<int:id>', methods=['POST', 'GET'])
@login_required
def funciones_eliminar(id):
    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            flash('Conexión a la base de datos fallida', 'danger')
            return redirect(url_for('funciones'))

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        cursor.execute('DELETE FROM funcion WHERE id_funcion = %s', (id,))
        conn.commit()
        eliminados = cursor.rowcount
        cursor.close()
        conn.close()

        if eliminados > 0:
            flash('Función eliminada correctamente', 'warning')
        else:
            flash('No se encontró la función', 'danger')

        return redirect(url_for('funciones'))
    except Exception as e:
        flash(f'Error al eliminar la función: {e}', 'danger')
        return redirect(url_for('funciones'))

@app.route('/productos')
def productos():
    return redirect(url_for('funciones_mysql'))

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def producto_editar(id):
    form = carteleraForm()
    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            flash('Conexión a la base de datos fallida', 'danger')
            return redirect(url_for('funciones_mysql'))

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        cursor.execute('SELECT id, nombre, descripcion, cantidad, precio FROM productos WHERE id = %s', (id,))
        row = cursor.fetchone()

        if row is None:
            cursor.close()
            conn.close()
            flash('Función no encontrada', 'danger')
            return redirect(url_for('funciones_mysql'))

        if request.method == 'GET':
            form.nombre.data = row[1]
            form.descripcion.data = row[2]
            form.cantidad.data = row[3]
            form.precio.data = row[4]

        if form.validate_on_submit():
            cursor.execute(
                'UPDATE productos SET nombre = %s, descripcion = %s, cantidad = %s, precio = %s WHERE id = %s',
                (form.nombre.data, form.descripcion.data, int(form.cantidad.data), float(form.precio.data), id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Función actualizada exitosamente', 'success')
            return redirect(url_for('funciones_mysql'))

        cursor.close()
        conn.close()
        return render_template('producto_editar.html', form=form, producto=row)
    except Exception as e:
        flash(f'Error al editar la función: {e}', 'danger')
        return redirect(url_for('funciones_mysql'))

@app.route('/productos/eliminar/<int:id>', methods=['GET', 'POST'])
def producto_eliminar(id):
    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            flash('Conexión a la base de datos fallida', 'danger')
            return redirect(url_for('funciones_mysql'))

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
        conn.commit()
        eliminados = cursor.rowcount
        cursor.close()
        conn.close()

        if eliminados > 0:
            flash('Función eliminada correctamente', 'warning')
        else:
            flash('No se encontró la función', 'danger')

        return redirect(url_for('funciones_mysql'))
    except Exception as e:
        flash(f'Error al eliminar la función: {e}', 'danger')
        return redirect(url_for('funciones_mysql'))

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
        cursor.execute('SELECT * from boleto')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        boletos_mysql = [Boleto(row[0], row[1], row[2], row[3], row[4]) for row in rows]
        return render_template('boleteria.html', boletos=boletos_mysql)
    except Exception as e:
        flash(f'Error al conectar a la base de datos: {e}', 'danger')
        return redirect(url_for('inicio'))


@app.route('/boleteria/nuevo', methods=['GET', 'POST'])
def boleteria_nuevo():
    form = BoletoForm()
    if form.validate_on_submit():
        pelicula = form.pelicula.data
        codigo_sala = form.codigo_sala.data
        butaca = form.butaca.data
        hora_funcion = form.hora_funcion.data

        try:
            conn = conectar()
            if conn is None or not conn.is_connected():
                flash('Conexión a la base de datos fallida', 'danger')
                return redirect(url_for('boleteria'))

            cursor = conn.cursor()
            cursor.execute('USE cimazon')
            cursor.execute(
                'INSERT INTO boleto (pelicula, codigo_sala, butaca, hora_funcion) VALUES (%s, %s, %s, %s)',
                (pelicula, codigo_sala, butaca, hora_funcion)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Boleto agregado exitosamente', 'success')
            return redirect(url_for('boleteria'))
        except Exception as e:
            flash(f'Error al guardar el boleto: {e}', 'danger')
            return redirect(url_for('boleteria'))

    return render_template('boleteria_form.html', form=form, titulo='Nuevo boleto')


@app.route('/boleteria/editar/<int:id>', methods=['GET', 'POST'])
def boleteria_editar(id):
    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            flash('Conexión a la base de datos fallida', 'danger')
            return redirect(url_for('boleteria'))

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        cursor.execute('SELECT * FROM boleto WHERE id_boleto = %s', (id,))
        row = cursor.fetchone()

        if row is None:
            cursor.close()
            conn.close()
            flash('Boleto no encontrado', 'danger')
            return redirect(url_for('boleteria'))

        boleto = Boleto(row[0], row[1], row[2], row[3], row[4])
        form = BoletoForm()

        if request.method == 'GET':
            form.pelicula.data = boleto.pelicula
            form.codigo_sala.data = boleto.codigo_sala
            form.butaca.data = boleto.butaca
            form.hora_funcion.data = boleto.hora_funcion

        if form.validate_on_submit():
            cursor.execute(
                'UPDATE boleto SET pelicula = %s, codigo_sala = %s, butaca = %s, hora_funcion = %s WHERE id_boleto = %s',
                (form.pelicula.data, form.codigo_sala.data, form.butaca.data, form.hora_funcion.data, id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Boleto actualizado exitosamente', 'success')
            return redirect(url_for('boleteria'))

        cursor.close()
        conn.close()
        return render_template('boleteria_form.html', form=form, titulo='Editar boleto')
    except Exception as e:
        flash(f'Error al editar el boleto: {e}', 'danger')
        return redirect(url_for('boleteria'))


@app.route('/boleteria/eliminar/<int:id>', methods=['GET', 'POST'])
def boleteria_eliminar(id):
    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            flash('Conexión a la base de datos fallida', 'danger')
            return redirect(url_for('boleteria'))

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        cursor.execute('DELETE FROM boleto WHERE id_boleto = %s', (id,))
        conn.commit()
        eliminados = cursor.rowcount
        cursor.close()
        conn.close()

        if eliminados > 0:
            flash('Boleto eliminado correctamente', 'warning')
        else:
            flash('No se encontró el boleto a eliminar', 'danger')

        return redirect(url_for('boleteria'))
    except Exception as e:
        flash(f'Error al eliminar el boleto: {e}', 'danger')
        return redirect(url_for('boleteria'))


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
