import requests
import time
from pymongo import MongoClient
import json
import re
from lxml import etree


class Article:
    def __init__(self):
        self.titlelnk = ''
        self.title = ''
        self.diggnum =  ''
        self.summary =  ''
        self.author =  ''
        self.publishtime =  ''
        self.comment =  ''
        self.view =  ''
        self.content =  ''



headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}
connectionString='mongodb://localhost:27017/'
def saveData(data):
    client = MongoClient(connectionString)
    db = client['Test_mongo']
    coll = db['article']
    coll.insert_many(data)
def saveOne(data):
    client = MongoClient(connectionString)
    db = client['Test_mongo']
    coll = db['article']
    coll.insert_one(data)


def analyseList(url):
    articleList=[]
    # headers = {'User-Agent': str(UserAgent().chrome)}
    print('正在爬取文章列表：',url)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html = response.content
        html = html.decode(encoding='utf-8')
        html=etree.HTML(html)
        post_items=html.xpath('//div[@id="post_list"]/child::*')
        for item in post_items:
            article=Article()
            article.diggnum = item.xpath('.//span[@class="diggnum"]/text()')[0].strip()
            article.titlelnk = item.xpath('.//a[@class="titlelnk"]/@href')[0].strip()
            article.title=item.xpath('.//a[@class="titlelnk"]/text()')[0].strip()
            article.summary=item.xpath('.//p[@class="post_item_summary"]/text()')[0].strip()
            article.author=item.xpath('.//a[@class="lightblue"]/text()')[0].strip()
            article.publishtime=re.sub(r"[\u4E00-\u9FA5]+",'',item.xpath('.//div[@class="post_item_foot"]/text()')[1].strip())
            article.comment=re.findall(r'\d+',item.xpath('.//div[@class="post_item_foot"]/span[@class="article_comment"]/a[@class="gray"]/text()')[0].strip())[0]
            article.view=re.findall(r'\d+',item.xpath('.//div[@class="post_item_foot"]/span[@class="article_view"]/a/text()')[0].strip())[0]
            articleList.append(article)
    return articleList

def analyseArticle(articleList):
    for article in articleList:
        time.sleep(2)
        print('正在爬取文章详情：',article.titlelnk)
        res=requests.get(article.titlelnk)
        if(res.status_code==200):
            html=etree.HTML(str(res.content,encoding='utf-8'))
            div=html.xpath('//div[@id="cnblogs_post_body"]')[0]
            article.content=str(etree.tostring(div,encoding='utf-8'),encoding='utf-8')
            json_data=json.dumps(article, default=lambda obj: obj.__dict__,ensure_ascii=False,sort_keys=True)    
            saveOne(eval(json_data))
          
def createUrl(pageIndex):
    url = 'https://www.cnblogs.com/pick/{}'
    if(pageIndex==1):
        return url.format('')
    else:
        return url.format('#p'+str(pageIndex))


def startScrapy(start=1,end=83):
    for n in range(start,end):
        articleList= analyseList(createUrl(n))
        analyseArticle(articleList)
        time.sleep(3)
startScrapy(1,83)    

