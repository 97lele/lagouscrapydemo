# -*- coding: utf-8 -*-

import requests
import MySQLdb
import threading


conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="mptest", charset="utf8")
cursor = conn.cursor()
get_lock=threading.Lock()
import time


# 获取极光付费代理，每次获取10个
def crawl_ips():
    get_lock.acquire()
    time.sleep(1)
    url = 'http://d.jghttp.golangapi.com/getip?num=20&type=1&pro=&city=0&yys=0&port=1&pack=15711&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0"}
    resp = requests.get("{0}".format(url), headers=headers)
    resp = resp.text
    resp = resp.split("\r\n")
    for ip_info in resp[0:-1]:
        ip = ip_info.split(":")[0]
        port = ip_info.split(":")[1]
        cursor.execute(
            "insert proxy_ip(ip, port, speed, proxy_type) VALUES('{0}', '{1}', {2}, 'HTTP')".format(
                ip, port, 2
            )
        )
    conn.commit()
    get_lock.release()


class GetIP(object):
    def delete_ip(self, ip):
        # 从数据库中删除无效的ip
        delete_sql = """
            delete from proxy_ip where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port, delete, timeout):
        # 判断ip是否可用
        http_url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict, timeout=timeout)
        except Exception as e:
            if delete:
                self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                return True
            else:
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        # 从数据库中随机获取一个可用的ip
        count = """
        select count(*) from proxy_ip
        """
        result = cursor.execute(count)
        count = cursor.fetchone()[0]
        if count < 10:
            crawl_ips()

        random_sql = """
              SELECT ip, port, speed FROM proxy_ip
            ORDER BY RAND()
            LIMIT 1
            """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            timeout = int(ip_info[2]) + 2
            judge_re = self.judge_ip(ip, port, True, timeout)
            if judge_re:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()


crawl_ips()

