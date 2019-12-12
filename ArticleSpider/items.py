# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.loader import ItemLoader
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
import re
from ArticleSpider.utils.common import get_publish_time, clear_str, get_md5, get_num


class LagouJobItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


class LagouCompany(scrapy.Item):
    tags = scrapy.Field(input_processor=MapCompose(Join('')))
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    company_name = scrapy.Field()
    industry = scrapy.Field()
    finance = scrapy.Field()
    people_count = scrapy.Field()
    city = scrapy.Field()
    score = scrapy.Field()
    create_date = scrapy.Field()
    company_desc = scrapy.Field()
    crawl_time = scrapy.Field()
    review_count = scrapy.Field(input_processor=MapCompose(get_num))
    job_count = scrapy.Field(input_processor=MapCompose(get_num))

    def get_insert_sql(item):
        insert_sql = """
        insert into lagou_company values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
          """
        params = (
            item["url"], item["url_object_id"], item["company_name"], item["industry"], item["finance"]
            , item["people_count"], item["city"], item["score"], item["create_date"], item['tags'],
            item["company_desc"], item["crawl_time"]
            , item["review_count"], item["job_count"]
        )
        return insert_sql, params


class LagouJob(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    max_salary = scrapy.Field(
    )
    min_salary = scrapy.Field(
    )
    job_city = scrapy.Field(
        input_processor=MapCompose(clear_str)
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(clear_str)
    )
    degree_need = scrapy.Field(input_processor=MapCompose(clear_str)
                               )
    job_type = scrapy.Field()
    publish_time = scrapy.Field(
        input_processor=MapCompose(get_publish_time)
    )
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=Join('')
    )
    job_addr = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    company_url_id = scrapy.Field(
        input_processor=MapCompose(get_md5)
    )
    tags = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(item):
        insert_sql = """
        insert into lagou_job values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
          """
        params = (
            item["url"], item["url_object_id"], item["title"]
            , item["max_salary"], item["min_salary"], item["job_city"], item["work_years"],
            item["degree_need"], item["job_type"],
            item["publish_time"], item["tags"], item["job_advantage"], item["job_desc"],
            item["job_addr"], item["company_url"], item["company_url_id"], item["company_name"],
            item["crawl_time"]
        )
        return insert_sql, params


class LagouReview(scrapy.Item):
    review_data_list = scrapy.Field()

    def get_insert_sql(item):
        data_list = item['review_data_list']
        values = []
        for data in data_list:
            for x in data:
                data[x] = format_str(data[x])
            value=','.join(data.values())
            value='('+value+')'
            values.append(value)

        insert_sql = "insert into lagou_review values {0}".format(','.join(values))
        params = ()
        return insert_sql, params


def format_str(str):
    return "'{0}'".format(str)
