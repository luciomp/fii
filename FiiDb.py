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
                select msg, count(id), string_agg(codigo, ' ') 
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
            cur.execute("""select tipo, count(id) as c 
                from 
                    fii 
                where 
                    codigoexec = (select max(codigoexec) from fii) 
                group by 
                    tipo 
                order by 
                    c desc;""")
            return cur.fetchall()

    def getSubtipos(self):
        logger.info('Getting Subtypes')
        with self.conn.cursor() as cur:
            cur.execute("""select 
	                subtipo, 
                    count(id) as c, 
                    round(avg(dy)::numeric, 2), 
                    round(avg(dya)::numeric, 2) as apvpa,
                    round(avg(pvpa)::numeric,2)
                from 
 	                fii 
                left join (
	                select 
		                fii as fiiid, sum(r.rendimento/f.cotacao)*100 as dya
	                from 
		                fii as f, rendimento as r 
	                where 
		                f.id = r.fii 
	                group by 
		                r.fii 
                ) t2 on fii.id = fiiid
                where 
	                codigoexec = (select max(codigoexec)  from fii) 
                group by 
	                tipo,subtipo 
                order by 
	                c desc;""")
            return cur.fetchall()

    def getRecomendacoes(self):
        logger.info('Getting Recomendations')
        with self.conn.cursor() as cur:
            cur.execute("""select 
                    codigo, tipo, subtipo, 
                    round(dy::numeric, 2), 
                    round(dya::numeric, 2),
                    round(pvpa::numeric, 2), 
                    url, 
                    notas
                from 
                    fii 
                left join (
	                select 
                        fii as fiiid, 
                        sum(r.rendimento/f.cotacao)*100 as dya, 
                        max(dtpagamento) as mdtpgto, 
                        (max(rendimento) - avg(rendimento)) / avg(rendimento) as Ma,
                        (avg(rendimento) - min(rendimento)) / avg(rendimento) as Mi
                        from 
                            fii as f, rendimento as r 
	                    where 
                            f.id = r.fii 
                        group by 
                            r.fii 
                ) t2 on fii.id = fiiid
                where
                    codigoexec = (select max(codigoexec) from fii) and
                    tipo <> 'papel' and 
                    subtipo <> 'desenvolvimento' and
                    mdtpgto > now() - interval '10 months' and 
                    dya >= 7 and 
                    Ma < 0.35 and
                    Mi < 0.35
                order by 
                    pvpa,dy desc""")
            return cur.fetchall()
