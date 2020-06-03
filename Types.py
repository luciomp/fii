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
