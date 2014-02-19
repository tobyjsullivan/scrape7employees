from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import FormRequest, Request
from geese.items import EmployeeItem
import ConfigParser

class GeeseSpider(CrawlSpider):

    name = 'geese'
    allowed_domains = ['7geese.com']
    start_urls = ['https://www.7geese.com/members/?letter=A']
    rules = [Rule(SgmlLinkExtractor(allow=['/members/[.]*']), 'login')]
    config = ConfigParser.ConfigParser()

    def form_data(self):
        self.config.read("7geese.cfg")
        username = self.config.get('7GeeseAuth', 'Username')
        password = self.config.get('7GeeseAuth', 'Password')
        return {'username': username,'password': password}

    def login(self, response):
        return [FormRequest.from_response(response,
                    formdata=self.form_data(),
                    callback=self.parse_employees)]

    def parse_employees(self, response):
        sel = Selector(response)
        for cur_employee in sel.xpath("//div[@class='member ']"):
            employee = EmployeeItem()
            employee['email'] = cur_employee.xpath(".//a[@class='member-email']/text()").extract()[0]
            name = cur_employee.xpath(".//span[@class='member-name']/a/text()").extract()[0].split(' ', 1)
            employee['firstName'] = name[0]
            employee['lastName'] = name[1]
            employee['role'] = cur_employee.xpath(".//span[@class='position']/text()").extract()[0]
            yield employee
        for url in sel.xpath("//ul[@class='segmented-control alphabet']//a/@href").extract():
            yield Request('https://www.7geese.com'+url, callback=self.parse_employees)

