from flask import Flask, render_template, request, redirect, url_for, send_file
import qrcode
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import base64

app = Flask(__name__)

peliculas = {
    'La Sutancia': {'hora': '10:00 -12:20', 'disponible': 0, 'imagen': 'images/sustancia.webp'},
    'Hereditary': {'hora': '12:30-14:30', 'disponible': 82, 'imagen': 'images/Hereditary.webp'},
    'La primera profecía': {'hora': '14:45-17:05', 'disponible': 82, 'imagen': 'images/la_primera_profecia.jpg'}
}

# Configuración de correo (modifica con tus datos)
EMAIL = 'terrorcine75@gmail.com'  # Cambia esto a tu correo
PASSWORD = 'tulz cuyr qurc bzxx'  # Cambia esto a tu contraseña

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
        correo = request.form['correo']
        boletos = int(request.form['boletos'])
        
        if peliculas[pelicula]['disponible'] >= boletos:
            peliculas[pelicula]['disponible'] -= boletos
            
            # Calcular el total
            costo_por_boleto = 10
            total = boletos * costo_por_boleto
            
            # Agrega el número de boletos a la información de la película
            peliculas[pelicula]['boletos'] = boletos
            
            # Generar código QR con toda la información necesaria
            qr_data = (f"Reserva de {nombre} para {pelicula}\n"
                       f"Boletos: {boletos}\n"
                       f"Costo total: {total} pesos\n"
                       f"Hora: {peliculas[pelicula]['hora']}\n"
                       f"Lugar: SALA P")
            
            img = qrcode.make(qr_data)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)  # Mover el puntero al inicio
            
            # Convertir a Base64 para mostrar en la página
            img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            
            # Enviar correo con el código QR adjunto
            enviar_correo_reserva(nombre, correo, pelicula, boletos, img_byte_arr.getvalue())
            
            # Mostrar el código QR en la página
            return render_template('qr.html', img_str=img_base64, info=peliculas[pelicula], pelicula=pelicula, total=total)

        else:
            return f"Lo siento, solo quedan {peliculas[pelicula]['disponible']} boletos disponibles."
    
    return render_template('reserva.html', pelicula=pelicula, disponible=peliculas[pelicula]['disponible'])


@app.route('/descargar_qr/<pelicula>')
def descargar_qr(pelicula):
    # Generar el código QR
    qr_data = f"Reserva para {peliculas[pelicula]['disponible']} boletos para {pelicula}"
    img = qrcode.make(qr_data)

    # Guardar el QR como un archivo en memoria
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Devolver el archivo como respuesta de descarga
    return send_file(img_byte_arr, mimetype='image/png', as_attachment=True, download_name=f"qr_{pelicula}.png")


if __name__ == '__main__':
    app.run(debug=True)
