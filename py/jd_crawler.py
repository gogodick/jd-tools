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
import multiprocessing
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
    def search_page(self, url):
        try:
            resp = self.sess.get(url)
            if resp.status_code != requests.codes.OK:
                return [], []
        except Exception, e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return [], []
        resp.encoding='utf-8'
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        tags = soup.select('title')
        tt = tags[0].text.strip(' \t\r\n')
        logging.info(u'{}'.format(tt))
        logging.info(u'{}'.format(url)) 

        page_list =re.findall(r"(https://sale.jd.com/act/\w+.html)" ,resp.text)
        page_list = list(set(page_list))
        coupon_list = re.findall(r"(https://coupon.jd.com/\S+.html)" ,resp.text)
        coupon_list = list(set(coupon_list))
        return page_list, coupon_list

    def click_list(self, coupon_list):
        for coupon_link in coupon_list:
            coupon_link = coupon_link.replace('&amp;','&') 
            self.click(coupon_link, logging.WARNING)
            logging.warning(coupon_link)    

def search_task(jd, page_list, id):
    logging.critical(u'进程{}:开始运行'.format(id+1))
    page_cnt = 0
    coupon_cnt = 0
    local_page_list = []
    for page_url in page_list:
        pages, coupons = jd.search_page(page_url)
        jd.click_list(coupons)
        coupon_cnt += len(coupons)
        local_page_list += pages
    local_page_list = list(set(local_page_list))
    for page_url in local_page_list:
        if page_url in page_list:
            continue
        pages, coupons = jd.search_page(page_url)
        jd.click_list(coupons)
        coupon_cnt += len(coupons)
    logging.critical(u'进程{}:完成任务'.format(id+1))
    return len(local_page_list), coupon_cnt

def main_task(jd, url):
    page_cnt = 0
    coupon_cnt = 0    
    pages, coupons = jd.search_page(url)
    jd.click_list(coupons)
    page_cnt += len(pages)
    coupon_cnt += len(coupons)
    pool = multiprocessing.Pool(processes=len(pages)+1)
    result = []
    for i in range(len(pages)):
        result.append(pool.apply_async(search_task, args=(jd, [pages[i]], i,)))
    pool.close()
    pool.join()
    for res in result:
        pp, cc = res.get()
        page_cnt += pp
        coupon_cnt += cc
    logging.info(u'找到{}个网页'.format(page_cnt))
    logging.info(u'找到{}个优惠券'.format(coupon_cnt))

def wait_task(jd, url, target, delay):
    jd.set_local_time()
    prev = jd.get_local_time()
    ph = prev / 3600
    while (1):
        curr = jd.get_local_time()
        ch = curr / 3600
        if ch != ph:
            if ph == target:
                break;
            ph = ch
            jd.set_local_time()
        try:
            resp = jd.sess.get(url)
        except Exception, e:
            pass
        time.sleep(delay)
    current = jd.get_local_time()
    m, s = divmod(current, 60)
    h, m = divmod(m, 60)
    logging.warning(u'#开始时间 {:0>2}:{:0>2}:{:0>2} #目标时间 {:0>2}:{:0>2}:{:0>2}'.format(h, m, s, target+1, 0, 0))
            
if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and click coupon')
    parser.add_argument('-u', '--url', 
                        help='Entry URL', required=True)
    parser.add_argument('-hh', '--hour', 
                        type=int, help='Target hour, 0...23', default=None)
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

    if options.hour == None:
        main_task(jd, options.url)
    else:
        target = options.hour - 1
        if target < 0:
            target += 24
        wait_task(jd, options.url, target, 1)
        main_task(jd, options.url)
