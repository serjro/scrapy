# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup as bs
from jobparser.items import JobparserItem
from jobparser.pipeline import JobparserPipeline

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?&only_with_salary=true&st=searchVacancy&text=python']

    def salary_pre(self, str_in):
        usd_rate = 72.5

        str_in = fr"{str_in}"
        if str_in.find('от') != -1:
            salary_from = int("".join(c for c in str_in if c.isdigit()))
            salary_to = salary_from
        if str_in.find('до') != -1:
            salary_to = int("".join(c for c in str_in if c.isdigit()))
            salary_from = salary_to
        if str_in.find('–') != -1:
            salary_from = int("".join(c for c in str_in[:str_in.find('–')] if c.isdigit()))
            salary_to = int("".join(c for c in str_in[str_in.find('–'):] if c.isdigit()))
        if salary_from < 15000:
            salary_from = salary_from * usd_rate
        if salary_to < 15000:
            salary_to = salary_to * usd_rate
        return salary_from, salary_to

    def parse(self, response: HtmlResponse):
        next_page = 'https://hh.ru' \
                    + response.css('a[class="bloko-button"][data-qa="pager-next"]').attrib['href']
        response.follow(next_page, callback=self.parse)
        vacansy = response.css(
            'div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header '
            'a.bloko-link::attr(href)'
        ).extract()
        for link in vacansy:
            yield response.follow(link, callback=self.vacansy_parse)

        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def vacansy_parse(self, response: HtmlResponse):
        site="hh.ru"
        name = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/text()").get()
        link = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").get()
        salary= response.xpath("//span[@data-qa='vacancy-serp__vacancy-compensation']").get()
        soup = bs(salary, "html.parser").get_text()
        cur=salary[salary.rfind("<!-- -->")+8:salary.find("</span>")]
        salary = soup.replace(cur, "").strip()
        sfrom, sto = self.salary_pre(salary)
        print('\nНазвание вакансии: ', name)
        print('Зарплата от: ', sfrom)
        print('Зарплата до: ', sto)
        print('Ссылка: ', link)
        print('Сайт: ',site)
        item=JobparserItem(name=name, salary_from=sfrom, salary_to=sto, link=link, site=site)
        pip=JobparserPipeline()
        pip.process_item(item,HhruSpider)
        yield item


