from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

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

    def __del__(self):
        self.driver.close()

    def getAll(self):
        logger.info('Getting Fiis')
        try:
            self.driver.get("https://fiis.com.br/lista-de-fundos-imobiliarios/")
            item_list = self.driver.find_element_by_id('items-wrapper')
            return [(i.find_element_by_class_name('ticker').text,
                i.find_element_by_tag_name('a').get_attribute('href')) 
                for i in item_list.find_elements_by_class_name('item')]
        except Exception as error:
            logger.error('Error getting Fiis: {0}'.format(str(error)))
            return []

    def getTV(self, e):
        try:
            return e.find_element_by_class_name('title').text, e.find_element_by_class_name('value').text
        except Exception as error:
            logger.error('Error getting TV: {0}'.format(str(error)))
            return None

    def toInt(self, n):
        return int(n.replace('.', ''))

    def toFloat(self, n):
        i = n.replace('.', '').replace(',', '.').replace('%', '').replace('R$', '')
        if 'B' in i: return float(i.replace('B', ''))*1000000000
        if 'M' in i: return float(i.replace('M', ''))*1000000
        return float(i)

    def getInfo(self, re):
        logger.debug('getInfo')
        ib = self.driver.find_element_by_id(re)
        items = [self.getTV(i) for i in ib.find_elements_by_class_name('item')]
        return {i[0]: i[1] for i in items if i is not None}

    def getExtraInfo(self):
        logger.debug('getExtraInfo')
        ei = self.driver.find_element_by_id('informations--extra')
        return {
            'notas': ei.find_element_by_class_name('notas').text,
            'taxas': ei.find_element_by_class_name('taxas').text
        }

    def getQuotationInfo(self):
        logger.debug('getQuotationInfo')
        qi = self.driver.find_element_by_id('quotations--infos-wrapper')
        item = qi.find_element_by_class_name('item')
        value = item.find_element_by_class_name('value')
        return {
            'quotation': self.toFloat(value.text)
        }

    def getLastRevenues(self):
        logger.debug('getLastRevenues')
        t = self.driver.find_element_by_id('last-revenues--table')
        tbody = t.find_element_by_tag_name('tbody')
        revenues = []
        for row in tbody.find_elements_by_tag_name('tr'):
            colums = [c.text for c in row.find_elements_by_tag_name('td')]
            revenues.append({
                'dt': datetime.strptime(colums[1], '%d/%m/%y').date(),
                'quotation': self.toFloat(colums[2]),
                'revenue': self.toFloat(colums[4])
            })
        return {'revenues': revenues}

    def clean(self, ofii):
        logger.debug('clean')
        fii = {k.replace(' ', '').lower(): v for k,v in ofii.items()}
        fii[u'cotas'] = self.toInt(fii[u'númerodecotas'])
        fii[u'cotistas'] = self.toInt(fii[u'númerodecotistas'])
        tipo = fii['tipodofii'].split(':')
        fii['tipo'] = tipo[0].replace(' ', '').lower()
        fii['subtipo'] = tipo[1].replace(' ', '').lower() if len(tipo) > 1 else ''
        try:
            fii['dtregistercvm'] = datetime.strptime(fii['registrocvm'], '%d/%m/%Y').date()
        except:
            fii['dtregistercvm'] = datetime.now()
        fii['dy'] = self.toFloat(fii['dividendyield'])
        fii['lastrevenue'] = self.toFloat(fii[u'últimorendimento'])
        fii['pl'] = self.toFloat(fii[u'patrimôniolíquido'])
        fii['vpa'] = self.toFloat(fii['valorpatrimonialporcota'])
        fii['p/vpa'] = fii['quotation'] / fii['vpa'] if fii['vpa'] != 0 else None
        return fii

    def getDetail(self, fii_code, fii_url):
        logger.info('Getting Details for {0}'.format(fii_code))
        try:
            self.driver.get(fii_url)
            fii = {}
            fii['code'] = fii_code
            fii['url'] = fii_url
            fii['id'] = fii_code
            fii['name'] = self.driver.find_element_by_id('fund-name').text
            fii.update(self.getInfo('informations--basic'))
            fii.update(self.getExtraInfo())
            fii.update(self.getInfo('informations--indexes'))
            fii.update(self.getQuotationInfo())
            fii.update(self.getLastRevenues())
            return self.clean(fii)
        except Exception as error:
            logger.error('Error getting detail: {0}'.format(str(error)))
            return {'code': fii_code, 'error': str(error)}

