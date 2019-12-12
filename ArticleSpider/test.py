import re
from pyecharts.charts import Bar
from pyecharts.charts import Pie
import pyecharts.options as opts
import pandas as pd
import MySQLdb


conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="mptest", charset="utf8")
cursor = conn.cursor()

sql = """
select distinct tags from lagou_job
"""
cursor.execute(sql)

result = cursor.fetchall()
set = set()
for tag in result:
    temp=tag[0]
    list = temp.split(',')
    for item in list:
        if item != '' and re.match('[A-Za-z]',item):
         set.add(item)
# for tag in set:
#     sql = "select count(*) from lagou_job where tags like '%{0}%'".format(tag)
#     cursor.execute(sql)
print(set)
# data = pd.DataFrame({'food': ['bacon', 'pulled pork', 'bacon', 'pastrami','corned beef', 'bacon', 'pastrami', 'honey ham','nova lox', 'apple'],
#                   'ounces': [4, 3, 12, 6, 7.5, 8, 3, 5, 6, 0]})
# meat_to_animal = {'bacon': 'pig', 'pulled pork': 'pig', 'pastrami': 'cow', 'corned beef': 'cow', 'honey ham': 'pig', 'nova lox': 'salmon'}
# #  map转换
# print(data['food'].map(meat_to_animal))
#
