from pyecharts.charts import Bar
from pyecharts.charts import Pie
from pyecharts.charts import Geo
import pyecharts.options as opts
import MySQLdb
from wordcloud import WordCloud
import jieba
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os
import pandas as pd
import re

conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="mptest", charset="utf8")
cursor = conn.cursor()
project_dir = os.path.abspath(os.path.dirname(__file__))
data_store = os.path.join(project_dir, 'data')


# 创建停用词列表
def stopwordslist():
    stopwords = [line.strip() for line in open('stop.txt', encoding='UTF-8').readlines()]
    return stopwords


def check_path(file):
    if not os.path.exists(file):
        f = open(file, 'w')
        f.close()


class GetData(object):

    def get_worldcloud(self, column, picture, table, where):
        content = ''
        # 连接所有公司福利介绍
        sql = "select {0} from {1} {2}".format(column, table, where)
        result = cursor.execute(sql)
        for x in cursor.fetchall():
            content = content + x[0]
        # 去除多余字符
        reg = "[^A-Za-z\u4e00-\u9fa5]"
        content = re.sub(reg, '', content)
        stopwords = stopwordslist()
        for word in stopwords:
            content = re.sub(word, '', content)
        # jieba 切词，pandas、numpy计数
        jieba.load_userdict('keyword.txt')
        segment = jieba.cut(content)
        words_df = pd.DataFrame({'segment': segment})
        words_stat = words_df.groupby(by=['segment'])['segment'].agg(np.size)
        words_stat = words_stat.to_frame()
        words_stat.columns = ['count']
        words_stat = words_stat.reset_index().sort_values(by=["count"], ascending=False)
        image = np.array(Image.open(picture))
        word_frequence = {x[0]: x[1] for x in words_stat.values}
        wordcloud = WordCloud(font_path="msyh.ttc", width=800, height=500, mask=image, background_color="white")
        wordcloud.fit_words(word_frequence)
        # 绘制,可以不用绘制直接保存图片
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show()
        path = data_store + "\\" + table + '-' + column + ".png"
        check_path(path)
        wordcloud.to_file(path)

    def get_salary_city(self):
        sql = """
        select city,cast(sum((max_salary+min_salary)/2)/count(*) as signed) salary from lagou_job GROUP BY city order by salary desc
        """
        cursor.execute(sql)
        key = []
        values = []
        for info in cursor.fetchall():
            if not info[0]=='海外':
                key.append(info[0])
                values.append(info[1])



        max = values[0];
        geo = Geo(init_opts=opts.InitOpts(width="1600px", height="1000px"))
        geo.add_schema(maptype="china",
                       itemstyle_opts=opts.ItemStyleOpts(color="#DDF8FF", border_color="#111"),
                       )
        geo.add("薪资水平", [list(z) for z in zip(key, values)], type_="effectScatter")
        geo.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        geo.set_global_opts(
            visualmap_opts=opts.VisualMapOpts(max_=max),
            title_opts=opts.TitleOpts(title="各城市工资水平,单位K"))
        file = data_store + "\\" + "salary.html"
        check_path(file)
        geo.render(file)

    def get_company_city(self):
        sql = """
         select city,count(distinct url) as company_count from lagou_company GROUP BY city 
         """
        result = cursor.execute(sql)
        key = []
        values = []
        for info in cursor.fetchall():
            if info[0]!='海外' and re.match('[\u4e00-\u9fa5]',info[0]):
                key.append(info[0])
                values.append(info[1])
        geo = Geo(init_opts=opts.InitOpts(width="1600px", height="1000px"))
        geo.add_schema(maptype="china"
                       )
        geo.add("公司分布", [list(z) for z in zip(key, values)], type_="heatmap")
        geo.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        geo.set_global_opts(
            visualmap_opts=opts.VisualMapOpts(),
            title_opts=opts.TitleOpts(title="各城市公司分布"))
        file = data_store + "\\" + "company.html"
        check_path(file)
        geo.render(file)

    def get_bar(self, table, column, title):
        sql = "select count(*),{0} from {1} group by {2}".format(column,table, column)
        result = cursor.execute(sql)
        key = []
        values = []
        for info in cursor.fetchall():
            key.append(info[1])
            values.append(info[0])
        bar = Bar()
        bar.add_xaxis(key)
        bar.add_yaxis(title, values)
        bar.set_global_opts(title_opts=opts.TitleOpts(title=title))
        file = data_store + "\\" + table + '-' + column + ".html"
        check_path(file)
        bar.render(file)

    def get_work_data(self):
        work = """
        select * from 
        (select count(*) as count,'java' from lagou_job where title like '%java%'
        union
        select count(*) as count,'python' from lagou_job where title like '%python%'
        union
        select count(*) as count,'前端' from lagou_job where title like '%前端%'
        union
        select count(*) as count,'后台/后端' from lagou_job where title like '%后台%' or title like '%后端%'
        union
        select count(*) as count,'区块链' from lagou_job where title like '%区块链%'
        union
        select count(*) as count,'C++/C' from lagou_job where title like '%C++%' or title like '%C'
        union
        select count(*) as count,'产品' from lagou_job where title like '%产品%'
        union
        select count(*) as count,'运维' from lagou_job where title like '%运维%'
        union
        select count(*) as count,'测试' from lagou_job where title like '%测试%'
        union
        select count(*) as count,'网络' from lagou_job where title like '%网络%'
        union
        select count(*) as count,'安全' from lagou_job where title like '%安全%'
        union
        select count(*) as count,'.net' from lagou_job where title like '%.net%'
        union
        select count(*) as count,'php' from lagou_job where title like '%php%'
        union
        select count(*) as count,'大数据/数据相关' from lagou_job where title like '%大数据%' or title like '%数据%'
        union
        select count(*) as count,'算法/NLP/机器学习/ai/深度学习/自然语言/人工智能/图像' from lagou_job where title like '%机器学习%' or title like '%ai%' or title like'%深度学习%' or title like '%自然语言%' or title like '%智能%' or title like '%图像%' or title like '%.算法%' or title like '%NLP%'
        union
        select count(*) as count,'架构' from lagou_job where title like '%架构%'
        union
        select count(*) as count,'devops' from lagou_job where title like '%devops%'
        union
        select count(*) as count,'go' from lagou_job where title like '%go%')res order by count desc
        """
        result = cursor.execute(work)
        work_key = []
        work_value = []
        for info in cursor.fetchall():
            work_key.append(info[1])
            work_value.append(info[0])

        data_pair = [list(z) for z in zip(work_key, work_value)]
        pie = Pie(init_opts=opts.InitOpts(width="1600px", height="1000px"))
        pie.add(series_name="职位",
                data_pair=data_pair,
                )
        pie.set_global_opts(
            title_opts=opts.TitleOpts(
                title="职位需求分布",
                pos_left="center",
                pos_top="20",
                title_textstyle_opts=opts.TextStyleOpts(color="#fff"),
            ),
            legend_opts=opts.LegendOpts(is_show=False),

        )
        file = data_store + "\\" + "work.html"
        check_path(file)
        pie.render(file)
