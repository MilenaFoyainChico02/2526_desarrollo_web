from flask import Flask, render_template, url_for, request, redirect, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from form import carteleraForm, BoletoForm, FuncionForm
from forms.login_form import LoginForm
from forms.registro_form import RegistroForm

from models.boleto import Boleto
from services.inv_persistencia import guardar_txt, leer_txt, guardar_json, leer_json, guardar_csv, leer_csv

from conexion.conexion import conectar
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

# Dead DB Init Block Removed
@login_manager.user_loader
def load_user(user_id):
    return obtener_usuario_por_id(user_id)
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            flash('No tienes permisos de administrador para acceder a esta página.', 'danger')
            return redirect(url_for('inicio'))
        return f(*args, **kwargs)
    return decorated_function


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

@app.route('/exportar/pdf')
@admin_required
def exportar_pdf():
    if FPDF is None:
        flash('La librería FPDF no está instalada.', 'danger')
        return redirect(url_for('inicio'))

    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            flash('Conexión a la base de datos fallida', 'danger')
            return redirect(url_for('inicio'))

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        cursor.execute('SELECT id_funcion, descripcion, fecha_hora, total, metodo_pago FROM funcion')
        funciones_vendidas = cursor.fetchall() # Trae los datos reales
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f'Error al cargar datos para el PDF: {e}', 'danger')
        return redirect(url_for('inicio'))

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte de ventas", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(15, 10, "ID", 1)
    pdf.cell(65, 10, "Descripcion", 1) 
    pdf.cell(45, 10, "Fecha y hora", 1)
    pdf.cell(25, 10, "Total", 1)
    pdf.cell(40, 10, "Metodo de pago", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)

    for f in funciones_vendidas:
        pdf.cell(15, 10, str(f[0]), 1) # id_funcion
        
        desc = str(f[1])[:35]          # descripcion 
        pdf.cell(65, 10, desc, 1)
        
        pdf.cell(45, 10, str(f[2]), 1) # fecha_hora
        
        # Validamos el total por si es None en la base de datos
        total_val = float(f[3]) if f[3] is not None else 0.0
        pdf.cell(25, 10, f"${total_val:.2f}", 1) 
        
        pdf.cell(40, 10, str(f[4]), 1) # metodo_pago
        pdf.ln()

    # generación y descarga del PDF
    output_data = pdf.output(dest='S')
    if isinstance(output_data, str):
        output_bytes = output_data.encode('latin-1', 'replace') 
    elif isinstance(output_data, (bytes, bytearray)):
        output_bytes = bytes(output_data)
    else:
        output_bytes = str(output_data).encode('latin-1', 'replace')

    response = make_response(output_bytes)
    response.headers.set('Content-Disposition', 'attachment', filename='reporte_ventas_cimazon.pdf')
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
@admin_required
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
@admin_required
def funciones():
    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            flash('Conexión a la base de datos fallida', 'danger')
            return redirect(url_for('inicio'))

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        # Pedimos los 5 datos
        cursor.execute('SELECT id_funcion, descripcion, fecha_hora, total, metodo_pago FROM funcion')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        lista_funciones = []
        for row in rows:
            lista_funciones.append({
                'id_funcion': row[0],
                'descripcion': row[1],
                'fecha_hora': row[2],
                'total': float(row[3]) if row[3] is not None else 0,
                'metodo_pago': row[4]
            })

        return render_template('funciones.html', funciones=lista_funciones)

    except Exception as e:
        flash(f'Error en el sistema: {e}', 'danger')
        return redirect(url_for('inicio'))

@app.route('/funciones/nuevo', methods=['GET', 'POST'])
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
        
        productos_mysql = []
        for row in rows:
            productos_mysql.append({
                'id': row[0],
                'nombre': row[1],
                'descripcion': row[2],
                'cantidad': row[3],
                'precio': float(row[4]) if row[4] is not None else 0.0
            })
            
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


@app.route('/boleteria/nuevo', methods=['GET', 'POST'])
def boleteria_nuevo():
    form = BoletoForm()
    
    # Populate choices before validation
    try:
        conn = conectar()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute('USE cimazon')
            cursor.execute('SELECT id, nombre FROM productos')
            productos = cursor.fetchall()
            form.id_producto.choices = [(p[0], p[1]) for p in productos]
            
            cursor.execute('SELECT id_funcion, descripcion, fecha_hora FROM funcion')
            funciones = cursor.fetchall()
            form.id_funcion.choices = [(f[0], f"{f[1]} - {f[2]}") for f in funciones]
            cursor.close()
            conn.close()
    except Exception as e:
        flash(f'Error al cargar formulario: {e}', 'danger')
        return redirect(url_for('boleteria') if current_user.rol == 'admin' else url_for('productos'))

    pelicula_id = request.args.get('pelicula_id', type=int)
    if request.method == 'GET' and pelicula_id:
        form.id_producto.data = pelicula_id

    if form.validate_on_submit():
        try:
            conn = conectar()
            if conn is None or not conn.is_connected():
                flash('Conexión a la base de datos fallida', 'danger')
                return redirect(url_for('boleteria') if current_user.rol == 'admin' else url_for('productos'))

            cursor = conn.cursor()
            cursor.execute('USE cimazon')

            # Check stock and get pelicula string
            cursor.execute('SELECT cantidad, nombre FROM productos WHERE id = %s', (form.id_producto.data,))
            row = cursor.fetchone()
            cantidad_boletos = form.cantidad.data
            
            if row is None or row[0] < cantidad_boletos:
                flash(f'Error: La película no tiene {cantidad_boletos} asientos disponibles', 'danger')
                cursor.close()
                conn.close()
                return redirect(url_for('boleteria') if current_user.rol == 'admin' else url_for('productos'))
            
            pelicula_name = row[1]
            
            # Validación de las butacas contra la cantidad
            butacas_list = [b.strip() for b in form.butaca.data.split(',') if b.strip()]
            if len(butacas_list) != cantidad_boletos:
                flash(f'Error: Debes seleccionar exactamente {cantidad_boletos} butaca(s). Ocurrió una discrepancia.', 'danger')
                cursor.close()
                conn.close()
                return redirect(url_for('boleteria') if current_user.rol == 'admin' else url_for('productos'))

            # Get hora_funcion string
            cursor.execute('SELECT fecha_hora FROM funcion WHERE id_funcion = %s', (form.id_funcion.data,))
            func_row = cursor.fetchone()
            hora_funcion = func_row[0] if func_row else "N/A"
            
            # Asignación automática de sala basada en el ID del producto
            salas = ['Sala 1', 'Sala 2', 'Sala 3', 'Sala 4D', 'Sala VIP']
            codigo_sala = salas[form.id_producto.data % len(salas)]

            for butaca in butacas_list:
                cursor.execute(
                    '''INSERT INTO boleto (pelicula, codigo_sala, butaca, hora_funcion, id_producto, id_funcion) 
                       VALUES (%s, %s, %s, %s, %s, %s)''',
                    (pelicula_name, codigo_sala, butaca, 
                     hora_funcion, form.id_producto.data, form.id_funcion.data)
                )

            cursor.execute(
                'UPDATE productos SET cantidad = cantidad - %s WHERE id = %s',
                (cantidad_boletos, form.id_producto.data)
            )

            # Guardamos ambos cambios al mismo tiempo
            conn.commit()
            
            cursor.close()
            conn.close()
            
            flash('Boleto registrado y stock actualizado', 'success')
            return redirect(url_for('boleteria') if current_user.rol == 'admin' else url_for('productos'))
            
        except Exception as e:
            flash(f'Error al procesar el boleto: {e}', 'danger')
            return redirect(url_for('boleteria') if current_user.rol == 'admin' else url_for('productos'))

    return render_template('boleteria_form.html', form=form, titulo='Nuevo boleto')


@app.route('/boleteria/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
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

        form = BoletoForm()
        
        # Populate choices
        cursor.execute('SELECT id, nombre FROM productos')
        productos = cursor.fetchall()
        form.id_producto.choices = [(p[0], p[1]) for p in productos]
        
        cursor.execute('SELECT id_funcion, descripcion, fecha_hora FROM funcion')
        funciones = cursor.fetchall()
        form.id_funcion.choices = [(f[0], f"{f[1]} - {f[2]}") for f in funciones]

        if request.method == 'GET':
            form.id_producto.data = row[5] if len(row) > 5 else None
            form.id_funcion.data = row[6] if len(row) > 6 else None
            form.cantidad.data = 1 # Para obligar al script JS a dejar seleccionar solo 1 en edición
            form.codigo_sala.data = row[2] # codigo_sala
            form.butaca.data = row[3] # butaca

        if form.validate_on_submit():
            # Get textual strings for database
            cursor.execute('SELECT nombre FROM productos WHERE id = %s', (form.id_producto.data,))
            pel_row = cursor.fetchone()
            pelicula_name = pel_row[0] if pel_row else "Desconocida"
            
            cursor.execute('SELECT fecha_hora FROM funcion WHERE id_funcion = %s', (form.id_funcion.data,))
            func_row = cursor.fetchone()
            hora_funcion = func_row[0] if func_row else "N/A"

            # Obtenemos la primera butaca en caso de que vengan varias por error
            butaca_editar = form.butaca.data.split(',')[0].strip()
            
            # Asignación automática de sala basada en el ID del producto
            salas = ['Sala 1', 'Sala 2', 'Sala 3', 'Sala 4D', 'Sala VIP']
            codigo_sala = salas[form.id_producto.data % len(salas)]

            cursor.execute(
                'UPDATE boleto SET pelicula = %s, codigo_sala = %s, butaca = %s, hora_funcion = %s, id_producto = %s, id_funcion = %s WHERE id_boleto = %s',
                (pelicula_name, codigo_sala, butaca_editar, hora_funcion, form.id_producto.data, form.id_funcion.data, id)
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
@admin_required
def boleteria_eliminar(id):
    try:
        conn = conectar()
        if conn is None or not conn.is_connected():
            flash('Conexión a la base de datos fallida', 'danger')
            return redirect(url_for('boleteria'))

        cursor = conn.cursor()
        cursor.execute('USE cimazon')
        
        # Get id_producto to restore stock
        cursor.execute('SELECT id_producto FROM boleto WHERE id_boleto = %s', (id,))
        id_prod_row = cursor.fetchone()

        cursor.execute('DELETE FROM boleto WHERE id_boleto = %s', (id,))
        eliminados = cursor.rowcount
        
        if eliminados > 0 and id_prod_row:
            cursor.execute('UPDATE productos SET cantidad = cantidad + 1 WHERE id = %s', (id_prod_row[0],))
            
        conn.commit()
        cursor.close()
        conn.close()

        if eliminados > 0:
            flash('Boleto eliminado y stock restaurado', 'warning')
        else:
            flash('No se encontró el boleto a eliminar', 'danger')

        return redirect(url_for('boleteria'))
    except Exception as e:
        flash(f'Error al eliminar el boleto: {e}', 'danger')
        return redirect(url_for('boleteria'))


# ruta para los datos persistentes
@app.route('/datos', methods=['GET', 'POST'])
@admin_required
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
@admin_required
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
