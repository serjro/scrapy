import scrapy


class JobparserItem(scrapy.Item):

    _id = scrapy.Field()
    name = scrapy.Field()
    salary_from = scrapy.Field()
    salary_to = scrapy.Field()
    link = scrapy.Field()
    site = scrapy.Field()
    pass
