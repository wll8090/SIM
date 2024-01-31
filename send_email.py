import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys


server='smtp.gmail.com'
port=587

email='sistemas@ufnt.edu.br'
key_app="dvpp rdwy wkfg keqr"
encode='utf-8'

roda_pe=f"{sys.argv.get('path_templates')}{sys.argv.get('roda_pe')}"
roda_pe=open(roda_pe, encoding = encode).read()

class enviar_email:
    def __init__(self, texto):
        self.texto=texto
        self.html='''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="{encode}"></head>
<body>
    <div>
    {texto}
    </div>
<br> <br> <br>
{roda_pe}

</body>
</html>
'''

    def connect(self):
        self.servidor=smtplib.SMTP(server, port)
        self.servidor.starttls()
        self.servidor.login(email, key_app)
        return self.servidor
    
    def format_texto(self, data):
        self.texto=self.texto.format(**data)
        
    def disparo(self, destino, assunto):
        destino='wllyvn@gmail.com'    ###  <<< ----  para teste
        self.msg=MIMEMultipart()
        self.msg['From']=email
        self.msg['To']=destino
        self.msg['Subject']=assunto

        self.texto=self.html.format(texto=self.texto, roda_pe=roda_pe, encode=encode)

        self.msg.attach(MIMEText(self.texto,'html', _charset=encode))
        self.servidor.sendmail(email, destino, self.msg.as_string())     ### <<<< ----   sem envio de emal  

    def desconect(self):
        self.servidor.quit()
