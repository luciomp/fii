import email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

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

    def buildSectorTable(self, h, b):
        logger.debug('Build Sector Table')
        error = '<table><thead><tr><th>'
        error += '</th><th>'.join(h)
        error += '</tr></thead><tbody>' 
        for row in b:
            error += '<tr><td>'
            error += '</td><td>'.join(str(c) + '%' if n in [2,3] else str(c) 
                for n,c in enumerate(row))
            error += '</td></tr>'
        error += '</tbody></table>'
        return error

    def buildRecomendationTable(self, h, b):
        logger.debug('Build Recomendation Table')
        error = '<table><thead><tr><th>'
        error += '</th><th>'.join(h)
        error += '</tr></thead><tbody>' 
        for row in b:
            error += '<tr><td>'
            error += '</td><td>'.join(c for c in row[:3])
            error += '</td><td>'
            error += '%</td><td>'.join(str(c) for c in row[3:5])
            error += '%</td><td>{0}</td>'.format(row[5])
            error += '<td><a href="{0}">Details</td>'.format(row[6])
            error += '<td><p title="{0}">Notas</p></td>'.format(row[7])
        error += '</tbody></table>'
        return error

    def buildMsg(self, report):
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
                </style>
            </head>
            <body>
                <h1>Erros</h1>
                <div>{0}</div>
                <h1>Setores</h1>
                <div>{1}</div>
                <h1>Recomendacoes</h1>
                <div>{2}</div>
            </body>
        </html>""".format(
            self.buildErrorTable(report.erroshdr, report.erros), 
            self.buildSectorTable(report.subtiposhdr, report.subtipos),
            self.buildRecomendationTable(report.recomendacoeshdr, 
                report.recomendacoes))
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
