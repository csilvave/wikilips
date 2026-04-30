import os
import sqlite3
import numpy as np
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'wikilips-secret-2025')

DB_PATH = os.path.join(os.path.dirname(__file__), 'BBDDWikilips.db')

# ─────────────────────────────────────────
# Utilidades de base de datos
# ─────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def obtener_marcas():
    with get_db() as conn:
        return conn.execute('SELECT ID, NombreMarca FROM Marca ORDER BY NombreMarca').fetchall()

def obtener_productos():
    with get_db() as conn:
        return conn.execute('SELECT ID, NombreProducto FROM Producto ORDER BY NombreProducto').fetchall()

def obtener_acabados():
    with get_db() as conn:
        return conn.execute('SELECT ID, NombreAcabado FROM Acabado').fetchall()

def obtener_formatos():
    with get_db() as conn:
        return conn.execute('SELECT ID, NombreFormato FROM Formato').fetchall()

def obtener_detalles_desde_bd():
    with get_db() as conn:
        return conn.execute(
            'SELECT D.R, D.G, D.B, M.NombreMarca, P.NombreProducto, D.Tono, D.RGB, '
            'A.NombreAcabado, F.NombreFormato '
            'FROM Detalle AS D '
            'JOIN Marca AS M ON D.Marca = M.ID '
            'JOIN Producto AS P ON D.Producto = P.ID '
            'JOIN Acabado AS A ON D.Acabado = A.ID '
            'JOIN Formato AS F ON D.Formato = F.ID'
        ).fetchall()

# ─────────────────────────────────────────
# Algoritmo de matching de colores (HSV)
# ─────────────────────────────────────────

def hsv_distance(color1, color2):
    dh = min(abs(color1[0] - color2[0]), 255 - abs(color1[0] - color2[0])) / 255.0
    ds = abs(color1[1] - color2[1]) / 255.0
    dv = abs(color1[2] - color2[2]) / 255.0
    return np.sqrt(dh**2 + ds**2 + dv**2)

def hex_to_rgb(hex_str):
    hex_str = hex_str.strip().lstrip('#')
    return (int(hex_str[:2], 16), int(hex_str[2:4], 16), int(hex_str[4:], 16))

def buscar_colores_similares(marca_id, producto_id, tono_rgb, n=3):
    detalles = obtener_detalles_desde_bd()
    tono_rgb_num = hex_to_rgb(tono_rgb)
    resultados = []

    for fila in detalles:
        r, g, b, marca, producto, tono, rgb, acabado, formato = fila
        if (marca_id, producto_id, tono_rgb.upper()) == (marca, producto, rgb.upper()):
            continue
        try:
            distancia = hsv_distance(tono_rgb_num, hex_to_rgb(rgb))
        except Exception:
            continue
        if distancia == 0:
            continue
        resultados.append((distancia, {
            'NombreMarca': marca, 'NombreProducto': producto,
            'Tono': tono, 'RGB': rgb,
            'NombreAcabado': acabado, 'NombreFormato': formato
        }))

    resultados.sort(key=lambda x: x[0])
    return [r[1] for r in resultados[:n]]

# ─────────────────────────────────────────
# Rutas públicas
# ─────────────────────────────────────────

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    marcas = obtener_marcas()
    if request.method == 'POST':
        marca_id    = int(request.form['marca'])
        producto_id = int(request.form['producto'])
        tono_rgb    = request.form['tono']
        colores_similares = buscar_colores_similares(marca_id, producto_id, tono_rgb, n=3)
        return render_template('index.html', marcas=marcas,
                               colores_similares=colores_similares,
                               tono_rgb=tono_rgb,
                               selected_marca=str(marca_id),
                               selected_producto=str(producto_id))
    return render_template('index.html', marcas=marcas,
                           colores_similares=[], selected_marca=None, selected_producto=None)

@app.route('/productos/<int:marca_id>')
def productos_por_marca(marca_id):
    with get_db() as conn:
        rows = conn.execute(
            'SELECT ID, NombreProducto FROM Producto WHERE Marca = ? ORDER BY NombreProducto',
            (marca_id,)
        ).fetchall()
    return jsonify([(str(r[0]), r[1]) for r in rows])

@app.route('/tonos/<int:marca_id>/<int:producto_id>')
def tonos_por_producto(marca_id, producto_id):
    with get_db() as conn:
        rows = conn.execute(
            'SELECT RGB, Tono FROM Detalle WHERE Marca = ? AND Producto = ?',
            (marca_id, producto_id)
        ).fetchall()
    return jsonify([(r[0], r[1]) for r in rows])

# ─────────────────────────────────────────
# Rutas de administración
# ─────────────────────────────────────────

def verificar_credenciales(usuario, contrasena):
    admin_user = os.environ.get('ADMIN_USER', 'admin')
    admin_pass = os.environ.get('ADMIN_PASS', 'admin123')
    return usuario == admin_user and contrasena == admin_pass

@app.route('/acceso-administrador', methods=['GET', 'POST'])
def acceso_administrador():
    mensaje = None
    if request.method == 'POST':
        if verificar_credenciales(request.form['usuario'], request.form['contrasena']):
            return redirect(url_for('admin_home'))
        mensaje = 'Usuario o contraseña incorrectos. Intente nuevamente.'
    return render_template('login.html', mensaje=mensaje)

@app.route('/admin_home', methods=['GET', 'POST'])
def admin_home():
    if request.method == 'POST':
        if 'agregar_marca' in request.form:
            return redirect('/agregar-marca')
        elif 'agregar_producto' in request.form:
            return redirect('/agregar-producto')
        elif 'agregar_detalle' in request.form:
            return redirect('/agregar-detalle')
    detalles = obtener_detalles_desde_bd()
    return render_template('admin_home.html', detalles=detalles)

@app.route('/agregar-marca', methods=['GET', 'POST'])
def agregar_marca():
    if request.method == 'POST':
        with get_db() as conn:
            conn.execute('INSERT INTO Marca (NombreMarca) VALUES (?)',
                         (request.form['nombre_marca'].strip(),))
        return redirect('/admin_home')
    return render_template('agregar_marca.html')

@app.route('/agregar-producto', methods=['GET', 'POST'])
def agregar_producto():
    marcas = obtener_marcas()
    if request.method == 'POST':
        with get_db() as conn:
            conn.execute('INSERT INTO Producto (Marca, NombreProducto) VALUES (?, ?)',
                         (int(request.form['marca']), request.form['nombre_producto'].strip()))
        return redirect('/admin_home')
    return render_template('agregar_producto.html', marcas=marcas)

@app.route('/agregar-detalle', methods=['GET', 'POST'])
def agregar_detalle():
    marcas = obtener_marcas()
    productos = obtener_productos()
    acabados = obtener_acabados()
    formatos = obtener_formatos()
    if request.method == 'POST':
        try:
            r = format(int(request.form['r'], 16), '02X')
            g = format(int(request.form['g'], 16), '02X')
            b = format(int(request.form['b'], 16), '02X')
        except ValueError:
            flash('Los valores RGB deben ser hexadecimales válidos.', 'error')
            return render_template('agregar_detalle.html', marcas=marcas, productos=productos,
                                   acabados=acabados, formatos=formatos)
        marca_id    = int(request.form['marca'])
        producto_id = int(request.form['producto'])
        nombre_tono = request.form['nombre_tono'].strip()
        rgb_hex     = f'{r}{g}{b}'
        with get_db() as conn:
            if conn.execute('SELECT COUNT(*) FROM Detalle WHERE Marca=? AND Producto=? AND Tono=?',
                            (marca_id, producto_id, nombre_tono)).fetchone()[0]:
                flash('Este tono ya existe en la base de datos.', 'error')
                return render_template('agregar_detalle.html', marcas=marcas, productos=productos,
                                       acabados=acabados, formatos=formatos)
            conn.execute(
                'INSERT INTO Detalle (Marca, Producto, Tono, Acabado, Formato, RGB, R, G, B) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (marca_id, producto_id, nombre_tono,
                 int(request.form['acabado']), int(request.form['formato']), rgb_hex, r, g, b)
            )
        return redirect('/admin_home')
    return render_template('agregar_detalle.html', marcas=marcas, productos=productos,
                           acabados=acabados, formatos=formatos)

@app.route('/editar/<int:detalle_id>', methods=['GET', 'POST'])
def editar_registro(detalle_id):
    marcas = obtener_marcas()
    acabados = obtener_acabados()
    formatos = obtener_formatos()
    with get_db() as conn:
        detalle = conn.execute('SELECT * FROM Detalle WHERE ID = ?', (detalle_id,)).fetchone()
    if not detalle:
        flash('Tono no encontrado.', 'error')
        return redirect('/admin_home')
    if request.method == 'POST':
        try:
            r = format(int(request.form['r'], 16), '02X')
            g = format(int(request.form['g'], 16), '02X')
            b = format(int(request.form['b'], 16), '02X')
        except ValueError:
            flash('Los valores RGB deben ser hexadecimales válidos.', 'error')
            return render_template('editar_registro.html', detalle=detalle,
                                   marcas=marcas, acabados=acabados, formatos=formatos)
        with get_db() as conn:
            conn.execute(
                'UPDATE Detalle SET Tono=?, Acabado=?, Formato=?, RGB=?, R=?, G=?, B=? WHERE ID=?',
                (request.form['nombre_tono'].strip(), int(request.form['acabado']),
                 int(request.form['formato']), f'{r}{g}{b}', r, g, b, detalle_id)
            )
        return redirect('/admin_home')
    return render_template('editar_registro.html', detalle=detalle,
                           marcas=marcas, acabados=acabados, formatos=formatos)

@app.route('/borrar/<int:detalle_id>', methods=['POST'])
def borrar_registro(detalle_id):
    with get_db() as conn:
        conn.execute('DELETE FROM Detalle WHERE ID = ?', (detalle_id,))
    return redirect('/admin_home')

if __name__ == '__main__':
    app.run(debug=False)
