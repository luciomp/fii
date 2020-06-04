class Fii:
    def __init__(self):
        self.codigoexec = None
        self.codigo = None
        self.url = None
        self.nome = None
        self.tipo = None
        self.subtipo = None
        self.dtregistrocvm = None
        self.cotas = None
        self.cotistas = None
        self.notas = None
        self.taxas = None
        self.dy = None
        self.ultimorendimento = None
        self.pl = None
        self.vpa = None
        self.cotacao = None
        self.pvpa = None

class Rendimento:
    def __init__(self):
        self.fii = None
        self.dtpagamento = None
        self.cotacao = None
        self.rendimento = None

class Error:
    def __init__(self):
        self.codigoexec = None
        self.codigo = None
        self.msg = None

class Report:
    def __init__(self):
        self.erros = None
        self.erroshdr = ['Erro', 'Qnt', 'Codigo']
        self.subtipos = None
        self.subtiposhdr = ['Setor', 'Qnt', 'DY', 'DY 10M', 'P/VPA']
        self.recomendacoes = None
        self.recomendacoeshdr = ['Codigo', 'Tipo', 'Setor', 'DY', 'DY 10M', 'P/VPA', 'Link', 'Nota']
