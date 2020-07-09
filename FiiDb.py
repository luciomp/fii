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

    def getErrors(self):
        logger.info('Getting Errors')
        with self.conn.cursor() as cur:
            cur.execute("""
                select msg, count(codigo), string_agg(codigo, ' ') 
                from 
                    errors 
                where 
                    codigoexec = (select max(codigoexec) from fii) 
                group by 
                    msg 
                order by 
                    msg;""")
            return cur.fetchall()

    def getTipos(self):
        logger.info('getting Types')
        with self.conn.cursor() as cur:
            cur.execute("""select tipo, count(codigo) as c 
                from 
                    fii 
                where 
                    codigoexec = (select max(codigoexec) from fii) 
                group by 
                    tipo 
                order by 
                    c desc;""")
            return cur.fetchall()

    def getGeneral(self):
        logger.info('Getting General Stats')
        with self.conn.cursor() as cur:
            cur.execute("""select
                    'Todos',
                    count(codigo) as c, 
                    round(avg(dy)::numeric, 2), 
                    round(avg(dy10m)::numeric, 2),
                    round(avg(dyano)::numeric, 2),
                    round(avg(pvpa)::numeric,2)
                from 
 	                fiiultimaexec 
                order by 
	                c desc;""")
            return cur.fetchall()

    def getSubtipos(self):
        logger.info('Getting Subtypes')
        with self.conn.cursor() as cur:
            cur.execute("""select 
	                subtipo, 
                    count(codigo) as c, 
                    round(avg(dy)::numeric, 2), 
                    round(avg(dy10m)::numeric, 2),
                    round(avg(dyano)::numeric, 2),
                    round(avg(pvpa)::numeric,2)
                from 
 	                fiiultimaexec
                group by 
	                tipo,subtipo 
                order by 
	                c desc;""")
            return cur.fetchall()

    def getMyFiis(self):
        logger.info('Getting My Fiis')
        with self.conn.cursor() as cur:
            cur.execute("""select
                codigo, tipo, subtipo, cotacao,
                dy, dy10m, dyano, pvpa, url, notas
            from 
                fiiultimaexec
            where
	            lower(codigo) in ('xpcm11', 'hgcr11', 'rbva11', 'mxrf11', 'sptw11', 'famb11b')
            order by
	            codigo""")
            return cur.fetchall()

    def getRecomendacoes(self):
        logger.info('Getting Recomendations')
        with self.conn.cursor() as cur:
            cur.execute("""select 
                    codigo, tipo, subtipo, cotacao,
                    dy, dy10m, dyano, pvpa, url, notas 
                from
                    fiiultimaexec
                where
                    subtipo <> 'desenvolvimento' and
                    dy10m >= 6.6 and 
                    Ma < 0.35 and
                    Mi < 0.35
                order by 
                    pvpa""")
            return cur.fetchall()
