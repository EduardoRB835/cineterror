from flask import Flask, render_template, request, redirect, url_for
import qrcode
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

app = Flask(__name__)

peliculas = {
    'Película 1': {'hora': '18:00', 'disponible': 82, 'imagen': 'images/sustancia.webp'},
    'Película 2': {'hora': '20:00', 'disponible': 82, 'imagen': 'images/opcion2.webp'},
    'Película 3': {'hora': '22:00', 'disponible': 82, 'imagen': 'images/Opcion1.jpg'}
}

# Configuración de correo (modifica con tus datos)
EMAIL = 'rojasbautistae02@gmail.com'
PASSWORD = 'qgfh aexm jmqb uvjr'
DESTINATARIO = 'rojasbautistae02@gmail.com'

def enviar_correo_reserva(nombre, pelicula, boletos, img_str):
    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = DESTINATARIO
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
            server.sendmail(EMAIL, DESTINATARIO, msg.as_string())
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
        boletos = int(request.form['boletos'])

        if peliculas[pelicula]['disponible'] >= boletos:
            peliculas[pelicula]['disponible'] -= boletos

            # Generar código QR
            qr_data = f"Reserva de {nombre} para {pelicula}, {boletos} boletos"
            img = qrcode.make(qr_data)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)  # Mover el puntero al inicio

            # Enviar correo
            enviar_correo_reserva(nombre, pelicula, boletos, img_byte_arr.getvalue())

            # Mostrar el código QR en la página
            return render_template('qr.html', img_str=img_byte_arr.getvalue())  # Cambiado aquí

        else:
            return f"Lo siento, solo quedan {peliculas[pelicula]['disponible']} boletos disponibles."

    return render_template('reserva.html', pelicula=pelicula, disponible=peliculas[pelicula]['disponible'])


if __name__ == '__main__':
    app.run(debug=True)
