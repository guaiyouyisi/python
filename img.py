#encoding=utf-8

import sys,json,requests,time,os
from bs4 import BeautifulSoup
from contextlib import closing

"""
    批量下载妹子图片
"""
class downImg():

    def __init__(self):
        self.server = "https://www.jdlingyu.mobi/collection/meizitu"
        self.nextpage = "https://www.jdlingyu.mobi/wp-admin/admin-ajax.php?action=zrz_load_more_posts"
        self.formdata = {"type":"collection1495","paged":1}
        self.imgs = []
        self.maxPage = 1
        self.headers = {":authority": "www.jdlingyu.mobi", ":method": "GET", ":path": "/collection/meizitu", ":scheme": "https","upgrade-insecure-requests": 1,
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36"
        }
        self.nums = 0

    """
        获取 照片分组
        分组页面连接
        分组名
    """
    def getImgGroup(self):
        req = requests.get(url=self.server)
        req.headers = self.headers
        text = req.text
        html = BeautifulSoup(text,"html.parser")

        maxpage = html.find_all("page-nav")[0].get(":pages") # 获取最大页
        self.maxPage = int(maxpage)

        a = html.find_all("h2", class_ = "entry-title") # 获取第一页的 图组
        for each in a:
            t = each.a
            title = {"group":t.text,"imgs":t.get("href")} # 获取图组 链接
            self.imgs.append(title)
        if self.maxPage > 1:
            self.getNextPage() # 循环获取剩余页的图组链接

    """
        当最大页面大于1页时
        循环剩余页面
        获取照片分组
    """
    def getNextPage(self):
        for i in range(2,self.maxPage+1):
            self.formdata['paged'] = i
            req = requests.post(self.nextpage,self.formdata)
            text = req.text
            html = json.loads(text)
            a_bf = BeautifulSoup(html['msg'],'html.parser')
            a = a_bf.find_all("h2", class_ = "entry-title")
            for each in a:
                t = each.a
                title = {"group":t.text,"imgs":t.get("href")}
                self.imgs.append(title)

    """
        根据获取到的分组链接
        进入页面中
        获取分组中的照片链接
    """
    def getImages(self):
        for x in self.imgs:
            req = requests.get(url=x['imgs'])
            text = req.text
            html = BeautifulSoup(text,"html.parser")
            img = html.find_all("img", class_ = "alignnone size-medium")
            src = []
            for i in img:
                src.append(i.get("src")) 
            time.sleep(1)                       
            x['imgs'] = src
            

    """
        根据照片链接和所属分组
        生成文件夹及文件
        下载到本地
    """
    def download(self):
        path = "./imgs"                                                 # 定义下载到那个文件夹
        if os.path.exists(path) == False:                               # 判断文件夹是否存在并创建
            os.mkdir(path)
        for x in self.imgs:
            ph = path + "/" + x['group']                                # 定义分组文件夹 并判断是否存在 并创建
            if os.path.exists(ph) == False:
                os.mkdir(ph)
            for i in x['imgs']:
                filename = i[i.rfind("/")+1:]                           # 获取文件名 并判断是否存在 存在跳出循环
                filepath = ph + "/" + "%s" % filename
                if os.path.exists(filepath) == True:
                    continue
                with closing(requests.get(url=i)) as r:                 # 访问图片地址
                    with open(filepath, "ab+") as f:                        
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)                          # 写入文件    
                                f.flush()



if __name__ == "__main__":
    downImg = downImg()
    print("开始采集图片组")
    downImg.getImgGroup()
    print("采集图片组完成\n开始采集图片")
    downImg.getImages()
    print("采集图片完成\n开始下载图片")
    downImg.download()
    print("下载图片完成")
