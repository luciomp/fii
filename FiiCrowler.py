from selenium import webdrive
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class FiiCrowler:
    def __init__(self, timeout=30):
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        op.add_argument('--no-sandbox')
        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "eager"
        self.driver = webdriver.Chrome(options=op, desired_capabilities=caps)
        self.driver.set_page_load_timeout(timeout)
        self.driver.implicitly_wait(1)
        #self.driver.set_timeout(5)

    def __del__(self):
        self.driver.close()

    def getAll(self):
        #print('getAll')
        self.driver.get("https://fiis.com.br/lista-de-fundos-imobiliarios/")
        item_list = self.driver.find_element_by_id('items-wrapper')
        return [i.find_element_by_tag_name('a').get_attribute('href') for i in
        item_list.find_elements_by_class_name('item')]

    def getTV(self, e):
        #print('getTV')
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
        #print('getInfo')
        ib = self.driver.find_element_by_id(re)
        items = [self.getTV(i) for i in ib.find_elements_by_class_name('item')]
        return {i[0]: i[1] for i in items if i is not None}

    def getExtraInfo(self):
        #print('getExtraInfo')
        ei = self.driver.find_element_by_id('informations--extra')
        return {
            'notas': ei.find_element_by_class_name('notas').text,
            'taxas': ei.find_element_by_class_name('taxas').text
        }

    def getQuotationInfo(self):
        #print('getQuotationInfo')
        qi = self.driver.find_element_by_id('quotations--infos-wrapper')
        item = qi.find_element_by_class_name('item')
        value = item.find_element_by_class_name('value')
        return {
            'quotation': self.toFloat(value.text)
        }

    def getLastRevenues(self):
        #print('getLastRevenues')
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
        #print('clean')
        fii = {k.replace(' ', '').lower(): v for k,v in ofii.items()}
        fii[u'cotas'] = self.toInt(fii[u'númerodecotas'])
        fii[u'cotistas'] = self.toInt(fii[u'númerodecotistas'])
        tipo = fii['tipodofii'].split(':')
        fii['tipo'] = tipo[0].replace(' ', '').lower()
        fii['subtipo'] = tipo[1].replace(' ', '').lower() if len(tipo) > 1 else ''
        fii['dy'] = self.toFloat(fii['dividendyield'])
        fii['lastrevenue'] = self.toFloat(fii[u'últimorendimento'])
        fii['pl'] = self.toFloat(fii[u'patrimôniolíquido'])
        fii['vpa'] = self.toFloat(fii['valorpatrimonialporcota'])
        #print(fii)
        return fii

    def getDetail(self, fii_url):
        print('Getting Details for {0}'.format(fii_url))
        try:
            self.driver.get(fii_url)
            #print('Parsing...')
            fii = {}
            fii['id'] = self.driver.find_element_by_id('fund-ticker').text
            fii['name'] = self.driver.find_element_by_id('fund-name').text
            fii.update(self.getInfo('informations--basic'))
            fii.update(self.getExtraInfo())
            fii.update(self.getInfo('informations--indexes'))
            fii.update(self.getQuotationInfo())
            fii.update(self.getLastRevenues())
            return self.clean(fii)
        except Exception as error:
            return {'error': str(error)}

