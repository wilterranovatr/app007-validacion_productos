from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# Importando Variables de Entornos
from dotenv import load_dotenv
import os


class EnviarCorreos:

    tipo_ver = []
    path_file = ""

    def __init__(self, tipo_veri, path_attach):
        self.tipo_ver = tipo_veri
        self.path_file = path_attach

    def enviarCorreo(self):
        # Cargamos las variables de entorno
        load_dotenv()

        # Creando Instancia de correo
        msg = MIMEMultipart()

        # Configurando parametros de envio
        password = os.environ.get("PASSWORD")
        msg['From'] = os.environ.get("EMAIL_USER")
        # msg['To'] = os.environ.get("EMAIL_USER")
        msg['To'] = os.environ.get("EMAILS_TO")
        msg['Subject'] = "Reporte de Verificación de Productos"
        msg['CC'] = os.environ.get("EMAILS_CC")

        # Agregando contenido de mensaje
        # msg.attach(MIMEText(message, 'plain'))
        msg_contenido = ""
        #####
        if "BARCODE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos sin código de barra</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "UNIT" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con error asignación de unidades de medida</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "SUNAT" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con observaciones en código SUNAT</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "PROVIDER" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos sin proveedores asignados</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "CATALOGO" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos sin categorías asignados</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "TRANSLATION" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos con campo de traducciones incompletas</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''
        if "STATUS_ACTIVE" in self.tipo_ver:
            msg_contenido = msg_contenido+'''<div style="margin-left: 14px;">
            <h3>Productos vendidos con estado INACTIVO</h3>
            <p>Se encontraron productos afectados los cuales se muestran en el archivo adjunto.
            </p>
        </div>'''

        #####
        msg.attach(MIMEText('''
                                 <!DOCTYPE html>
<html>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;font-size: 14px;">
    <div style="padding:20px 0px;width: 100%; height: 100%;">
        <img src="https://trujillodatalake.blob.core.windows.net/public/img/logo.png" style="height: 100px;">
        <div style="background-color:#F44336;padding-top: 1px;padding-bottom: 1px;margin-top: 10px; margin-bottom: 20px;">
            <h2 style="color:white; font-size: 15px; margin-left: 14px;">Reporte de Verificación de Productos</h2>
        </div>
        '''+msg_contenido+'''
    </div>
    <div style="margin-left: 14px; margin-top: 5px; font-size: 14px;">
            <span>El presente correo electrónico fue generado por un proceso automático, para más información o inconveniente por favor comuniquese con el área de Tecnología.
                <br><br>Saludos.
            </span>
        </div>
</body>
</html>''', 'html'))
        #####
        self.attach_file_to_email(msg, self.path_file)
        #####
        try:
            # Creando servidor
            server = smtplib.SMTP('smtp.outlook.com: 587')
            server.starttls()

            # Direccion de envio "DE"
            server.login(msg['From'], password)
            # Agregando CC
            emails = f"{msg['To']}, {msg['CC']}".split(",")
            # emails = f"{msg['To']}".split(",")

            # Direccion de envio "PARA"
            server.sendmail(msg['From'], emails, msg.as_string())
            server.quit()
        except Exception as e:
            print(e)
        else:
            print("Correo enviado correctamente a", (msg['To']))

    def attach_file_to_email(self, email_message, filename):
        # Abriendo archivo
        with open(filename, "rb") as f:
            file_attachment = MIMEApplication(f.read())
        # Agregamos archivo en cabecera
        file_name = filename.split("/")[-1]
        file_attachment.add_header(
            "Content-Disposition",
            f"attachment; filename= {file_name}",
        )
        # Agregamos el archivo en el mensaje
        email_message.attach(file_attachment)
