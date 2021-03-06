# -*- coding: utf-8 -*-
import jieba
from lxml import etree
import requests
import time
import multiprocessing as mp
from wordcloud import WordCloud


class GetHtml(object):
    def get_one_page(self, url, headers, timeout=3):
        try:
            response = requests.get(url=url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                return response
            return None
        except TimeoutError:
            print("Time Out", url)
            time.sleep(1)
            return self.get_one_page(url=url, headers=headers, timeout=timeout + 3)
        except Exception as e:
            print(e, url)
            time.sleep(1)
            return self.get_one_page(url=url, headers=headers, timeout=timeout + 3)


class WordClouds(object):
    def wordc(self, file_name):
        with open("{}.txt".format(file_name), encoding="utf-8") as f:
            seg_list = jieba.cut(f.read(), cut_all=False)
            a = " ".join(seg_list)
            word_coulds = WordCloud(
                font_path='msyh.ttc',  # 字体
                background_color='white',  # 背景颜色
                max_words=5000,  # 要显示的词的最大个数
                min_font_size=9,  # 显示的最小的字体大小
                width=1100,  # 输出的画布宽度，默认为400像素
                height=650,  # 输出的画布高度，默认为400像素
                relative_scaling=1,  # 词频和字体大小的关联性
                random_state=20  # 可以有多少种随机配色
            )
            a = word_coulds.generate(a)
            a.to_file("{}.jpg".format(file_name))


class RenminRibao(GetHtml, WordClouds):  # 人民日报
    def __init__(self):
        self.url = "http://paper.people.com.cn/rmrb/html/{}/nbs.D110000renmrb_01.htm".format(time.strftime("%Y-%m/%d"))
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/67.0.3396.62 Safari/537.36"
        }
        self.timeout = 5
        self.name = "人民日报"

    def get_html(self):
        return self.get_one_page(url=self.url, headers=self.headers, timeout=self.timeout).content.decode()

    def parse(self, html):
        try:
            ele = etree.HTML(html)
            for i in ele.xpath('//div[@id="pageList"]/ul/div'):
                if i.xpath('.//text()')[1][-2:] == "要闻":
                    nbs = i.xpath('.//a[@id="pageLink"]/@href')
                    qz_url = "http://paper.people.com.cn/rmrb/html/{}/".format(time.strftime("%Y-%m/%d"))
                    if nbs[0][:3] == "nbs":
                        info_html = self.get_one_page(qz_url + nbs[0], headers=self.headers).content.decode()
                    else:
                        info_html = self.get_one_page(qz_url + nbs[0][2:], headers=self.headers).content.decode()
                    elee = etree.HTML(info_html)
                    for ii in elee.xpath('//div[@id="titleList"]/ul//li'):
                        data_html = self.get_one_page(qz_url + ii.xpath('./a/@href')[0], headers=self.headers).content.decode()
                        etr = etree.HTML(data_html)
                        yield "".join(etr.xpath('//div[@id="ozoom"]//p//text()'))
        except IndexError as e:
            print("人民日报", e)



    def save(self, info):
        with open("{}.txt".format(self.name), "a", encoding="utf-8") as f:
            f.write(info)
            f.write("\n")


    def run(self):
        s = time.time()
        html = self.get_html()
        for info in self.parse(html):
            self.save(info)
        self.wordc(self.name)
        e = time.time()
        print("人民日报完成，用时：", e-s)


class XinhuaRibao(GetHtml, WordClouds):  # 新华日报
    def __init__(self):
        # http://xh.xhby.net/mp3/pc/layout/201807/25/l1.html
        # self.url = "http://paper.people.com.cn/rmrb/html/{}/nbs.D110000renmrb_01.htm".format(time.strftime("%Y-%m/%d"))
        self.url = "http://xh.xhby.net/mp3/pc/layout/{}/".format(time.strftime("%Y%m/%d"))
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/67.0.3396.62 Safari/537.36"
        }
        self.timeout = 5
        self.name = "新华日报"

    def get_html(self):
        return self.get_one_page(url=self.url + "l1.html", headers=self.headers, timeout=self.timeout).content.decode()

    def parse(self, html):
        try:
            ele = etree.HTML(html)
            for i in ele.xpath('//ul[@class="page-num"]//li'):
                if i.xpath('./a/text()')[0][4:] in ["要闻", "重要新闻"]:
                    info_url = self.url + i.xpath('./a/@href')[0]
                    info_html = self.get_one_page(info_url, headers=self.headers).content.decode()
                    elee = etree.HTML(info_html)
                    for ii in elee.xpath('//ul[@id="articlelist"]//li'):
                        data_url = ii.xpath('./a/@href')[0].replace("../../..", "http://xh.xhby.net/mp3/pc")
                        data_html = self.get_one_page(data_url, headers=self.headers).content.decode()
                        el = etree.HTML(data_html)
                        yield "".join(el.xpath('//div[@id="ozoom"]//p//text()'))
        except IndexError as e:
            print("新华日报", e)

    def save(self, info):
        with open("{}.txt".format(self.name), "a", encoding="utf-8") as f:
            f.write(info)
            f.write("\n")


    def run(self):
        s = time.time()
        html = self.get_html()
        for info in self.parse(html):
            self.save(info)
        self.wordc(self.name)
        e = time.time()
        print("新华日报完成，用时：", e-s)

if __name__ == '__main__':
    # s = time.time()
    # renminribao = RenminRibao()
    # renminribao.run()
    # xinhuaribao = XinhuaRibao()
    # xinhuaribao.run()
    # e = time.time()
    # for i in range(5):
    s = time.time()
    renminribao = RenminRibao()
    xinhuaribao = XinhuaRibao()
    p1 = mp.Process(target=renminribao.run)
    # t1 = td.Thread(target=renminribao.run)
    p2 = mp.Process(target=xinhuaribao.run)
    # t2 = td.Thread(target=xinhuaribao.run)
    p1.start()
    p2.start()
    e = time.time()
    print("用时：", e-s)
