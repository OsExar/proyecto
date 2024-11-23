import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from cs50 import SQL

# Crear la instancia de la aplicación Flask
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

# Configuración de la base de datos
db = SQL("sqlite:///RecetasDB.db")

# Función para verificar si el archivo es válido
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta para el inicio de sesión y registro
@app.route('/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Registro
        if "signup" in request.form:
            nombre = request.form.get('signup-username')
            email = request.form.get('signup-email')
            contraseña = request.form.get('signup-password')
            confirm_password = request.form.get('signup-confirm-password')
            aceptar_terminos = request.form.get('terms')

            # Validar que se acepten los términos y condiciones
            if not aceptar_terminos:
                flash('Debes aceptar los términos y condiciones para registrarte.')
                return redirect(url_for('signin'))

            # Validar que las contraseñas coincidan
            if contraseña != confirm_password:
                flash('Las contraseñas no coinciden.')
                return redirect(url_for('signin'))

            # Verificar si el email ya está registrado
            existing_user = db.execute("SELECT * FROM Usuario WHERE email = ?", email)
            if existing_user:
                flash('El email ya está registrado.')
                return redirect(url_for('signin'))

            # Crear el nuevo usuario
            hashed_password = generate_password_hash(contraseña)
            try:
                db.execute("INSERT INTO Usuario (nombre, email, contraseña) VALUES (?, ?, ?)", nombre, email, hashed_password)
                new_user = db.execute("SELECT * FROM Usuario WHERE email = ?", email)
                session['user_id'] = new_user[0]['id']
                session['username'] = new_user[0]['nombre']
                flash('Registro exitoso. Has iniciado sesión.')
                return redirect(url_for('index'))
            except Exception as e:
                flash('Ocurrió un error durante el registro.')
                return redirect(url_for('signin'))

        # Inicio de sesión
        elif "signin" in request.form:
            nombre = request.form.get('signin-username')
            contraseña = request.form.get('signin-password')
            user = db.execute("SELECT * FROM Usuario WHERE nombre = ?", nombre)
            if user and check_password_hash(user[0]['contraseña'], contraseña):
                session['user_id'] = user[0]['id']
                session['username'] = user[0]['nombre']
                flash('Has iniciado sesión correctamente.')
                return redirect(url_for('index'))
            else:
                flash('Usuario o contraseña incorrectos.')

    return render_template('signin.html')

# Ruta para cerrar sesión
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.')
    return redirect(url_for('signin'))

# Ruta para el dashboard
@app.route('/index')
def index():
    categories = db.execute("SELECT * FROM Categoria")
    return render_template('index.html', categories=categories)

# Ruta para el grid de categorías
@app.route('/categories-grid')
def categories_grid():
    categories = db.execute("SELECT * FROM Categoria")
    return render_template('categories-grid.html', categories=categories)

# Ruta para añadir recetas
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión para añadir una receta.')
        return redirect(url_for('signin'))

    if request.method == 'POST':
        nombre = request.form.get('recipe-name')
        if not nombre:
            flash('El nombre de la receta es obligatorio.')
            return redirect(url_for('add'))
        descripcion = request.form.get('recipe-description')
        if not descripcion:
            flash('La descripción de la receta es obligatoria.')
            return redirect(url_for('add'))
        tiempo_preparacion = request.form.get('prep-time')
        dificultad = request.form.get('difficulty')
        categoria_id = request.form.get('category')
        comentarios = request.form.get('additional-notes')
        imagen = request.files.get('recipe-image')

        # Verificar si se sube una imagen válida
        if imagen and allowed_file(imagen.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], imagen.filename)
            imagen.save(filename)
            imagen_ruta = os.path.join('uploads', imagen.filename)
        else:
            imagen_ruta = None

        db.execute(
            "INSERT INTO Receta (nombre, descripcion, tiempoPreparacion, dificultad, autor_id, categoria_id, comentarios, imagenReceta) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            nombre, descripcion, tiempo_preparacion, dificultad, session['user_id'], categoria_id, comentarios, imagen_ruta
        )
        flash('Receta añadida correctamente!')
        return redirect(url_for('index'))

    categories = db.execute("SELECT * FROM Categoria")
    return render_template('add.html', categories=categories)

# Ruta para añadir categorías
@app.route('/add-category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        nombre = request.form.get('name')
        if not nombre:
            flash('El nombre de la categoría es obligatorio.')
            return redirect(url_for('add_category'))

        try:
            db.execute("INSERT INTO Categoria (nombre) VALUES (?)", nombre)
            flash('Categoría añadida correctamente.')
        except Exception as e:
            flash('Ocurrió un error al añadir la categoría.')
        return redirect(url_for('categories_grid'))

    return render_template('add-category.html')

# Ruta para visualizar una receta específica
@app.route('/single-post/<int:recipe_id>')
def single_post(recipe_id):
    recipe = db.execute("SELECT * FROM Receta WHERE id = ?", recipe_id)
    if not recipe:
        flash('Receta no encontrada.', 'danger')
        return redirect(url_for('index'))
    return render_template('single-post.html', recipe=recipe[0])

# Ruta para mostrar categorías en lista
@app.route('/categories-list')
def categories_list():
    categories = db.execute("SELECT * FROM Categoria")
    return render_template('categories-list.html', categories=categories)

# Ruta para visualizar recetas por categoría
@app.route('/category/<int:category_id>')
def category_view(category_id):
    category = db.execute("SELECT * FROM Categoria WHERE id = ?", category_id)
    if not category:
        flash('Categoría no encontrada.', 'danger')
        return redirect(url_for('index'))

    recipes = db.execute("SELECT * FROM Receta WHERE categoria_id = ?", category_id)
    category_name = category[0]['nombre']

    return render_template('category_view.html', recipes=recipes, category_name=category_name)

# Ruta para buscar recetas o categorías
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    if not query:
        flash('Por favor, ingresa un término de búsqueda.', 'warning')
        return redirect(url_for('index'))

    recipes = db.execute(
        "SELECT * FROM Receta WHERE nombre LIKE ? OR descripcion LIKE ?",
        f'%{query}%', f'%{query}%'
    )
    categories = db.execute(
        "SELECT * FROM Categoria WHERE nombre LIKE ?",
        f'%{query}%'
    )

    return render_template('search_results.html', recipes=recipes, categories=categories)

# Ruta para editar el perfil del usuario
@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión para editar tu perfil.')
        return redirect(url_for('signin'))

    if request.method == 'POST':
        nombre = request.form.get('name')
        email = request.form.get('email')
        biografia = request.form.get('biografia')
        mostrar_ingredientes = request.form.get('mostrar_ingredientes') == 'on'

        db.execute(
            "UPDATE Usuario SET nombre = ?, email = ?, biografia = ?, mostrarIngredientes = ? WHERE id = ?",
            nombre, email, biografia, mostrar_ingredientes, session['user_id']
        )
        session['username'] = nombre
        flash('Perfil actualizado correctamente!')
        return redirect(url_for('index'))

    user = db.execute("SELECT * FROM Usuario WHERE id = ?", session['user_id'])[0]
    return render_template('edit-profile.html', user=user)

# Ruta para visualizar el perfil del usuario
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión para ver tu perfil.')
        return redirect(url_for('signin'))
    
    user = db.execute("SELECT * FROM Usuario WHERE id = ?", session['user_id'])
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('index'))
    
    user = user[0]  # Extraer el usuario de la lista
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)