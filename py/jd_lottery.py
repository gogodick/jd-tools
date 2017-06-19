# -*- coding: utf-8 -*-

import bs4
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import os
import time
import datetime
import json
import re
import random
import math
import logging, logging.handlers
import argparse
from jd_wrapper import JDWrapper
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# get function name
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

class JDLottery(JDWrapper):
    '''
    This class used for JD lottery
    '''
    def check_file(self, filename):
        file = open(filename)
        pattern = re.compile(r'(?P<code>.*),(?P<url>.*)')
        for line in file:
            res = pattern.search(line)
            if res == None:
                continue
            if len(res.group('code')) == 0:
                continue
            prize_list = self.check_lottery(res.group('code'))
            if len(prize_list) > 0:
                logging.warning(res.group('code'))
                logging.warning(res.group('url'))
                for [windate, prizename] in prize_list:
                    logging.warning(u'{}, {}'.format(windate, prizename))
        file.close()

    def check_lottery(self, lotterycode):
        prize_list = []
        headers = {'referer': u'http://ls.activity.jd.com/lotteryApi/getWinnerList.action?lotteryCode=' + lotterycode}
        getwater = requests.get('http://ls.activity.jd.com/lotteryApi/getWinnerList.action?lotteryCode=' + lotterycode,
                                headers=headers, verify=False).text
        for each in re.findall('{"prizeName":(.*?)}', getwater, re.S):
            prizename = re.findall('"(.*?)","userPin', each, re.S)[0]
            windate = re.findall('"winDate":"(.*?)"', each, re.S)[0]
            prize_list.append([windate, prizename])
        return prize_list

if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and click coupon')
    parser.add_argument('-f', '--file', 
                        help='Lottery file', default=None)
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
    jd = JDLottery()
    if options.file != None:
        jd.check_file(options.file)
