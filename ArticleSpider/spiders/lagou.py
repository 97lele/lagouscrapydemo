# -*- coding: utf-8 -*-
from functools import reduce
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.items import LagouJob, LagouCompany, LagouJobItemLoader, LagouReview
from ArticleSpider.utils.common import get_md5, clear_str, get_now, get_max_min_salary, get_city
import re
import MySQLdb
from ArticleSpider.tool.crawl_jiguang import GetIP
from selenium import webdriver
import time
from scrapy.http import HtmlResponse
from selenium.common.exceptions import WebDriverException, ElementNotVisibleException, NoSuchElementException

conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="mptest", charset="utf8")
cursor = conn.cursor()
driver = webdriver.Chrome()


def handle_review_list(review_list, id_list, review_data_list, company_url, company_url_id, company_name):
    for review in review_list:
        review_data = dict()
        id = review.xpath("div[@class='review-action']//a//@data-id").extract_first('')
        review_data['id'] = id
        id_list.append("'" + id + "'")
        review_data['review_comment'] = review.xpath(
            "div[@class='review-content']//div[@class='interview-process']//text()").extract_first('')
        review_data['company_url'] = company_url
        review_data['company_url_id'] = company_url_id
        review_data['company_name'] = company_name
        review_data['review_tags'] = ','.join(
            review.xpath("div[@class='review-tags clearfix']//div//text()").extract())
        review_data['useful_count'] = review.xpath(
            "div[@class='review-action']/a/span/text()").extract_first('0')
        scores = review.xpath(
            "div[@class='review-stars clearfix']//span[@class='score']//text()").extract()
        score = round(reduce(lambda x, y: float(x) + float(y), scores) / len(scores), 1)
        review_data['score'] = score
        review_data['review_job'] = review.xpath(
            "div[@class='review-stars clearfix']//a[@class='job-name']//text()").extract_first('')
        review_data['comment_time'] = review.xpath(
            "div[@class='review-stars clearfix']//span[@class='review-date']//text()").extract_first('')
        review_data_list.append(review_data)


def return_new_company_response(request, response):
    if len(response.xpath("//span[@class='text_over']").extract()) > 0:
        time.sleep(1)
        driver.get(request.url)
        time.sleep(2)
        try:
            driver.find_element_by_xpath("//span[@class='text_over']").click()
        except ElementNotVisibleException as e:
            return response
        except WebDriverException as e:
            return response
        except NoSuchElementException as e:
            return response
        return HtmlResponse(url=driver.current_url, body=driver.page_source,
                            encoding="utf-8", request=request)
    else:
        return response


# 判断是否有该url
def check_table_url(table, url):
    check_sql = "SELECT * FROM {0} where url = '{1}'".format(table, url)
    cursor.execute(check_sql)
    return len(list(cursor)) == 0


def check_comment_in(param):
    check_sql = "select id from lagou_review where id in ({0})".format(",".join(param))
    cursor.execute(check_sql)
    return len(list(cursor)) == len(param)


def delete_ip(response):
    if response.status != 200:
        request = response.request
        ip = request.meta["proxy"]
        ip = ip.split('//')[1]
        get_ip.delete_ip(ip.split(':')[0])
        return False
    return True


get_ip = GetIP()


class LagouSpider(CrawlSpider):
    handle_httpstatus_list = [302]
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com']
    rules = (
        Rule(LinkExtractor(allow=("zhaopin/.*")), callback='parse_zhaopin', follow=True),
        Rule(LinkExtractor(allow=(r'jobs/\d+.html')), callback='parse_job', follow=True),
        Rule(LinkExtractor(allow=r'gongsi/\d+.html', restrict_xpaths="//dl[@id='job_company']"),
             callback='parse_company', follow=True),
        Rule(LinkExtractor(allow=r'gongsi/i\d+.html', restrict_xpaths="//a[@class='view-more']"),
             callback='parse_review', follow=True)
    )

    def parse_zhaopin(self, response):
        delete_ip(response)

    def parse_company(self, response):
        if delete_ip(response):
            url = response.url
            match_re = r'(https://www.lagou.com/gongsi/?\d+.html).*$'
            match = re.match(match_re, url)
            if match:
                url = match.group(1)
                if check_table_url('lagou_company', url):
                    response = return_new_company_response(response.request,response)
                    companyItemLoader = LagouJobItemLoader(item=LagouCompany(), response=response)
                    companyItemLoader.add_value('url', url)
                    companyItemLoader.add_value('url_object_id', get_md5(url))
                    tags = response.xpath("//div[@id='tags_container']//li//text()").extract()
                    if len(tags) != 0:
                        tags = clear_str((',').join(tags))
                    else:
                        tags = ''
                    companyItemLoader.add_value('tags', tags)
                    company_name = clear_str(
                        ''.join(response.xpath("//h1[@class='company_main_title']//text()").extract()))
                    companyItemLoader.add_value('company_name', company_name)
                    companyItemLoader.add_value('industry', response.xpath(
                        "//div[@id='basic_container']//li//i[@class='type']/following-sibling::span[1]//text()").extract_first(
                        ""))
                    companyItemLoader.add_value('finance', response.xpath(
                        "//div[@id='basic_container']//li//i[@class='process']/following-sibling::span[1]//text()").extract_first(
                        ""))
                    companyItemLoader.add_value('people_count', response.xpath(
                        "//div[@id='basic_container']//li//i[@class='number']/following-sibling::span[1]//text()").extract_first(
                        ""))
                    companyItemLoader.add_value('city', response.xpath(
                        "//div[@id='basic_container']//li//i[@class='address']/following-sibling::span[1]//text()").extract_first(
                        ""))
                    score = response.xpath("//span[@class='score']//text()").extract_first("0")
                    companyItemLoader.add_value('score', score)
                    create_date = response.xpath(
                        r"//div[@class='company_bussiness_info_container']//div[@class='content']//text()").extract()
                    if len(create_date) != 0:
                        create_date = create_date[1]
                    else:
                        create_date = ''
                    companyItemLoader.add_value('create_date', create_date)
                    company_desc = response.xpath(
                        "//div[@id='company_intro']/div[@class='item_content']/div[@class='company_intro_text']//text()").extract()
                    company_desc = clear_str(('').join(company_desc))
                    companyItemLoader.add_value('company_desc', company_desc.strip())
                    companyItemLoader.add_value('crawl_time', get_now())
                    company_data = response.xpath("//div[@class='company_data']//li//strong//text()").extract()
                    companyItemLoader.add_value('review_count', company_data[3].strip())
                    companyItemLoader.add_value('job_count', company_data[0].strip())
                    company_item = companyItemLoader.load_item()
                    return company_item

    def parse_job(self, response):
        if delete_ip(response):
            # 解析拉钩网职位
            url = response.url
            # 可能会被重定向，被重定向不做处理
            match_re = r'(https://www.lagou.com/jobs/?\d+.html).*$'
            match = re.match(match_re, url)
            if match:
                url = match.group(1)
                # 判断数据库是否有该url
                if check_table_url('lagou_job', url):
                    jobItemLoader = LagouJobItemLoader(item=LagouJob(), response=response)
                    jobItemLoader.add_xpath('title', "//div[@class='job-name']//h1/text()")
                    jobItemLoader.add_value('url', url)
                    url_object_id = get_md5(url)
                    jobItemLoader.add_value('url_object_id', url_object_id)
                    job_request = response.xpath("//dd[@class='job_request']//span/text()").extract()
                    salary = job_request[0].strip()
                    jobItemLoader.add_value('max_salary', get_max_min_salary(salary, True))
                    jobItemLoader.add_value('min_salary', get_max_min_salary(salary, False))
                    job_city = get_city(job_request[1])
                    jobItemLoader.add_value('job_city', job_city)
                    work_years = job_request[2]
                    jobItemLoader.add_value('work_years', work_years)
                    degree_need = job_request[3]
                    jobItemLoader.add_value('degree_need', degree_need)
                    job_type = job_request[4]
                    jobItemLoader.add_value('job_type', job_type)
                    jobItemLoader.add_xpath('publish_time', "//p[@class='publish_time']/text()")
                    jobItemLoader.add_xpath('job_advantage', "//dd[@class='job-advantage']//p/text()")
                    jobItemLoader.add_xpath('job_desc', "//div[@class='job-detail']//text()")
                    job_addr = ''.join(response.xpath("//div[@class='work_addr']//text()").extract())
                    jobItemLoader.add_value('job_addr', clear_str(job_addr))
                    jobItemLoader.add_value("company_name",
                                            response.xpath("//h3[@class='fl']/em/text()").extract()[0].strip())
                    jobItemLoader.add_xpath("company_url", "//dl[@class='job_company']//a/@href")
                    jobItemLoader.add_xpath("company_url_id", "//dl[@class='job_company']//a/@href")
                    tags = response.xpath("//ul[@class='position-label clearfix']//li/text()").extract()
                    if len(tags) != 0:
                        tags = clear_str((',').join(tags))
                    else:
                        tags = ''
                    jobItemLoader.add_value('tags', tags)
                    jobItemLoader.add_value('crawl_time', get_now())
                    job_item = jobItemLoader.load_item()
                    return job_item


    def parse_review(self, response):
        if delete_ip(response):
            url = response.url
            match_re = '(https://www.lagou.com/gongsi/i?\d+.html).*$'
            match = re.match(match_re, url)
            if match:
                review_item = LagouReview()
                review_data_list = list()
                company_url = response.xpath("//div[@class='reviews-title']/a/@href").extract()[0]
                company_url_id = get_md5(company_url)
                company_name = response.xpath("//div[@class='reviews-title']/a/text()").extract_first('')
                id_list = list()
                count = 5
                review_list = response.xpath("//div[@class='review-right']")
                handle_review_list(review_list, id_list, review_data_list, company_url, company_url_id, company_name)
                time.sleep(1)
                driver.get(url)
                for x in range(1, count):
                    try:
                        time.sleep(1)
                        driver.find_element_by_xpath("//span[@class='next']").click()
                        time.sleep(2)
                    except ElementNotVisibleException as e:
                        break
                    except WebDriverException as e:
                        break
                    except NoSuchElementException as e:
                        break
                    response = HtmlResponse(url=driver.current_url, body=driver.page_source,
                                            encoding="utf-8", request=url)
                    review_list = response.xpath("//div[@class='review-right']")
                    handle_review_list(review_list, id_list, review_data_list, company_url, company_url_id,
                                       company_name)
                if not check_comment_in(id_list):
                    review_item['review_data_list'] = review_data_list
                    return review_item
