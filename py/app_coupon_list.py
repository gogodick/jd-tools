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
list_url = 'https://api.m.jd.com/client.action?functionId=selectCouponList&clientVersion=6.4.0&client=android&uuid=357755070126840-e458b88e8e4c&st=1506136940474&sign=cb517e79176dd1e5841f69eb5ad8dac7&sv=112&body={"deliveryId":"368","pageNum":1,"pageSize":10,"showIds":""}'
coupon_url = 'https://api.m.jd.com/client.action?functionId=receiveRvcCoupon&clientVersion=6.4.0&client=android&uuid=357755070126840-e458b88e8e4c&st=1506153297956&sign=77de5316299a59e31c9e1018d134c215&sv=112&body={"extend":"0271DFD6890D3B60ACB8BA8A9E49BEB1BB0B558C96AD56812B4F52B2D5C63807D3E319EF5DF35511AC506FA80234E3DB3A7D8D52B0DFC0199B0168D79BED7E4EC5BA9EFBDF9B0DE7211E3556781CC4526F5EDD73C0BA84030EA8E6592A7F3FA7","source":"couponCenter","rcType":"1"}'
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - (%(levelname)s) %(message)s', datefmt='%H:%M:%S')  
    jd = JDWrapper()
    try:
        resp = jd.sess.post(list_url)
        pattern = re.compile(r'"limitStr":"(?P<limitStr>.*?)","startTime":"(?P<startTime>.*?)".*?,"receiveKey":"(?P<receiveKey>\w+)"')
        res = pattern.findall(resp.text)
        if len(res) > 0:
            print u'找到{}个优惠券'.format(len(res))
            print '########################################################'
        for i in range(len(res)):
            print res[i][0]
            print res[i][1]
            print 'RKey="'+res[i][2]+'"'
            print '########################################################'
    except Exception as e:
        logging.warning('Exp: {}'.format(e))
