from flask import Flask, render_template, request, redirect, url_for
import qrcode
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import base64

app = Flask(__name__)

peliculas = {
    'Película 1': {'hora': '18:00', 'disponible': 82, 'imagen': 'images/sustancia.webp'},
    'Película 2': {'hora': '20:00', 'disponible': 82, 'imagen': 'images/opcion2.webp'},
    'Película 3': {'hora': '22:00', 'disponible': 82, 'imagen': 'images/Opcion1.jpg'}
}

# Configuración de correo (modifica con tus datos)
EMAIL = 'rojasbautistae02@gmail.com'  # Cambia esto a tu correo
PASSWORD = 'qgfh aexm jmqb uvjr'  # Cambia esto a tu contraseña

def enviar_correo_reserva(nombre, correo, pelicula, boletos, img_str):
    msg = MIMEMultipart()
    msg['From'] = EMAIL  # Remitente sigue siendo tu correo para autenticación
    msg['To'] = correo  # Usar el correo del usuario
    msg['Subject'] = f'Nueva reserva de {nombre} para {pelicula}'

    # Texto del correo
    body = f"{nombre} ha reservado {boletos} boletos para {pelicula}."
    msg.attach(MIMEText(body, 'plain'))

    # Adjuntar imagen del QR al correo
    img = MIMEImage(img_str)
    img.add_header('Content-Disposition', 'attachment', filename="qr_code.png")
    msg.attach(img)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, correo, msg.as_string())  # Enviar al correo del usuario
            print('Correo enviado con éxito.')
    except Exception as e:
        print(f'Error al enviar el correo: {e}')


@app.route('/')
def index():
    return render_template('index.html', peliculas=peliculas)


@app.route('/reservar/<pelicula>', methods=['GET', 'POST'])
def reservar(pelicula):
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']  # Capturar el correo ingresado por el usuario
        boletos = int(request.form['boletos'])

        if peliculas[pelicula]['disponible'] >= boletos:
            peliculas[pelicula]['disponible'] -= boletos

            # Generar código QR
            qr_data = f"Reserva de {nombre} para {pelicula}, {boletos} boletos"
            img = qrcode.make(qr_data)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)  # Mover el puntero al inicio

            # Convertir a Base64
            img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

            # Enviar correo
            enviar_correo_reserva(nombre, correo, pelicula, boletos, img_byte_arr.getvalue())

            # Mostrar el código QR en la página
            return render_template('qr.html', img_str=img_base64)

        else:
            return f"Lo siento, solo quedan {peliculas[pelicula]['disponible']} boletos disponibles."

    return render_template('reserva.html', pelicula=pelicula, disponible=peliculas[pelicula]['disponible'])


if __name__ == '__main__':
    app.run(debug=True)
