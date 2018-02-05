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
import logging, logging.handlers
import argparse
from jd_wrapper import JDWrapper
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# get function name
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

class JDSign(JDWrapper):
    '''
    This class is used to sign
    '''
    def sign_shop(self, filename):
        shop_list = []
        uf_url = 'http://t.jd.com/follow/vender/unfollow.do?venderId='
        logging.info(u'签到京东店铺')
        file = open(filename)
        for line in file:
            shop_list.append(line)
        for sign_url in shop_list:
            try:
                resp = self.sess.get(sign_url)
                if resp.status_code != requests.codes.OK:
                    logging.error('Failed to get {}'.format(sign_url))
                pattern = re.compile(r'"everyday-area J_everyday_area (?P<award>.*?)"')
                res = pattern.search(resp.text)
                if res == None:
                    logging.warning(u'{}没有找到award'.format(sign_url))
                else:
                    award = res.group('award')
                    logging.warning(u'领取结果：{}'.format(award))
            except Exception as e:
                logging.error('Exp {0} : {1}'.format(FuncName(), e))
            pattern = re.compile(r'(?P<shop>\d+)')
            res = pattern.search(sign_url)
            if res != None:
                url  = uf_url + res.group('shop')
                try:
                    self.sess.get(url)
                except Exception as e:
                    logging.error('Exp {0} : {1}'.format(FuncName(), e))

if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and search shop')
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

    jd = JDSign()
    if not jd.pc_login():
        sys.exit(1)
    jd.sign_shop(options.coupon_file)
