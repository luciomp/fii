from selenium import webdriver
import json
from datetime import datetime

class FiiCrowler:
    def __init__(self, timeout=30):
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        op.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=op)
        self.driver.set_page_load_timeout(timeout)
        self.driver.implicitly_wait(timeout)
        #self.driver.set_timeout(5)

    def __del__(self):
        self.driver.close()

    def getAll(self):
        self.driver.get("https://fiis.com.br/lista-de-fundos-imobiliarios/")
        item_list = self.driver.find_element_by_id('items-wrapper')
        return [i.find_element_by_tag_name('a').get_attribute('href') for i in
        item_list.find_elements_by_class_name('item')]

    def getTV(self, e):
        try:
            return e.find_element_by_class_name('title').text, e.find_element_by_class_name('value').text
        except:
            return None

    def toInt(self, n):
        return int(n.replace('.', ''))

    def toFloat(self, n):
        i = n.replace('.', '').replace(',', '.').replace('%', '').replace('R$', '')
        if 'B' in i: return float(i.replace('B', ''))*1000000000
        if 'M' in i: return float(i.replace('M', ''))*1000000
        return float(i)

    def getInfo(self, re):
        ib = self.driver.find_element_by_id(re)
        items = [self.getTV(i) for i in ib.find_elements_by_class_name('item')]
        return {i[0]: i[1] for i in items if i is not None}

    def getExtraInfo(self):
        ei = self.driver.find_element_by_id('informations--extra')
        return {
            'notas': ei.find_element_by_class_name('notas').text,
            'taxas': ei.find_element_by_class_name('taxas').text
        }

    def getQuotationInfo(self):
        qi = self.driver.find_element_by_id('quotations--infos-wrapper')
        item = qi.find_element_by_class_name('item')
        value = item.find_element_by_class_name('value')
        return {
            'quotation': self.toFloat(value.text)
        }

    def getLastRevenues(self):
        t = self.driver.find_element_by_id('last-revenues--table')
        tbody = t.find_element_by_tag_name('tbody')
        revenues = []
        for row in tbody.find_elements_by_tag_name('tr'):
            colums = [c.text for c in row.find_elements_by_tag_name('td')]
            revenues.append({
                'dt': colums[1],
                'quotation': self.toFloat(colums[2]),
                'revenue': self.toFloat(colums[4])
            })
        return {'revenues': revenues}

    def clean(self, ofii):
        fii = {k.replace(' ', '').lower(): v for k,v in ofii.items()}
        fii[u'cotas'] = self.toInt(fii[u'númerodecotas'])
        fii[u'cotistas'] = self.toInt(fii[u'númerodecotistas'])
        tipo = fii['tipodofii'].split(':')
        fii['tipo'] = tipo[0].replace(' ', '').lower()
        fii['subtipo'] = tipo[1].replace(' ', '').lower()
        fii['dy'] = self.toFloat(fii['dividendyield'])
        fii['lastrevenue'] = self.toFloat(fii[u'últimorendimento'])
        fii['pl'] = self.toFloat(fii[u'patrimôniolíquido'])
        fii['vpa'] = self.toFloat(fii['valorpatrimonialporcota'])
        return fii

    def getDetail(self, fii_url):
        print('Getting Details for {0}'.format(fii_url))
        self.driver.get(fii_url)
        fii = {}
        fii['id'] = self.driver.find_element_by_id('fund-ticker').text
        fii['name'] = self.driver.find_element_by_id('fund-name').text
        fii.update(self.getInfo('informations--basic'))
        fii.update(self.getExtraInfo())
        fii.update(self.getInfo('informations--indexes'))
        fii.update(self.getQuotationInfo())
        fii.update(self.getLastRevenues())
        return self.clean(fii)

def readFromFile(filename):
    with open(filename, 'r') as f:
        return json.loads(f.read())

def saveToFile(filename, fiis):
    with open(filename, 'w') as f:
        f.write(json.dumps(fiis))

fc = FiiCrowler()
filename = 'crowledfiis.json'
fiis = readFromFile(filename)
print(fiis)
fiis[datetime.now().isoformat()] = {fii: fc.getDetail(fii) for fii in fc.getAll()}
saveToFile(filename, fiis)
