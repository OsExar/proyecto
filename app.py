from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from cs50 import SQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Conectar a la base de datos usando CS50
db = SQL("sqlite:///RecetasDB.db")

@app.route('/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Registro
        if 'signup' in request.form:
            nombre = request.form['signup-username']
            email = request.form['signup-email']
            contraseña = request.form['signup-password']
            hashed_password = generate_password_hash(contraseña)

            # Guardar el usuario en la base de datos usando CS50
            db.execute("INSERT INTO usuario (nombre, email, contraseña) VALUES (?, ?, ?)", nombre, email, hashed_password)

            flash('Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect(url_for('signin'))

        # Inicio de sesión
        elif 'signin' in request.form:
            nombre = request.form['signin-username']
            contraseña = request.form['signin-password']

            # Consultar el usuario en la base de datos usando CS50
            user = db.execute("SELECT * FROM usuario WHERE nombre = ?", nombre)

            if user and check_password_hash(user[0]['contraseña'], contraseña):
                session['user_id'] = user[0]['id']
                session['username'] = user[0]['nombre']
                flash('Inicio de sesión exitoso.')
                return redirect(url_for('dashboard'))
            else:
                flash('Nombre de usuario o contraseña incorrectos.')

    return render_template('signin.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    return f"Bienvenido, {session['username']}!"


@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.')
    return redirect(url_for('signin'))

@app.route('/index')
def index():
    return render_template('index.html')  # Asumiendo que tienes un archivo index.html en la carpeta templates

if __name__ == '__main__':
    app.run(debug=True)
