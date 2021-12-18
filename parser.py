from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import itertools
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import json


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
                "market": "DNS",
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

        time.sleep(3)


    def send_data_to_site(self):
        pass

    def to_xpath(self, name):
        xpath = xpath_soup(name)
        return self.driver.find_element_by_xpath(xpath)

    def read_data(self):
        pass


class ParserDNS(AbstractParser):
    def __init__(self, city, product_name, url):
        temp_str = product_name

        url = url + "search/?q=" + product_name.replace(' ', '+') + "&order=price-asc&stock=soft"

        self.product_name = temp_str

        AbstractParser.__init__(self, city, product_name, url)



    def send_data_to_site(self):
        city_soup = self.soup.find("a", {"class": "w-choose-city-widget pseudo-link pull-right"})
        selenium_path_element = self.to_xpath(city_soup)
        ActionChains(self.driver).move_to_element(selenium_path_element).click().perform()

        time.sleep(2)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        city_soup = self.soup.find("input", {"data-role": "search-city"})
        selenium_path_element = self.to_xpath(city_soup)
        ActionChains(self.driver).move_to_element(selenium_path_element).click().send_keys(self.city).send_keys(
            Keys.ENTER).perform()

    def read_data(self):

        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        time.sleep(3)
        is_available_soup = self.soup.find("div" , {"class" : "order-avail-wrap"})
        if (is_available_soup == None):
            self.returned_data_json["is_available"] = False
            return 0

        price_soup = self.soup.find("div", {"class": "product-buy__price"})
        price_text_raw = price_soup.text
        price_text = ""
        for i in range(len(price_text_raw)):
            if (price_text_raw[i].isnumeric()):
                price_text += price_text_raw[i]
        self.returned_data_json["price"] = price_text

class ParserRegard(AbstractParser):
    def __init__(self, city, product_name, url  ):
        AbstractParser.__init__(self, city, product_name, url)

        self.returned_data_json["market"] = "Regard"
    def send_data_to_site(self):
        input_product_soup = self.soup.find("input" , {"id" : "query"})

        input_product_selenium = self.to_xpath(input_product_soup)
        ActionChains(self.driver).move_to_element(input_product_selenium).click().send_keys(self.product_name).send_keys(Keys.ENTER).perform()
        time.sleep(1)
        self.soup = BeautifulSoup(self.driver.page_source , 'html.parser')

        sort_soup = self.soup.find("a" , {"onclick" : "sorting('price_asc')"})
        sort_selenium = self.to_xpath(sort_soup)
        ActionChains(self.driver).move_to_element(sort_selenium).click().perform()
        time.sleep(1)

    def read_data(self):
        self.soup = BeautifulSoup(self.driver.page_source , 'html.parser')

        price_div_soup  = self.soup.find("div" , {"class" :"price"})
        if (price_div_soup == None):

            self.returned_data_json["is_available"] = False
            return


        price_text_raw = price_div_soup.findAll("span")[1]
        price_text_raw = price_text_raw.text
        
        price_text = ""
        for  i in  range(len(price_text_raw)):
            if (price_text_raw[i].isnumeric()):
                price_text+=price_text_raw[i]

        self.returned_data_json["price"] = price_text


a = ParserRegard("Москва", "GeForce RTX 3060 Ti", "https://www.regard.ru/")
a.send_data_to_site()
a.read_data()
print(a.returned_data_json)
