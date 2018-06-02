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
    wait_interval = 1
    wait_delay = 30
    duration = 1
    start_limit = 0.5
    coupon_url = ""
    def setup(self, key, role_id):
        try:
            data = {
                'key': key, 
                'roleId': role_id, 
            } 
            resp = self.sess.get('http://coupon.m.jd.com/coupons/show.action', params = data)
            if resp.status_code != requests.codes.OK:
                return False
            url = 'http://coupon.m.jd.com/coupons/submit.json'
            soup = bs4.BeautifulSoup(resp.text, "html.parser")
            tags = soup.select('input#sid')
            if len(tags) != 0:
                url += '?sid='
                url += str(tags[0]['value'])
            tags = soup.select('input#codeKey')
            if len(tags) != 0:
                url += '&codeKey='
                url += str(tags[0]['value'])
            tags = soup.select('input#validateCodeSign')
            if len(tags) != 0:
                url += '&validateCode='
                url += str(tags[0]['value'])
            tags = soup.select('input#roleId')
            if len(tags) != 0:
                url += '&roleId='
                url += str(tags[0]['value'])
            tags = soup.select('input#key')
            if len(tags) != 0:
                url += '&key='
                url += str(tags[0]['value'])
            tags = soup.select('input#couponKey')
            if len(tags) != 0:
                url += '&couponKey='
                url += str(tags[0]['value'])
            tags = soup.select('input#activeId')
            if len(tags) != 0:
                url += '&activeId='
                url += str(tags[0]['value'])
            tags = soup.select('input#couponType')
            if len(tags) != 0:
                url += '&couponType='
                url += str(tags[0]['value'])
            self.coupon_url = url
            return True
        except Exception, e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False
    
    def click(self, level=None):
        try:
            resp = self.sess.get(self.coupon_url, timeout=5)
            if not resp.ok:
                return 0
            if level != None:
                as_json = resp.json()
                logging.log(level, u'{}'.format(self.dump_json(as_json)))
        except Exception, e:
            if level != None:
                logging.log(level, 'Exp {0} : {1}'.format(FuncName(), e))
            return 0
        else:
            return 1

    def click_fast(self, count):
        try:
            return [self.sess.head(self.coupon_url, timeout=0.2) for i in range(count)]
        except Exception, e:
            return []

    def relax_wait(self, target):
        counter = 0
        self.set_local_time()
        while 1:
            if counter >= self.wait_delay:
                self.click(logging.INFO)
                counter = 0
            diff = self.compare_local_time(target)
            if (diff <= 60) and (diff >= -60):
                break;
            time.sleep(self.wait_interval)
            counter += self.wait_interval

    def busy_wait(self, target):
        self.set_local_time()
        while 1:
            diff = self.compare_local_time(target)
            if (diff <= self.start_limit):
                break;

def click_task(coupon_url, id):    
    cnt = 0
    jd = JDCoupon()
    logging.warning(u'进程{}:开始运行'.format(id+1))
    if not jd.load_cookie(jd.mobile_cookie_file):
        logging.warning(u'进程{}:无法加载cookie'.format(id+1))
        return 0
    jd.coupon_url = coupon_url
    while(wait_flag.value != 0):
        pass
    result = []
    while(run_flag.value != 0):
        result += jd.click_fast(8)
    jd.click(logging.WARNING)
    for resp in result:
        if resp.ok:
            cnt += 1
    return cnt

if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and click coupon')
    parser.add_argument('-u', '--url', 
                        help='Coupon URL', default="")
    parser.add_argument('-k', '--key', 
                        help='Coupon key', required=True)
    parser.add_argument('-r', '--role_id', 
                        help='Coupon role id', required=True)
    parser.add_argument('-hh', '--hour', 
                        type=int, help='Target hour', default=10)
    parser.add_argument('-m', '--minute', 
                        type=int, help='Target minute', default=0)
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
    if not jd.mobile_login():
        sys.exit(1)
    if len(options.url) > 0:
        jd.coupon_url = options.url
    elif not jd.setup(options.key, options.role_id):
        sys.exit(1)
    jd.click(logging.WARNING)
    target = (options.hour * 3600) + (options.minute * 60)
    jd.relax_wait(target)
    jd.click(logging.WARNING)
    wait_flag = multiprocessing.Value('i', 0)
    run_flag = multiprocessing.Value('i', 0)
    pool = multiprocessing.Pool(processes=options.process+1)
    result = []
    h, m, s = jd.format_local_time()
    logging.warning(u'#开始时间 {:0>2}:{:0>2}:{:0>2} #目标时间 {:0>2}:{:0>2}:{:0>2}'.format(h, m, s, options.hour, options.minute, 0))
    wait_flag.value = 1
    run_flag.value = 1
    for i in range(options.process):
        result.append(pool.apply_async(click_task, args=(jd.coupon_url, i,)))
    jd.busy_wait(target)
    wait_flag.value = 0
    run_time = jd.duration
    time.sleep(run_time)
    h, m, s = jd.format_local_time()
    logging.warning(u'#结束时间 {:0>2}:{:0>2}:{:0>2} #目标时间 {:0>2}:{:0>2}:{:0>2}'.format(h, m, s, options.hour, options.minute, 0))
    run_flag.value = 0
    pool.close()
    pool.join()
    cnt = 0
    for res in result:
        cnt += res.get()
    logging.warning(u'运行{}秒，点击{}次'.format(run_time, cnt))
