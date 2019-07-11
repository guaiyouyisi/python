# -*- coding:UTF-8 -*-
from bs4 import BeautifulSoup
import pymysql,sys,requests

"""
下载笔趣阁小说
示例《一念永恒》
"""

class caiji:

    def __init__(self):
        self.db = ''
        self.cursor = ''
        self.target = "https://www.biqukan.com/1_1094"
        self.host = "https://www.biqukan.com"
        self.nums = 0                                       # 章节数
        self.names = []                                     # 章节标题
        self.urls = []                                      # 章节链接
        self.book = ''
        self.author = ''
        self.desc = ''

    # 数据库连接
    def mysql_connect(self):
        db = pymysql.connect('localhost','root','root','python')
        cursor = db.cursor()
        self.db = db
        self.cursor = cursor

    # 数据库关闭
    def mysql_close(self):
        self.db.close()

    # 获取章节链接 章节名 章节数
    def get_urls(self):
        req = requests.get(url=self.target) # 访问
        req.encoding = "gbk"                # 网页编码
        html = req.text
        text = BeautifulSoup(html,"html.parser")
        meta = text.find_all("meta")
        for n in meta:
            if n.get("property") == "og:novel:author":
                self.author = n.get("content")
            if n.get("property") == "og:novel:book_name":
                self.book = n.get("content")
        desc = text.find_all("div", class_ = "intro")
        desc = desc[0]
        desc = str(desc).split("<br/>")[0]
        desc = str(desc).split("</span>")[1]
        self.desc = desc
        dl = text.find_all("dl")
        a_bf = BeautifulSoup(str(dl[0]),"html.parser")
        a = a_bf.find_all("a")
        a = a[12:]
        # a = a[:-2]
        self.nums = len(a)
        for x in a:
            if x.text.split()[0] != "第":
                continue
            self.urls.append(self.host + x.get('href'))
            self.names.append(x.text)
    
    def get_content(self,target):
        req = requests.get(url=target)
        req.encoding = "gbk"
        html = req.text
        text = BeautifulSoup(html,"html.parser")
        title = text.body.h1.text
        content = text.find_all('div', class_ = "showtxt")
        content = content[0].text.replace("\xa0"*7,'\n')
        return {"title":title,"content":content}

    def get_result(self,sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return result[0]

    def addBook(self):
        book_id = 0
        is_book_sql = "SELECT count(*) FROM books WHERE name = '%s'" % self.book
        try:
            count = self.get_result(is_book_sql)
            if count == 0:
                add_book_sql = "INSERT INTO books(`name`,`author`,`desc`) VALUES('%s','%s','%s')" %(self.book,self.author,self.desc)
                self.cursor.execute(add_book_sql)

            self.db.commit()
        except:
            self.db.rollback()
        
        book_id =  self.get_result("SELECT id FROM books WHERE name = '%s'" % self.book)
        return book_id

    def insert(self,obj,book_id):
        title = obj['title']
        content = obj['content']
        res = False
        add_article_sql = "INSERT INTO articles(title,contents,book_id) VALUES('%s','%s','%s')" %(title,content,book_id)
        try:
            res = True if(self.cursor.execute(add_article_sql)) else False
            self.db.commit()
        except:
            self.db.rollback()

        return res

if __name__ == "__main__":
    cj = caiji()
    cj.target = input("请输入小说目录链接：")
    cj.get_urls()
    cj.mysql_connect()

    book_id = cj.addBook()
    if book_id == False:
        print("新增《%s》书籍失败" % cj.book)
        sys.exit(0)

    print("%s 开始采集\n" % cj.book)    
    for i in range(cj.nums):
        url = cj.urls[i]
        res = cj.insert(cj.get_content(url),book_id)
        sys.stdout.write("  已采集：%.3f%%" %  float(i/cj.nums) + '\r')
        if(res == False):
            print("%s采集失败" % cj.names[i])
        
        sys.stdout.flush()
    print("%s 采集完成" % cj.book)
    cj.mysql_close()