# -*- coding: utf-8 -*-

import bs4
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import os
import time
import datetime
import json
import random
import math
import logging, logging.handlers
import argparse
import multiprocessing
from jd_wrapper import JDWrapper
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# get function name
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

class JDCoupon(JDWrapper):
    '''
    This class used to click JD coupon
    '''
    delta_time = None

    def set_local_time(self):
        logging.warning(u'开始校准系统时间')
        for i in range(3):
            ttime = self.get_network_time()
            stime = time.time()
            if (ttime != None):
                break;
        if (ttime == None):
            logging.warning(u'无法获取网络时间！！！')
            return
        self.delta_time = ttime - stime
        logging.warning(u'系统时间差为{}秒'.format(self.delta_time))

    def get_local_time(self):
        if self.delta_time != None:
            return time.time() + self.delta_time
        else:
            logging.error(u'本地时间没有校准！！！')
            return time.time()
    
    def format_local_time(self):
        ttime = time.localtime(self.get_local_time())
        return ttime.tm_hour, ttime.tm_min, ttime.tm_sec

    def click(self, url, level=None):
        try:
            resp = self.sess.get(url)
            if level != None:
                soup = bs4.BeautifulSoup(resp.text, "html.parser")
                tag1 = soup.select('title')
                tag2 = soup.select('div.content')
                if len(tag2):
                    logging.log(level, u'{}'.format(tag2[0].text.strip(' \t\r\n')))
                else:
                    if len(tag1):
                        logging.log(level, u'{}'.format(tag1[0].text.strip(' \t\r\n')))
                    else:
                        logging.log(level, u'页面错误')
        except Exception, e:
            if level != None:
                logging.log(level, 'Exp {0} : {1}'.format(FuncName(), e))
            return 0
        else:
            return 1

    def compare_local_time(self, target):
        one_day = 86400.0; # 24 * 60 *60
        local_time = self.get_local_time()
        fraction = local_time - math.floor(local_time)
        ttime = time.localtime(local_time)
        current = (ttime.tm_hour * 3600) + (ttime.tm_min * 60) + ttime.tm_sec + fraction
        if target < current:
            target += one_day
        return target - current
    
    def click_wait(self, url, target, delay):
        self.set_local_time()
        while 1:
            self.click(url, logging.INFO)
            diff = self.compare_local_time(target)
            if (diff <= 50) and (diff >= -50):
                break;
            time.sleep(delay)
        return 1

def click_task(jd, url, target, id):    
    cnt = 0
    logging.warning(u'进程{}:开始运行'.format(id+1))
    while(1):
        if (run_flag.value == 0):
            return 0
        diff = jd.compare_local_time(target)
        if (diff <= 10):
            break;
    while(run_flag.value != 0):
        cnt = cnt + jd.click(url, None)
    jd.click(url, logging.WARNING)
    return cnt

if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and click coupon')
    parser.add_argument('-u', '--url', 
                        help='Coupon URL', required=True)
    parser.add_argument('-hh', '--hour', 
                        type=int, help='Target hour', default=10)
    parser.add_argument('-m', '--minute', 
                        type=int, help='Target minute', default=0)
    parser.add_argument('-d', '--duration', 
                        type=int, help='Duration in minutes', default=24*60)
    parser.add_argument('-p', '--process', 
                        type=int, help='Number of processes', default=1)
    parser.add_argument('-l', '--log', 
                        help='Log file', default=None)

    options = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - (%(levelname)s) %(message)s', datefmt='%H:%M:%S')  
    if (options.log != None):
        log_hdl = logging.FileHandler(options.log,"w")  
        log_hdl.setLevel(logging.WARNING)
        log_fmt = logging.Formatter("%(asctime)s - %(message)s", '%H:%M:%S')  
        log_hdl.setFormatter(log_fmt)  
        logging.getLogger('').addHandler(log_hdl)
    jd = JDCoupon()
    if not jd.login_by_QR():
        sys.exit(1)
    jd.click(options.url, logging.WARNING)
    target = (options.hour * 3600) + (options.minute * 60)
    if (0 == jd.click_wait(options.url, target, 5)):
        sys.exit(1)
    jd.click(options.url, logging.WARNING)
    run_flag = multiprocessing.Value('i', 0)
    pool = multiprocessing.Pool(processes=options.process+1)
    result = []
    h, m, s = jd.format_local_time()
    logging.warning(u'#开始时间 {:0>2}:{:0>2}:{:0>2} #目标时间 {:0>2}:{:0>2}:{:0>2}'.format(h, m, s, options.hour, options.minute, 0))
    run_flag.value = 1
    for i in range(options.process):
        result.append(pool.apply_async(click_task, args=(jd, options.url, target, i,)))
    time.sleep(options.duration * 60)
    h, m, s = jd.format_local_time()
    logging.warning(u'#结束时间 {:0>2}:{:0>2}:{:0>2} #目标时间 {:0>2}:{:0>2}:{:0>2}'.format(h, m, s, options.hour, options.minute, 0))
    run_flag.value = 0
    pool.close()
    pool.join()
    cnt = 0
    for res in result:
        cnt += res.get()
    logging.warning(u'运行{}分钟，点击{}次'.format(options.duration, cnt))
