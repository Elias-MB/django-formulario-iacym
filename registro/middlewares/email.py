from django.core.files.base import ContentFile
import base64
from dotenv import load_dotenv
import yagmail
import os
from django.conf import settings

load_dotenv()

class Email:
    def __init__(self) -> None:
        self.from_email = os.getenv('FROM_EMAIL')
        self.from_password = os.getenv('FROM_PASSWORD')
        self.to_emails=os.getenv('TO_EMAILS').split(',')
        self.yag = yagmail.SMTP(user=self.from_email, password=self.from_password)
        
    def enviar_texto(self, asunto="ROBOT DEVELOPER", mensaje="Este mensaje es un correo de prueba. Si lo recibió ignórelo por favor."):
        try:
            self.yag.send(self.to_emails, asunto, mensaje)
            print("Se ha enviado un correo")
        except Exception as e:
            print(e)
        finally:
            self.cerrar_conexion()
            
    def enviar_html(self, datos, asunto="ROBOT DEVELOPER", html="<h2>Este mensaje es un correo de prueba. Si lo recibió ignórelo por favor.</h2>", archivo_adjunto=None):
        try:
            if archivo_adjunto:                
                format, imgstr = archivo_adjunto.split(';base64,')
                extension = format.split('/')[-1]
                nombre_archivo_completo = f"voucher_tmp.{extension}"
                datos_archivo = ContentFile(base64.b64decode(imgstr), name=nombre_archivo_completo)
                RUTA_CARPETA_TEMP = os.path.join(settings.BASE_DIR, 'tmp')
                if not os.path.exists(RUTA_CARPETA_TEMP):
                    os.makedirs(RUTA_CARPETA_TEMP)

                ruta_archivo_temporal = os.path.join(RUTA_CARPETA_TEMP, nombre_archivo_completo)
                with open(ruta_archivo_temporal, 'wb') as f:
                    f.write(datos_archivo.read())
                # self.to_emails.append(datos["email"])
                self.yag.send(self.to_emails, asunto, html, attachments=ruta_archivo_temporal)
                print("Correo con adjunto enviado correctamente.")

                os.remove(ruta_archivo_temporal)
            else:
                self.yag.send(self.to_emails, asunto, html)
                print("Correo enviado correctamente (sin adjunto).")
        except Exception as e:
            print(e)
        finally:
            self.cerrar_conexion()
            
    def cerrar_conexion(self):
        try:
            if self.yag:
                self.yag.close()
                print("Conexión SMTP cerrada correctamente.")
        except Exception as e:
            print(f"Error al cerrar la conexión SMTP: {e}")