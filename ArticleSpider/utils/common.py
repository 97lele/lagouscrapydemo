import hashlib
import re
import time
from selenium.common.exceptions import NoSuchElementException,ElementNotVisibleException

list = ['\n', ' ', '\t', '经验', '/', '查看地图']


def get_now():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def clear_str(str):
    for s in list:
        str = re.sub(s, '', str)
    return str.strip()


def get_max_min_salary(str,is_max):
    match_re = re.match(r".*?(\d+).*?(\d+).*", str)
    if match_re:
        if is_max:
            return match_re.group(2)
        else:
            return match_re.group(1)
    else:
        return 0



def get_city(str):
    match_re = re.match(r".*?([\u4E00-\u9FA5]+)", str)
    if match_re:
        return match_re.group(1)


def get_num(str):
    match_re = re.match(r".*?(\d+).*", str)
    if match_re:
        return match_re.group(1)
    return 0


def get_addr(str):
    match_re = re.match(r".*?([\u4E00-\u9FA5\d]+)$", str)
    if match_re:
        return match_re.group(1)


def get_publish_time(str):
    match_re = re.match(".*(\d{4}[年/-]\d{1,2}([月/-]\d{1,2}|[月/-]$|$))", str)
    if match_re:
        return match_re.group(1)
    else:
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))








