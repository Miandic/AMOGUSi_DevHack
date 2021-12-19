from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import itertools
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import json
import threading


def xpath_soup(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        previous = itertools.islice(parent.children, 0, parent.contents.index(child))
        xpath_tag = child.name
        xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
        components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

class AbstractParser():
    def __init__(self, city, product_name, url):
        self.returned_data_json ={
                "market": "dns",
                "name" : product_name,
                "is_available" : True,
                "price" : "0"

        }
        self.url = url
        self.city = city
        self.product_name = product_name
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

        self.driver.get(self.url)
        self.driver.maximize_window()
        WebDriverWait(self.driver, 20)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')


    def send_data_to_site(self):
        pass

    def to_xpath(self, name):
        xpath = xpath_soup(name)
        return self.driver.find_element_by_xpath(xpath)

    def read_data(self):
        pass
    def click_element(self , element_to_find, parametr , paramatr_value ):

        soup_element = self.soup.find(element_to_find, {parametr: paramatr_value})
        selenium_path_element = self.to_xpath(soup_element)
        ActionChains(self.driver).move_to_element(selenium_path_element).click().perform()

    def insert_data_to_element(self ,  parametr , paramatr_value , inserted_value ):
        soup_element = self.soup.find("input", {parametr: paramatr_value})
        selenium_path_element = self.to_xpath(soup_element)

        ActionChains(self.driver).move_to_element(selenium_path_element).click().send_keys(inserted_value).send_keys(
            Keys.ENTER).perform()

    def parse_site(self):
        self.send_data_to_site()
        self.read_data()

    def update_soup(self , time_to_wait):
        time.sleep(time_to_wait)
        self.soup = BeautifulSoup(self.driver.page_source , 'html.parser')
    def raw_text_to_send_num(self, text_raw):
        text = ""
        for i in range(len(text_raw)):
            if (text_raw[i].isnumeric()):
                text += text_raw[i]
        return text
    def parse(self):
        self.send_data_to_site()

        self.read_data()


class ParserDNS(AbstractParser):
    def __init__(self, city, product_name):
        temp_str = product_name
        url = "https://www.dns-shop.ru/" + "search/?q=" + product_name.replace(' ', '+') + "&order=price-asc&stock=soft"
        product_name = temp_str

        AbstractParser.__init__(self, city, product_name, url)

    def send_data_to_site(self):
        time.sleep(2)

        self.click_element("a" , "class" , "w-choose-city-widget pseudo-link pull-right")

        self.update_soup(2)
        city_soup = self.soup.find("input", {"data-role": "search-city"})
        selenium_path_element = self.to_xpath(city_soup)
        ActionChains(self.driver).move_to_element(selenium_path_element).click().send_keys(self.city).perform()

        self.update_soup(3)

        all_data_cities = self.soup.find("ul" , {"class" : "cities-search"})

        all_data_cities = all_data_cities.findAll("span" )

        for i in range(len(all_data_cities)):
            t = all_data_cities[i].text

            if (t.lower() == self.city):
                data_city_selenium = self.to_xpath(all_data_cities[i])
                ActionChains(self.driver).move_to_element(data_city_selenium).click().perform()
                break


    def read_data(self):
        self.update_soup(3)

        is_available_soup = self.soup.find("span" , {"class" : "available"})

        if (is_available_soup == None or is_available_soup.text != "В наличии: "):
            self.returned_data_json["is_available"] = False
            return 0

        price_soup = self.soup.find("div", {"class": "product-buy__price"})
        price_text_raw = price_soup.text
        price_text = self.raw_text_to_send_num(price_text_raw)

        self.returned_data_json["price"] = price_text


class ParserRegard(AbstractParser):
    def __init__(self, city, product_name  ):

        AbstractParser.__init__(self, city, product_name, "https://www.regard.ru/")

        self.returned_data_json["market"] = "regard"
    def send_data_to_site(self):
        time.sleep(2)

        self.insert_data_to_element("id" , "query" , self.product_name)

        self.update_soup(2)

        russia = self.soup.find("span", {"class" : "filter-text"})
        if (russia != None):
            russia = russia.find("a")
            russia_selenium = self.to_xpath(russia)
            ActionChains(self.driver).move_to_element(russia_selenium).click().perform()

        self.click_element("a" , "onclick" , "sorting('price_asc')")


    def read_data(self):
        self.update_soup(1)

        price_div_soup  = self.soup.find("div" , {"class" :"price"})
        if (price_div_soup == None):

            self.returned_data_json["is_available"] = False
            return

        price_text_raw = price_div_soup.findAll("span")[1]
        price_text_raw = price_text_raw.text

        price_text = self.raw_text_to_send_num(price_text_raw)
        self.returned_data_json["price"] = price_text


class ParserCitilink(AbstractParser):
    def __init__(self, city, product_name, url  ):
        AbstractParser.__init__(self, city, product_name, url)
    def send_data_to_site(self):
        button_city_soup = self.soup.find("button" , {"class" : "js--CitiesSearch-trigger MainHeader__open-text TextWithIcon"})
        button_city_selenium = self.to_xpath(button_city_soup)
        ActionChains(self.driver).move_to_element(button_city_selenium).click().perform()

        time.sleep(2)
        self.soup = BeautifulSoup(self.driver.page_source , 'html.parser')

        input_city_soup = self.soup.find("input" , {"name" :"search_text" })
        input_city_selenium = self.to_xpath(input_city_soup)
        ActionChains(self.driver).move_to_element(input_city_selenium).click().send_keys(self.city).perform()

        time.sleep(2)
        self.soup = BeautifulSoup(self.driver.page_source , 'html.parser')

        click_city_soup = self.soup.find("span" , {"class" :"CitiesSearch__highlight" })
        click_city_selenium = self.to_xpath(click_city_soup)
        ActionChains(self.driver).move_to_element(click_city_selenium).click().perform()


with open ('data.json' , encoding = 'utf-8') as f:
    all_data = json.load(f )

data_to_send = {}

for key in  all_data.keys():
    data_to_send[key] = data_to_send.get(key , [])
    for i in range(len(all_data[key])):
        parser_DNS = ParserDNS(key , all_data[key][i])
        parser_REGARD = ParserRegard(key , all_data[key][i])

        thread_dns = threading.Thread(target = parser_DNS.parse_site())
        thread_regard = threading.Thread(target = parser_REGARD.parse_site())

        thread_dns.start()
        thread_regard.start()

        thread_dns.join()
        thread_regard.join()

        if (parser_DNS.returned_data_json["is_available"]):
            data_to_send[key].append(parser_DNS.returned_data_json)
        if (parser_REGARD.returned_data_json["is_available"]):
            data_to_send[key].append(parser_REGARD.returned_data_json)
with open('sendedData.json' , 'w' , encoding = "utf-8") as f:
    json.dump(data_to_send , f , ensure_ascii = False)
