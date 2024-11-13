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
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limite de 16MB
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Conectar a la base de datos
db = SQL("sqlite:///RecetasDB.db")

# Función para verificar si el archivo es válido
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Registro
        if 'signup' in request.form:
            print("Procesando registro...")  # Depuración: verificar si entra en el bloque de registro
            nombre = request.form['signup-username']
            email = request.form['signup-email']
            contraseña = request.form['signup-password']
            confirm_password = request.form['signup-confirm-password']

            # Validar que las contraseñas coincidan
            if contraseña != confirm_password:
                flash('Las contraseñas no coinciden.')
                print("Las contraseñas no coinciden.")  # Depuración
                return redirect(url_for('signin'))

            # Verificar si el email ya está registrado
            existing_user = db.execute("SELECT * FROM Usuario WHERE email = ?", email)  # Cambiar a 'Usuario'
            if existing_user:
                flash('El correo ya está registrado.')
                print("Correo ya registrado.")  # Depuración
                return redirect(url_for('signin'))

            hashed_password = generate_password_hash(contraseña)
            
            # Manejo de imagen de perfil y portada
            fotoPerfil = request.files['fotoPerfil']
            fotoPortada = request.files['fotoPortada']
            if fotoPerfil and allowed_file(fotoPerfil.filename):
                filename_perfil = secure_filename(fotoPerfil.filename)
                fotoPerfil.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_perfil))
            else:
                filename_perfil = None  # Puedes asignar un valor predeterminado aquí

            if fotoPortada and allowed_file(fotoPortada.filename):
                filename_portada = secure_filename(fotoPortada.filename)
                fotoPortada.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_portada))
            else:
                filename_portada = None

            print("Guardando usuario en la base de datos...")  # Depuración

            # Guardar el usuario en la base de datos
            try:
                db.execute("INSERT INTO Usuario (nombre, email, contraseña, fotoPerfil, fotoPortada) VALUES (?, ?, ?, ?, ?)", 
                           nombre, email, hashed_password, filename_perfil, filename_portada)

                print("Usuario guardado.")  # Depuración
                
                # Obtener el ID del usuario recién creado para iniciar sesión automáticamente
                new_user = db.execute("SELECT * FROM Usuario WHERE email = ?", email)  # Cambiar a 'Usuario'
                session['user_id'] = new_user[0]['id']
                session['username'] = new_user[0]['nombre']
                flash('Registro exitoso. Has iniciado sesión automáticamente.')
                return redirect(url_for('index'))  # Redirige al índice después del registro

            except Exception as e:
                # Si ocurre un error, mostrar el mensaje
                print(f"Error al registrar el usuario: {e}")  # Depuración para capturar cualquier error
                flash('Ocurrió un error durante el registro. Inténtalo nuevamente.')
                return redirect(url_for('signin'))

        # Inicio de sesión
        elif 'signin' in request.form:
            print("Procesando inicio de sesión...")  # Depuración
            nombre = request.form['signin-username']
            contraseña = request.form['signin-password']

            # Consultar el usuario en la base de datos
            user = db.execute("SELECT * FROM Usuario WHERE nombre = ?", nombre)  # Cambiar a 'Usuario'
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

@app.route('/')
def index():
    return render_template('index.html')  # Asegúrate de que tengas este archivo en la carpeta 'templates'

if __name__ == '__main__':
    app.run(debug=True)