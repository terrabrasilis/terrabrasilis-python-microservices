#!/usr/bin/python3
import os, sys
import traceback
from send import SenderMail


pathToConfigFile = os.path.abspath(os.path.dirname(__file__) + '/config_test')

bodyHeader='Use este link para baixar os dados.'
bodyFooter='Att. Equipe do projeto PRODES.'
bodyHtml='<p><a href="http://terrabrasilis.dpi.inpe.br">terrabrasilis</a></p>'

bodyHtml = ''.join(bodyHtml)#.encode('utf-8')
bodyHtml = """\
    <html>
        <head></head>
        <body>
        <p>
        <h3>{0}</h3>
        </p>
        {1}
        <br/>
        <p style="color:#C0C0C0;">{2}</p>
        </body>
    </html>
    """.format(bodyHeader, bodyHtml, bodyFooter)
try:
    subject='[PRODES] - Link para download de dados.'
    mail = SenderMail(pathToConfigFile)
    mail.setEmailTo('andre.carvalho@inpe.br')
    mail.send(subject, bodyHeader, bodyHtml)
except BaseException as error:
    print(str(error))
