import json
from datetime import datetime
from optparse import OptionParser
from statistics import mean
from FiiCrowler import FiiCrowler

class PostgresSaver:
    def __init__(self, host, db, user, passwd):
        self.conn = psycopg2.connect(host=host, database=db, 
            user=user, password=passwd)
    
    def insert(self, fii):

    def getLatest(self):

def getOnline(fs):
    fc = FiiCrowler()
    fiis = {fii: fc.getDetail(fii) for fii in fc.getAll()}
    fs.addFiis(fiis)
    return fiis

def buildOptParser():
    parser = OptionParser('usage: %prog [options] arg')
    parser.add_option('--online', action='store_true', 
        dest='online', default=False, help='get fii list from internet')
    parser.add_option('--file', dest='filename', 
        default=None, help='fii file')
    parser.add_option('--db', dest='dbconn', 
        default='host=localhost dbname=fii user=postgresql password=postgres', help='postgres fii connection')
    return parser

def counter(fiis, att):
    l = list(v[att] for k,v in fiis.items() if att in v)
    return sorted(((x,l.count(x)) for x in set(l)), reverse=True, key=lambda i: i[1])

def meanOfGroup(fiis, group, att):
    l = set(v[group] for k,v in fiis.items() if group in v)
    return [(groupv, mean(list(v[att] for k,v in fiis.items() if group in v and v[group] == groupv and att in v))) for
    groupv in l]

if __name__ == '__main__':
    parser = buildOptParser()
    (opt, args) = parser.parse_args()

    fs = FileSaver(opt.filename)
    fiis = getOnline(fs) if opt.online else fs.getLatest()
    print('Total FIIs: {0}'.format(len(fiis)))
    print('Erros FIIs: {0}'.format(sum(1 for k,v in fiis.items() if 'error' in v)))
    print('Total por Tipo:\r\n{0}'.format('\r\n'.join('\t{0}:\t\t{1}'.format(k,v) for k,v in counter(fiis, 'tipo'))))
    print('Total por Subtipo:\r\n{0}'.format('\r\n'.join('\t{0}:\t\t{1}'.format(k,v) for k,v in counter(fiis,
    'subtipo'))))
    print('Media P/VPA por tipo: {0}'.format(meanOfGroup(fiis, 'tipo', 'dy')))

