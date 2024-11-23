import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from cs50 import SQL

# Configuración de la app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuración de la base de datos
db = SQL("sqlite:///RecetasDB.db")

# Ruta para el inicio de sesión y registro
@app.route('/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Registro
        if "signup" in request.form:
            nombre = request.form['signup-username']
            email = request.form['signup-email']
            contraseña = request.form['signup-password']
            confirm_password = request.form['signup-confirm-password']
            aceptar_terminos = request.form.get('terms')

            # Validar que se acepten los términos y condiciones
            if not aceptar_terminos:
                flash('You must agree to the terms and conditions to register.')
                return redirect(url_for('signin'))

            # Validar que las contraseñas coincidan
            if contraseña != confirm_password:
                flash('Passwords do not match.')
                return redirect(url_for('signin'))

            # Verificar si el email ya está registrado
            existing_user = db.execute("SELECT * FROM Usuario WHERE email = ?", email)
            if existing_user:
                flash('Email is already registered.')
                return redirect(url_for('signin'))

            # Crear el nuevo usuario
            hashed_password = generate_password_hash(contraseña)
            try:
                db.execute("INSERT INTO Usuario (nombre, email, contraseña) VALUES (?, ?, ?)", nombre, email, hashed_password)
                new_user = db.execute("SELECT * FROM Usuario WHERE email = ?", email)
                session['user_id'] = new_user[0]['id']
                session['username'] = new_user[0]['nombre']
                flash('Registration successful. You are now logged in.')
                return redirect(url_for('index'))
            except Exception as e:
                flash('An error occurred during registration.')
                return redirect(url_for('signin'))

        # Inicio de sesión
        elif "signin" in request.form:
            nombre = request.form['signin-username']
            contraseña = request.form['signin-password']
            user = db.execute("SELECT * FROM Usuario WHERE nombre = ?", nombre)
            if user and check_password_hash(user[0]['contraseña'], contraseña):
                session['user_id'] = user[0]['id']
                session['username'] = user[0]['nombre']
                flash('Logged in successfully.')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.')

    return render_template('signin.html')

# Ruta para cerrar sesión
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Logged out successfully.')
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
        flash('Please log in to add a recipe.')
        return redirect(url_for('signin'))

    if request.method == 'POST':
        nombre = request.form['recipe-name']
        descripcion = request.form['recipe-description']
        tiempo_preparacion = request.form['prep-time']
        dificultad = request.form['difficulty']
        categoria_id = request.form['category']
        comentarios = request.form['additional-notes']

        db.execute(
            "INSERT INTO Receta (nombre, descripcion, tiempoPreparacion, dificultad, autor_id, categoria_id, comentarios) VALUES (?, ?, ?, ?, ?, ?, ?)",
            nombre, descripcion, tiempo_preparacion, dificultad, session['user_id'], categoria_id, comentarios
        )
        flash('Recipe added successfully!')
        return redirect(url_for('index'))

    # Consulta las categorías desde la base de datos
    categories = db.execute("SELECT * FROM Categoria")
    return render_template('add.html', categories=categories)

# Ruta para visualizar recetas por categoría
@app.route('/category/<int:category_id>')
def category_view(category_id):
    # Obtener la categoría
    category = db.execute("SELECT * FROM Categoria WHERE id = ?", category_id)
    if not category:
        flash('Category not found.', 'danger')
        return redirect(url_for('index'))

    # Obtener las recetas de esa categoría
    recipes = db.execute("SELECT * FROM Receta WHERE categoria_id = ?", category_id)
    category_name = category[0]['nombre']

    return render_template('category_view.html', recipes=recipes, category_name=category_name)

# Ruta para buscar recetas o categorías
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    if not query:
        flash('Please enter a search term.', 'warning')
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
        flash('Please log in to edit your profile.')
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
        flash('Profile updated successfully!')
        return redirect(url_for('index'))

    user = db.execute("SELECT * FROM Usuario WHERE id = ?", session['user_id'])[0]
    return render_template('edit-profile.html', user=user)

# Ruta para visualizar el perfil del usuario
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to view your profile.')
        return redirect(url_for('signin'))
    
    user = db.execute("SELECT * FROM Usuario WHERE id = ?", session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('index'))
    
    user = user[0]  # Extraer el usuario de la lista
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
