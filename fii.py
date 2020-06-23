from optparse import OptionParser
from FiiCrowler import FiiCrowler
from FiiDb import FiiPostgres
from Types import Fii, Rendimento, Error, Report
from FiiEmail import FiiEmail
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def getOnline(db):
    fc = FiiCrowler()
    ec = datetime.now().isoformat()
    for fii in iter(fc.getDetail(code, url) for code, url in fc.getAll()):
        if 'error' in fii: 
            error = Error()
            error.codigoexec = ec
            error.codigo = fii['code']
            error.msg = fii['error']
            db.insertError(error)
        else:
            i = Fii()
            i.codigoexec = ec
            i.codigo = fii['code']
            i.url = fii['url']
            i.nome = fii['name']
            i.tipo = fii['tipo']
            i.subtipo = fii['subtipo']
            i.dtregistrocvm = fii['dtregistercvm'].strftime('%Y-%m-%d')
            i.cotas = fii['cotas']
            i.cotistas = fii['cotistas']
            i.notas = fii['notas']
            i.taxas = fii['taxas']
            i.dy = fii['dy']
            i.ultimorendimento = fii['lastrevenue']
            i.pl = fii['pl']
            i.vpa = fii['vpa']
            i.cotacao = fii['quotation']
            i.pvpa = fii['p/vpa']
            fiiid = db.insertFii(i)
            for rendimento in fii['revenues']:
                r = Rendimento()
                r.dtpagamento = rendimento['dt'].strftime('%Y-%m-%d') 
                r.cotacao = rendimento['quotation']
                r.rendimento = rendimento['revenue']
                db.insertRendimento(fiiid, r)

def makeReport(db):
    logger.info('Making The Report')
    r = Report()
    r.erros = db.getErrors()
    r.subtipos = db.getSubtipos()
    r.recomendacoes = db.getRecomendacoes()
    r.my = db.getMyFiis()
    r.general = db.getGeneral()
    return r

def buildOptParser():
    parser = OptionParser('usage: %prog [options]')
    parser.add_option('--log', dest='loglevel', default='ERROR', 
        help='set log level')
    parser.add_option('--online', action='store_true', 
        dest='online', default=False, 
        help='update fiis with online info')
    parser.add_option('--db', dest='dbconn', 
        default='host=localhost dbname=fii user=postgres password=postgres', 
        help='database connection info')
    parser.add_option('--email', dest='email', default=None, 
        help='destination email to send statistics')
    return parser

if __name__ == '__main__':
    try:
        # Command line arguments
        parser = buildOptParser()
        (opt, args) = parser.parse_args()
        # logging
        FORMAT = '%(asctime)s %(levelname)s %(module)s %(message)s'
        logging.basicConfig(level=getattr(logging, opt.loglevel.upper()), 
            format=FORMAT)
        # Database 
        db = FiiPostgres(opt.dbconn)
        # Crowler from internet
        if opt.online: getOnline(db)
        # Report
        report = makeReport(db)
        # Show
        if opt.email:
            fe = FiiEmail('lucio.m.prado@hotmail.com', 'Suntech03;', opt.email)
            fe.send(report)
        else:
            print(report)
    except Exception as error:
        print('Error: {0}'.format(str(error)))

