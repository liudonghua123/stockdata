# coding=utf8

from urllib.request import urlopen, Request
# from urllib.error import HTTPError
import re
import json
# from json.decoder import JSONDecodeError
import traceback
import logging
from ast import literal_eval
from tablib import Dataset

pattern = re.compile("^.*?\((.+)\)$")

class Crawler:
    def __init__(self, url_template, date, count):
        self.url_template = url_template
        self.date = date
        self.count = count
        self.start_url = url_template.format(date=self.date, count=self.count, page=1)
        self.totalPages = self.getPages()
        self.data = []
    
    def getPages(self):
        jsonData = self.doRequest(self.start_url)
        return jsonData['sum'] // self.count + 1
    
    def crawler(self):
        for page in range(1, self.totalPages + 1):
            url = self.url_template.format(date=self.date, count=self.count, page=page)
            print('doRequest({url})'.format(url=url))
            jsonData = self.doRequest(url)
            listData = jsonData['list']
            self.data += listData
    
    def writeDataToExcel(self, filePath, sheetName):
        data = Dataset()
        data.json = json.dumps(self.data)
        with open('{filePath}-{sheetName}.xls'.format(filePath=filePath, sheetName=sheetName), 'wb') as f:
            f.write(data.export('xls'))
    
    def doRequest(self, url):
        try:
            req = Request(url, headers={'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"}) 
            connection = urlopen(req)
            # html = connection.read().decode("gb2312")
            html = connection.read().decode("gb18030")
            # Fix json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes
            # html = html.replace("\'", "\"")
            html = re.sub(r"(\w+):", lambda m: '"{content}":'.format(content=m.group(1)), html)
            connection.close()
            match = re.search(pattern, html)
            if not match:
                print('doRequest({url}) did not get expected data'.format(url=url))
                return None
            # https://stackoverflow.com/questions/38694800/how-to-convert-string-into-dictionary-in-python-3?noredirect=1&lq=1
            # return json.loads(match.group(1))
            return literal_eval(match.group(1))
        except Exception as exception:
            print('doRequest({url}) error with {exception}'.format(url=url, exception=exception))
            logging.error(traceback.format_exc())

if __name__ == '__main__':
    dates = ['2010-12-31', '2011-12-31', '2012-12-31', '2013-12-31', '2014-12-31', '2015-12-31', '2016-12-31', '2017-12-31']
    start_page = 1
    page_count = 100
    url_template = "http://stockdata.stock.hexun.com/zrbg/data/zrbList.aspx?date={date}&count={count}&pname=20&titType=null&page={page}&callback=hxbase_json11526691780158"
    for date in dates:
        print("crawler {date} data begin".format(date=date))
        cralwer = Crawler(url_template, date, page_count)
        cralwer.crawler()
        cralwer.writeDataToExcel('data', date)
        print("crawler {date} data end".format(date=date))

