from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import send_file
# ---------- Configuración ----------
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Lista de usuarios y reembolsos
usuarios = []
reembolsos = []

# ---------- Función para enviar correo con Excel ----------
def send_email_with_excel(to_email, subject, body, excel_path):
    sender_email = "kiragrisluciano@gmail.com"  # Cambiar por tu correo
    sender_password = "xlfz aufx djzn egqc"      # Cambiar por tu contraseña

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEBase('application', "octet-stream"))

    # Adjuntar Excel
    part = MIMEBase('application', "octet-stream")
    with open(excel_path, 'rb') as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(excel_path)}"')
    msg.attach(part)

    # Enviar correo
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("Correo enviado a", to_email)
    except Exception as e:
        print("Error enviando correo:", e)

# ---------- Rutas ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html', reembolsos=reembolsos)

# ---------- Registrar usuario ----------
@app.route('/register_user', methods=['POST'])
def register_user():
    form = request.form
    file = request.files.get('ine')
    filename = None
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    usuario = {
        'type': 'Comisionista' if 'rfc' in form else 'Agente Comercial',
        'name': form.get('name'),
        'email': form.get('email'),
        'extra': form.get('extra') or form.get('rtt') or '',
        'ine_file': filename
    }
    usuarios.append(usuario)

    # Guardar Excel de usuarios
    df = pd.DataFrame(usuarios)
    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'usuarios.xlsx')
    df.to_excel(excel_path, index=False)

    # Enviar correo
    send_email_with_excel("kiragrisluciano@gmail.com", "Nuevo Usuario Registrado", "Se registró un nuevo usuario.", excel_path)

    return jsonify({'success': True, 'message': 'Usuario registrado y enviado por correo.'})

# ---------- Solicitud de reembolso ----------
@app.route('/submit', methods=['POST'])
def submit_reembolso():
    form = request.form
    file = request.files.get('ine_file')
    filename = None
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    reembolso = {
        'id': len(reembolsos)+1,
        'name': form.get('name'),
        'email': form.get('email'),
        'reason': form.get('reason'),
        'amount': form.get('amount'),
        'ine_file': filename,
        'authorized': False
    }
    reembolsos.append(reembolso)

    # Guardar Excel de reembolsos
    df = pd.DataFrame(reembolsos)
    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reembolsos.xlsx')
    df.to_excel(excel_path, index=False)

    # Enviar correo
    send_email_with_excel("kiragrisluciano@gmail.com", "Nuevo Reembolso Solicitado", "Se solicitó un nuevo reembolso.", excel_path)

    return jsonify({'success': True, 'message': 'Reembolso registrado y enviado por correo.'})

# ---------- Autorizar reembolso ----------
@app.route('/authorize_reembolso/<int:id>', methods=['POST'])
def authorize_reembolso(id):
    data = request.get_json()
    password = data.get('password')

    if password == 'cs2908GE':  # contraseña de ejemplo
        reembolso = next((r for r in reembolsos if r['id']==id), None)
        if reembolso:
            reembolso['authorized'] = True

            # ---------- ENVIAR CORREO AL USUARIO ----------
            sender_email = "kiragrisluciano@gmail.com"
            sender_password = "xlfz aufx djzn egqc"  # Tu contraseña de aplicación

            try:
                # Usando smtplib
                import smtplib
                from email.mime.text import MIMEText

                msg = MIMEText(f"Hola {reembolso['name']}, tu reembolso por ${reembolso['amount']} ha sido autorizado.")
                msg['Subject'] = "Reembolso Autorizado"
                msg['From'] = sender_email
                msg['To'] = reembolso['email']

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, reembolso['email'], msg.as_string())
                server.quit()

                print("Correo de autorización enviado a", reembolso['email'])

            except Exception as e:
                print("Error enviando correo al usuario:", e)

            return jsonify({'success': True, 'message': 'Reembolso autorizado y correo enviado.'})

        return jsonify({'success': False, 'message': 'Reembolso no encontrado.'}), 404
    else:
        return jsonify({'success': False, 'message': 'Contraseña incorrecta.'}), 403
# Descargar Excel de usuarios
@app.route('/download/usuarios')
def download_usuarios():
    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'usuarios.xlsx')
    if os.path.exists(excel_path):
        return send_file(excel_path, as_attachment=True)
    return "Archivo no encontrado", 404

# Descargar Excel de reembolsos
@app.route('/download/reembolsos')
def download_reembolsos():
    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reembolsos.xlsx')
    if os.path.exists(excel_path):
        return send_file(excel_path, as_attachment=True)
    return "Archivo no encontrado", 404



if __name__ == '__main__':
    app.run(debug=True)
