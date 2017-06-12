# -*- coding: utf-8 -*-

import bs4
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import os
import time
import json
import random
import logging, logging.handlers
import argparse
import re
import chardet
from jd_coupon import JDCoupon
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# get function name
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

class JDCrawler(JDCoupon):
    '''
    This class used to search JD coupon
    '''
    def find_coupons(self, url):
        try:
            resp = self.sess.get(url)
            if resp.status_code != requests.codes.OK:
                return 0
        except Exception, e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return 0
        resp.encoding='utf-8'
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        tags = soup.select('title')
        tt = tags[0].text.strip(' \t\r\n')
        logging.info(u'{}'.format(tt))
        logging.info(u'{}'.format(url))
        link_list =re.findall(r"(https://coupon.jd.com/\S+.html)" ,resp.text)
        link_list = list(set(link_list))
        for link in link_list:
            link = link.replace('&amp;','&') 
            self.click(link, logging.WARNING)
            logging.warning(link)
        return len(link_list)
    
    def find_pages(self, url):
        try:
            resp = self.sess.get(url)
            if resp.status_code != requests.codes.OK:
                return 0
        except Exception, e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return 0
        link_list =re.findall(r"(https://sale.jd.com/act/\w+.html)" ,resp.text)
        link_list.append(url)
        link_list = list(set(link_list))
        logging.info(u'找到{}个网页'.format(len(link_list)))
        cnt = 0
        for link in link_list:
            cnt += self.find_coupons(link)
        logging.info(u'找到{}个优惠券'.format(cnt))
        return cnt

if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and click coupon')
    parser.add_argument('-u', '--url', 
                        help='Entry URL', required=True)
    parser.add_argument('-l', '--log', 
                        help='Log file', default=None)
    options = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - (%(levelname)s) %(message)s', datefmt='%H:%M:%S')  
    if (options.log != None):
        log_hdl = logging.FileHandler(options.log,"w")  
        log_hdl.setLevel(logging.INFO)
        log_fmt = logging.Formatter('%(asctime)s - (%(levelname)s) %(message)s', '%H:%M:%S')  
        log_hdl.setFormatter(log_fmt)  
        logging.getLogger('').addHandler(log_hdl)

    jd = JDCrawler()
    if not jd.login_by_QR():
        sys.exit(1)
    jd.find_pages(options.url)
