import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from cs50 import SQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configurar el directorio para subir imágenes
UPLOAD_FOLDER = 'static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Crear la carpeta si no existe
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Límite de 16MB
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Base de datos
db = SQL("sqlite:///RecetasDB.db")

# Función para verificar si el archivo es válido
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta para el inicio de sesión
@app.route('/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Registro
        if "signup" in request.form:
            nombre = request.form['signup-username']
            email = request.form['signup-email']
            contraseña = request.form['signup-password']
            confirm_password = request.form['signup-confirm-password']

            # Validar que las contraseñas coincidan
            if contraseña != confirm_password:
                flash('Las contraseñas no coinciden.')
                return redirect(url_for('signin'))

            # Verificar si el email ya está registrado
            existing_user = db.execute("SELECT * FROM Usuario WHERE email = ?", email)
            if existing_user:
                flash('El correo ya está registrado.')
                return redirect(url_for('signin'))

            hashed_password = generate_password_hash(contraseña)
            try:
                db.execute("INSERT INTO Usuario (nombre, email, contraseña) VALUES (?, ?, ?)", nombre, email, hashed_password)
                new_user = db.execute("SELECT * FROM Usuario WHERE email = ?", email)
                session['user_id'] = new_user[0]['id']
                session['username'] = new_user[0]['nombre']
                flash('Registro exitoso. Has iniciado sesión automáticamente.')
                return redirect(url_for('index'))
            except Exception as e:
                flash('Ocurrió un error durante el registro.')
                return redirect(url_for('signin'))

        # Inicio de sesión
        elif "signin" in request.form:
            nombre = request.form['signin-username']
            contraseña = request.form['signin-password']
            user = db.execute("SELECT * FROM Usuario WHERE nombre = ?", nombre)
            if user and check_password_hash(user[0]['contraseña'], contraseña):
                session['user_id'] = user[0]['id']
                session['username'] = user[0]['nombre']
                flash('Inicio de sesión exitoso.')
                return redirect(url_for('index'))
            else:
                flash('Nombre de usuario o contraseña incorrectos.')

    return render_template('signin.html')

# Ruta para cerrar sesión
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.')
    return redirect(url_for('signin'))

# Ruta para el dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    return f"Bienvenido, {session['username']}!"

# Ruta para la página principal
@app.route('/index')
def index():
    return render_template('index.html')

# Ruta para la vista de categorías en grid
@app.route('/categories-grid')
def categories_grid():
    return render_template('categories-grid.html')

# Ruta para la vista de categorías en lista
@app.route('/categories-list')
def categories_list():
    return render_template('categories-list.html')

# Ruta para un solo post
@app.route('/single-post')
def single_post():
    return render_template('single-post.html')

# Ruta para la tipografía
@app.route('/typography')
def typography():
    return render_template('typography.html')

# Ruta para añadir una receta
@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para añadir una receta.')
        return redirect(url_for('signin'))

    if request.method == 'POST':
        nombre = request.form['recipe-name']
        descripcion = request.form['recipe-description']
        tiempo_preparacion = request.form['prep-time']
        dificultad = request.form['difficulty']
        categoria_id = request.form['category']
        comentarios = request.form['additional-notes']

        # Verificar si se sube una imagen
        imagen = request.files['recipe-image']
        if imagen and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagen_ruta = os.path.join('uploads', filename)
        else:
            imagen_ruta = None

        # Insertar en la base de datos
        try:
            db.execute(
                "INSERT INTO Receta (nombre, descripcion, tiempoPreparacion, dificultad, puntuacion, autor_id, categoria_id, comentarios, imagenReceta) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                nombre, descripcion, tiempo_preparacion, dificultad, 0, session['user_id'], categoria_id, comentarios, imagen_ruta
            )
            flash('Receta añadida exitosamente.')
            return redirect(url_for('index'))
        except Exception as e:
            flash('Ocurrió un error al añadir la receta.')
            return redirect(url_for('add_recipe'))

    return render_template('add.html')

# Ruta para la página de inicio de sesión
@app.route('/signin')
def signin_page():
    return render_template('signin.html')

if __name__ == '__main__':
    app.run(debug=True)
