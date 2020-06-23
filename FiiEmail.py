import email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

# TODO:
# - separar os setores de interesse

class FiiEmail:
    def __init__(self, login, passwd, to):
        self.login = login
        self.passwd = passwd
        self.to = to

    def buildErrorTable(self, h, b):
        logger.debug('Build Error Table')
        error = '<table><thead><tr><th>'
        error += '</th><th>'.join(h)
        error += '</tr></thead><tbody>' 
        for row in b:
            error += '<tr><td>'
            error += '</td><td>'.join(str(c) for c in row)
            error += '</td></tr>'
        error += '</tbody></table>'
        return error

    def buildGeneralTable(self, h, b):
        logger.debug('Build General Table')
        error = '<table><thead><tr><th>'
        error += '</th><th>'.join(h)
        error += '</tr></thead><tbody>' 
        for row in b:
            error += '<tr><td>'
            error += '</td><td>'.join(str(c) + '%' if n in [2,3,4] else str(c) 
                for n,c in enumerate(row))
            error += '</td></tr>'
        error += '</tbody></table>'
        return error

    def buildFiiTable(self, h, b):
        logger.debug('Build Fii Table')
        error = '<table><thead><tr><th>'
        error += '</th><th>'.join(h)
        error += '</tr></thead><tbody>' 
        for row in b:
            error += '<tr><td>'
            error += '</td><td>'.join(str(c) for c in row[:4])
            error += '</td><td>'
            error += '%</td><td>'.join(str(c) for c in row[4:7])
            error += '%</td><td>{0}</td>'.format(row[7])
            error += '<td><a href="{0}">Details</td>'.format(row[8])
            error += '<td><p title="{0}">Notas</p></td>'.format(row[9])
        error += '</tbody></table>'
        return error

    def buildMsg(self, report):
        si = [u'galpões', 'shoppings', 'outros']
        html = """<html>
            <head>
                <style>
                    table {{
                        width: 100%;
                    }}
                    td {{
                        max-width: 100px;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        white-space: nowrap;
                    }}
                    th {{
                        text-align: left
                    }}
                </style>
            </head>
            <body>
                <h1>Erros</h1>
                <div>{0}</div>
                <h1>Geral</h1>
                <div>{1}</div>
                <h1>Setores de Interesse</h1>
                <div>{2}</div>
                <h1>Outros Setores</h1>
                <div>{3}</div>
                <h1>Recomendacoes dos Setores de Interesse</h1>
                <div>{4}</div>
                <h1>Recomendacoes Gerais</h1>
                <div>{5}</div>
                <h1>Meus Fii</h1>
                <div>{6}</div>
            </body>
        </html>""".format(
            self.buildErrorTable(report.erroshdr, report.erros), 
            self.buildGeneralTable(report.generalhdr, report.general),
            self.buildGeneralTable(report.generalhdr, [i for i in report.subtipos if i[0] in si]),
            self.buildGeneralTable(report.generalhdr, [i for i in report.subtipos if i[0] not in si]),
            self.buildFiiTable(report.fiihdr, [i for i in report.recomendacoes if i[2] in si]),
            self.buildFiiTable(report.fiihdr, [i for i in report.recomendacoes if i[2] not in si]),
            self.buildFiiTable(report.fiihdr, report.my))
        msg = MIMEText(html, 'html')
        msg['From'] = self.login
        msg['To'] = self.to
        msg['Subject'] = 'Relatorio de Fiis'
        return msg

    def send(self, report):
        logger.info('Sending E-mail')
        msg = self.buildMsg(report)
        s = smtplib.SMTP("smtp.live.com",587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(self.login, self.passwd)
        s.sendmail(self.login, self.to, msg.as_string())
        s.quit()
