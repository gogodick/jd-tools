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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# get function name
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

def task_wrapper(jd, pages, id):
    visited_pages = []
    start = time.time()
    pp, cc, ll = jd.search_pages(visited_pages, pages, 0, id)
    stop = time.time()
    duration = int((stop - start) / 60)
    logging.warning(u'任务{}:结束运行，运行时间为{}分钟'.format(id, duration))
    return pp, cc, ll

class Progress:
    def __init__(self, total = 0):
        self.count = 1
        self.total = total
    def move(self, s):
        logging.info(s + str(int(self.count * 100/self.total)) + '%')
        self.count += 1

class JDCrawler(object):
    '''
    This class used to search JD coupon and lottery
    '''
    sale_patterns = ["(sale.jd.com/act/\S+.html)"]
    coupon_patterns = ["(coupon.jd.com/ilink/\S+.html)"]
    lottery_patterns =  ["lotterycode:'(.*?)'", 'lotterycode=(.*?)"', 'data-code="(.*?)', 'lottNum="(.*?)"']
    visited_pages = []
    lottery_dict = {}
    coupon_dict = {}
    crawler_time_out = 5
    depth_limit = 1
    
    def read_page(self, url):
        try:
            resp = self.sess.get(url, timeout = self.crawler_time_out)
            if resp.status_code != requests.codes.OK:
                return None
        except Exception, e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return None 
        else:
            return resp.text
    
    def search_pages(self, visited_pages, pages, depth, id):
        if depth > self.depth_limit:
            return [], {}, {}
        local_pages = []
        local_pages += visited_pages
        local_coupon_dict = {}
        local_lottery_dict = {}
        progress = Progress(len(pages))
        for page in pages:
            if depth <= 1:
                progress.move(u'任务{}-深度{}:进度为'.format(id, depth))
            if page in local_pages:
                continue
            new_pages = []
            new_coupons = []
            new_lotterys = []
            page_text = self.read_page("https://"+page)
            if page_text == None:
                continue
            for pattern in self.sale_patterns:
                new_pages += re.findall(pattern, page_text)
            for pattern in self.coupon_patterns:
                new_coupons += re.findall(pattern, page_text)
            for pattern in self.lottery_patterns:
                new_lotterys += re.findall(pattern, page_text)
            new_coupons = list(set(new_coupons))
            for coupon in new_coupons:
                if coupon not in local_coupon_dict:
                    local_coupon_dict[coupon] = page
            new_lotterys = list(set(new_lotterys))
            for lottery in new_lotterys:
                if lottery not in local_lottery_dict:
                    local_lottery_dict[lottery] = page    
            new_pages = list(set(new_pages))
            local_pages.append(page)
            pp, cc, ll = self.search_pages(local_pages, new_pages, depth+1, id)
            for p in pp:
                if p not in local_pages:
                    local_pages.append(p)
            for c in cc:
                if c not in local_coupon_dict:
                    local_coupon_dict[c] = cc[c]
            for l in ll:
                if l not in local_lottery_dict:
                    local_lottery_dict[l] = ll[l]
        logging.info(u'任务{}:当前搜索了{}个页面，找到了{}个优惠券，找到了{}个抽奖'.format(id, len(local_pages), len(local_coupon_dict), len(local_lottery_dict)))
        return local_pages, local_coupon_dict, local_lottery_dict

    def split_list(self, l, n):
        length = len(l)
        if n > length:
            n = length
        sz = length // n
        c = length % n
        return map(lambda i: l[i*(sz+1):(i+1)*(sz+1)] if i < c else l[i*sz+c:i*sz+c+sz], range(n))

    def start(self, num):
        self.sess = requests.Session()
        current_url = "https://www.jd.com"
        new_pages = []
        page_text = self.read_page(current_url)
        if page_text == None:
            return
        for pattern in self.sale_patterns:
            new_pages += re.findall(pattern, page_text)
        new_pages = list(set(new_pages))
        page_ll = self.split_list(new_pages, num)
        pool = multiprocessing.Pool(processes=len(page_ll)+1)
        result = []
        for i in range(len(page_ll)):
            result.append(pool.apply_async(task_wrapper, args=(self, page_ll[i], i,)))
        pool.close()
        pool.join()
        for res in result:
            pp, cc, ll = res.get()
            for p in pp:
                if p not in self.visited_pages:
                    self.visited_pages.append(p)
            for c in cc:
                if c not in self.coupon_dict:
                    self.coupon_dict[c] = cc[c]
            for l in ll:
                if l not in self.lottery_dict:
                    self.lottery_dict[l] = ll[l]
        logging.warning(u'总共搜索了{}个页面，找到了{}个优惠券，找到了{}个抽奖'.format(len(self.visited_pages), len(self.coupon_dict), len(self.lottery_dict)))

    def save_coupon(self, file_name):
        try:
            f = open(file_name, 'w')
            for k in self.coupon_dict:
                v = self.coupon_dict[k]
                k = k.replace('&amp;','&')
                str = '{},{}\n'.format(k, v)
                f.write(str)
            f.close()
        except Exception as Err:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))

    def save_lottery(self, file_name):
        try:
            f = open(file_name, 'w')
            for k in self.lottery_dict:
                v = self.lottery_dict[k]
                str = '{},{}\n'.format(k, v)
                f.write(str)
            f.close()
        except Exception as Err:
            logging.error('Exp {0} : {1}'.format(FuncName(), Err))
    
if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and search coupon')
    parser.add_argument('-d', '--depth', 
                        type=int, help='depth limit', default=1)
    parser.add_argument('-p', '--process', 
                        type=int, help='Number of processes', default=1)
    parser.add_argument('-cf', '--coupon_file', 
                        help='Coupon file', default=None)
    parser.add_argument('-lf', '--lottery_file', 
                        help='Lottery file', default=None)
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
    jd.depth_limit = options.depth
    jd.start(options.process)
    if options.coupon_file != None:
        jd.save_coupon(options.coupon_file);
    if options.lottery_file != None:
        jd.save_lottery(options.lottery_file);
