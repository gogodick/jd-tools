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
import multiprocessing
from jd_wrapper import JDWrapper
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class JDCoupon(JDWrapper):
    '''
    This class used to click JD coupon
    '''
    def click(self, url, level=None):
        try:
            resp = self.sess.get(url)
            if level != None:
                soup = bs4.BeautifulSoup(resp.text, "html.parser")
                tags = soup.select('div.content')
                logging.log(level, u'{}'.format(tags[0].text.strip(' \t\r\n')))
            if resp.status_code != requests.codes.OK:
                return 0
            return 1
        except Exception, e:
            if level != None:
                logging.log(level, 'Exp {0} : {1}'.format(FuncName(), e))
            return 0

    def click_wait(self, url, hour, minute, delay):
        target = (hour * 3600) + (minute * 60)
        for i in range(3):
            ttime = self.get_current_time()
            stime = time.time()
            if (ttime != None):
                break;
        if ttime == None:
            logging.warning(u'获取时间失败')
            return 0
        current = (ttime.tm_hour * 3600) + (ttime.tm_min * 60) + ttime.tm_sec
        delta = int(current - stime)
        logging.warning(u'系统时间差为{}秒'.format(delta))
        if (target < current):
            target = current
        while 1:
            tick = time.time()
            self.click(url, logging.INFO)
            if (tick + delta + 60) >= target:
                break;
            time.sleep(delay)
        current = time.time() + delta
        m, s = divmod(current, 60)
        h, m = divmod(m, 60)
        logging.warning(u'#开始时间 {:0>2}:{:0>2}:{:0>2} #目标时间 {:0>2}:{:0>2}:{:0>2}'.format(int(h), int(m), int(s), hour, minute, 0))
        return 1

def click_thread(jd, url, target, id):    
    cnt = 0
    logging.warning(u'进程{}:开始运行'.format(id+1))
    while(time.time() < target):
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
    if (0 == jd.click_wait(options.url, options.hour, options.minute, 1)):
        sys.exit(1)
    jd.click(options.url, logging.WARNING)
    pool = multiprocessing.Pool(processes=options.process+1)
    result = []
    deadline = time.time() + (options.duration * 60)
    for i in range(options.process):
        result.append(pool.apply_async(click_thread, args=(jd, options.url, deadline, i,)))
    pool.close()
    pool.join()
    cnt = 0
    for res in result:
        cnt += res.get()
    logging.warning(u'运行{}分钟，点击{}次'.format(options.duration, cnt))
