import psycopg2
import logging 

logger = logging.getLogger(__name__)

class FiiPostgres:
    def __init__(self, connstr):
        self.conn = psycopg2.connect(connstr)
    
    def insertFii(self, fii):
        logger.info('Inserting Fii {0}'.format(fii.codigo))
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO FII (
                    codigoexec,
                    url,
                    codigo,
                    nome,
                    tipo,
                    subtipo,
                    dtregistrocvm,
                    cotas,
                    cotistas,
                    notas,
                    taxas,
                    dy,
                    ultimorendimento,
                    pl,
                    vpa,
                    cotacao,
                    pvpa
                ) VALUES (%s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s
                ) RETURNING id; """, (
                fii.codigoexec,
                fii.url,
                fii.codigo,
                fii.nome,
                fii.tipo,
                fii.subtipo,
                fii.dtregistrocvm,
                fii.cotas,
                fii.cotistas,
                fii.notas,
                fii.taxas,
                fii.dy,
                fii.ultimorendimento,
                fii.pl,
                fii.vpa,
                fii.cotacao,
                fii.pvpa
            ))
            r = cur.fetchone()[0]
            self.conn.commit()
            return r

    def insertError(self, error):
        logger.info('Inserting Error for {0}'.format(error.codigo))
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO ERRORS (
                    codigoexec,
                    codigo,
                    msg
                ) VALUES (%s, %s, %s);""", (
                error.codigoexec,
                error.codigo,
                error.msg
            ))
            self.conn.commit()

    def insertRendimento(self, fiiid, r):
        logger.info('Inserting Rendimento for id {0}'.format(fiiid))
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO RENDIMENTO (
                    fii,
                    dtpagamento,
                    cotacao,
                    rendimento
                ) VALUES (%s, %s, %s, %s);""", (
                fiiid,
                r.dtpagamento,
                r.cotacao,
                r.rendimento
            ))
            self.conn.commit()
