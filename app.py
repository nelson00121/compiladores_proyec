from flask import Flask, render_template, request, session
import pyodbc
import random

app = Flask(__name__)
app.secret_key = '4040kdaklsdlfkasl44o4494949'

# Configuración de la base de datos SQL Server
server = 'DESKTOP-3PG54HH'  # Nombre del servidor
database = 'AHORCADO'       # Nombre de la base de datos
username = 'sa'               # Nombre de usuario
password = '3330'           # Contraseña
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def cargar_palabra():
    # Conectar a la base de datos y obtener una palabra aleatoria
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT texto FROM palabras")
    palabras = [row[0] for row in cursor.fetchall()]
    conn.close()
    return random.choice(palabras).upper()

def inicializar_juego():
    session['palabra'] = cargar_palabra()
    session['letras_correctas'] = []
    session['letras_incorrectas'] = []
    session['intentos_restantes'] = 6

def mostrar_palabra():
    palabra = session['palabra']
    letras_adivinadas = session['letras_correctas']
    return "".join([letra if letra in letras_adivinadas else '_' for letra in palabra])

def generar_dibujo_ahorcado(intentos):
    estados = [
        '''
           -----
           |   |
               |
               |
               |
               |
        =========''',
        '''
           -----
           |   |
           O   |
               |
               |
               |
        =========''',
        '''
           -----
           |   |
           O   |
           |   |
               |
               |
        =========''',
        '''
           -----
           |   |
           O   |
          /|   |
               |
               |
        =========''',
        '''
           -----
           |   |
           O   |
          /|\\  |
               |
               |
        =========''',
        '''
           -----
           |   |
           O   |
          /|\\  |
          /    |
               |
        =========''',
        '''
           -----
           |   |
           O   |
          /|\\  |
          / \\  |
               |
        ========='''
    ]
    return estados[6 - intentos]

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'palabra' not in session:
        inicializar_juego()

    mensaje = ''
    if request.method == 'POST':
        letra = request.form['letra'].upper()
        if letra in session['palabra']:
            if letra not in session['letras_correctas']:
                session['letras_correctas'].append(letra)
                mensaje = f'¡Correcto! La letra {letra} está en la palabra.'
            else:
                mensaje = f'Ya has adivinado la letra {letra}.'
        else:
            if letra not in session['letras_incorrectas']:
                session['letras_incorrectas'].append(letra)
                session['intentos_restantes'] -= 1
                mensaje = f'Lo siento, la letra {letra} no está en la palabra.'
            else:
                mensaje = f'Ya has intentado con la letra {letra}.'

    palabra_mostrada = mostrar_palabra()
    if '_' not in palabra_mostrada:
        mensaje = '¡Felicidades! Has ganado.'
        inicializar_juego()
    elif session['intentos_restantes'] <= 0:
        mensaje = f'Has perdido. La palabra era {session["palabra"]}.'
        inicializar_juego()

    dibujo_ahorcado = generar_dibujo_ahorcado(session['intentos_restantes'])

    return render_template('index.html', palabra_mostrada=palabra_mostrada,
                           intentos_restantes=session['intentos_restantes'],
                           letras_adivinadas=', '.join(session['letras_correctas'] + session['letras_incorrectas']),
                           mensaje=mensaje, dibujo_ahorcado=dibujo_ahorcado)

if __name__ == '__main__':
    app.run(debug=True)
