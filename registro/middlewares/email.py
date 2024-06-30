from dotenv import load_dotenv
import yagmail
import os

load_dotenv()

class Email:
    def __init__(self) -> None:
        self.from_email = os.getenv('FROM_EMAIL')
        self.from_password = os.getenv('FROM_PASSWORD')
        self.to_emails=os.getenv('TO_EMAILS').split(',')
        self.yag = yagmail.SMTP(user=self.from_email, password=self.from_password)
        
    def enviar_texto(self, asunto="ROBOT DEVELOPER", mensaje="Este mensaje es un correo de prueba. Si lo recibió ignórelo por favor."):
        try:
            print("Se esta enviando un correo")
            print("self.from_email")
            print(self.from_email)
            print("self.from_password")
            print(self.from_password)
            self.yag.send(self.to_emails, asunto, mensaje)
            print("Se ha enviado un correo")
        except Exception as e:
            print(e)
            
    def enviar_html(self, asunto="ROBOT DEVELOPER", html="<h2>Este mensaje es un correo de prueba. Si lo recibió ignórelo por favor.</h2>"):
        try:
            self.yag.send(self.to_emails, asunto, html)
        except Exception as e:
            print(e)