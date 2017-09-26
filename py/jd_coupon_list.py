# -*- coding: utf-8 -*-

import bs4
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import os
import re
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

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - (%(levelname)s) %(message)s', datefmt='%H:%M:%S')  

    jd = JDWrapper()
    try:
        data = {'r': random.random()}
        headers = {'Referer': 'http://a.jd.com/'}
        resp = jd.sess.get('http://a.jd.com/ajax/queryServerData.html', params=data, headers=headers)
        as_json = resp.json()
        rand_str = str(int(math.floor(1e7 * random.random())))
        data = {
            'callback': 'jQuery'+rand_str,
            'catalogId': 0,
            'page': 1,
            'pageSize': 24,
            '_' : str(as_json['serverTime']),
        }
        resp = jd.sess.get('http://a.jd.com/indexAjax/getCouponListByCatalogId.html', params=data, headers=headers)
        pattern = re.compile(r'"key":"(?P<key>\w+)","roleId":"(?P<roleId>\w+)".*?,"limitStr":"(?P<limitStr>.*?)","startTime":"(?P<startTime>.*?)",')
        res = pattern.findall(resp.content)
        if len(res) > 0:
            print u'找到{}个优惠券'.format(len(res))
            print '########################################################'
        for i in range(len(res)):
            print res[i][2]
            print res[i][3]
            print 'KEY="'+res[i][0]+'"'
            print 'ROLEID="'+res[i][1]+'"'
            print '########################################################'
    except Exception as e:
        logging.warning('Exp: {}'.format(e))

