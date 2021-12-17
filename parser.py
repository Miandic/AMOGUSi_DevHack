from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import itertools
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


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
        self.city = city
        self.product_name = product_name
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

        wait = WebDriverWait(self.driver, 20)
        self.url = url
        self.soup = None

    def send_data(self):
        pass

    def to_xpath(self, name):
        xpath = xpath_soup(name)
        return self.driver.find_element_by_xpath(xpath)

    def take_data(self):
        pass


class ParserDNS(AbstractParser):
    def __init__(self, city, product_name, url):
        AbstractParser.__init__(self, city, product_name, url)
        self.driver.get(url)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def set_city(self):
        city_soup = self.soup.find("a" , {"class" : "w-choose-city-widget pseudo-link pull-right"})
        selenium_path_element = self.to_xpath(city_soup)
        ActionChains(self.driver).move_to_element(selenium_path_element).click().perform()

        time.sleep(2)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        city_soup = self.soup.find("input" , {"data-role" : "search-city"})
        selenium_path_element = self.to_xpath(city_soup)
        ActionChains(self.driver).move_to_element(selenium_path_element).click().send_keys(self.city).send_keys(Keys.ENTER).perform()

    def send_data(self):
        input_data = self.soup.find("a" , {"class" : "w-choose-city-widget pseudo-link pull-right"})
        selenium_path_element = self.to_xpath(input_data)
        ActionChains(self.driver).move_to_element(selenium_path_element).click().send_keys(self.product_name).perform()

        

a = ParserDNS("Москва", "geforce gtx 1650", "https://www.dns-shop.ru/")
a.set_city()
