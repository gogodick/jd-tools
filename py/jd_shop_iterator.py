# -*- coding: utf-8 -*-

import bs4
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import os
import time
import datetime
import cookielib
import json
import random
import re
import multiprocessing
import logging, logging.handlers
import argparse
from jd_wrapper import JDWrapper
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# get function name
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

class JDShop(JDWrapper):
    '''
    This class is used to sign
    '''
    pst = 10
    def search_shop_a(self, id, start, stop):
        result = []
        progress = 0
        for i in range(start, stop):
            current = (i-start) * self.pst / (stop - start)
            if (current > progress):
                progress = current
                logging.warning(u'task {}: progress {}%'.format(id, progress*100/self.pst))
            x = i + 1000000000
            sign_url = 'https://mall.jd.com/shopSign-{}.html'.format(x)
            try:
                resp = self.sess.get(sign_url, allow_redirects=False)
                if resp.status_code != requests.codes.OK:
                    continue
                pattern = re.compile(r'"everyday-area J_everyday_area (?P<award>.*?)"')
                res = pattern.search(resp.text)
                if res != None:
                    award = res.group('award')
                    logging.warning(u'shop {}: {}'.format(x, award))
                    result.append(sign_url)
            except Exception as e:
                logging.error('Exp {0} : {1}'.format(FuncName(), e))
        logging.warning(u'task {}: progress 100%'.format(id))
        return result

    def search_shop_b(self, id, start, stop):
        result = []
        progress = 0
        for i in range(start, stop):
            current = (i-start) * self.pst / (stop - start)
            if (current > progress):
                progress = current
                logging.warning(u'task {}: progress {}%'.format(id, progress*100/self.pst))
            sign_url = 'https://mall.jd.com/shopSign-{}.html'.format(i)
            try:
                resp = self.sess.get(sign_url, allow_redirects=False)
                if resp.status_code != requests.codes.OK:
                    continue
                pattern = re.compile(r'"everyday-area J_everyday_area (?P<award>.*?)"')
                res = pattern.search(resp.text)
                if res != None:
                    award = res.group('award')
                    logging.warning(u'shop {}: {}'.format(i, award))
                    result.append(sign_url)
            except Exception as e:
                logging.error('Exp {0} : {1}'.format(FuncName(), e))
        logging.warning(u'task {}: progress 100%'.format(id))
        return result

def shop_task(id, start, stop):    
    cnt = 0
    jd = JDShop()
    logging.warning(u'进程{}:开始运行'.format(id+1))
    if not jd.load_cookie(jd.pc_cookie_file):
        logging.warning(u'进程{}:无法加载cookie'.format(id+1))
        return 0
    return jd.search_shop_a(id+1, start, stop)

def save_shop(shop_list, file_name):
    try:
        f = open(file_name, 'w')
        for k in shop_list:
            str = '{}\n'.format(k)
            f.write(str)
        f.close()
    except Exception as Err:
        logging.error('Exp {0} : {1}'.format(FuncName(), e))

if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and search shop')
    parser.add_argument('-length', '--length', 
                        type=int, help='search length', default=100000)
    parser.add_argument('-p', '--process', 
                        type=int, help='Number of processes', default=10)
    parser.add_argument('-cf', '--coupon_file', 
                        help='Coupon file', default="my_shop.csv")
    parser.add_argument('-log', '--log', 
                        help='Log file', default=None)
    options = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - (%(levelname)s) %(message)s', datefmt='%H:%M:%S')  
    if (options.log != None):
        log_hdl = logging.FileHandler(options.log,"w")  
        log_hdl.setLevel(logging.INFO)
        log_fmt = logging.Formatter('%(asctime)s - (%(levelname)s) %(message)s', '%H:%M:%S')  
        log_hdl.setFormatter(log_fmt)  
        logging.getLogger('').addHandler(log_hdl)

    jd = JDShop()
    if not jd.pc_login():
        sys.exit(1)
    shop_list = []
    result = []
    pool = multiprocessing.Pool(processes=options.process+1)
    step = options.length/options.process
    for i in range(options.process):
        start = i*step
        stop = start+step
        result.append(pool.apply_async(shop_task, args=(i, start, stop,)))
    pool.close()
    pool.join()
    for res in result:
        shop_list += res.get()
    save_shop(shop_list, options.coupon_file)

