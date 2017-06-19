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
    
    def click_lottery(self, code, level=None):
        headers = {'Referer': 'http://l.activity.jd.com/lottery/lottery_chance.action?lotteryCode='+code}
        lottery_url = 'http://l.activity.jd.com/lottery/lottery_start.action?lotteryCode='+code
        try:
            resp = self.sess.get(lottery_url,headers=headers,timeout=5)
            if level != None:
                prompt = re.findall(u'"promptMsg":"(.*?)"', resp.text, re.S)
                logging.log(level, u'{}'.format(prompt[0]))
        except Exception, e:
            if level != None:
                logging.log(level, 'Exp {0} : {1}'.format(FuncName(), e))
            return 0
        else:
            return 1

    def touch_lottery(self, code, level=None):
        headers = {'Referer': 'http://l.activity.jd.com/lottery/lottery_chance.action?lotteryCode='+code}
        lottery_url = 'http://l.activity.jd.com/lottery/lottery_chance.action?lotteryCode='+code
        try:
            resp = self.sess.get(lottery_url,headers=headers,timeout=5)
            if level != None:
                prompt = re.findall(u'"promptMsg":"(.*?)"', resp.text, re.S)
                logging.log(level, u'{}'.format(prompt[0]))
        except Exception, e:
            if level != None:
                logging.log(level, 'Exp {0} : {1}'.format(FuncName(), e))
            return 0
        else:
            return 1
    
    def relax_wait(self, code, target, delay):
        self.set_local_time()
        while 1:
            self.touch_lottery(code, logging.INFO)
            diff = self.compare_local_time(target)
            if (diff <= 60) and (diff >= -60):
                break;
            time.sleep(delay)
        return

    def busy_wait(self, target):
        self.set_local_time()
        while 1:
            diff = self.compare_local_time(target)
            if (diff <= 0.05):
                break;
        return

if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and click coupon')
    parser.add_argument('-f', '--file', 
                        help='Lottery file', default=None)
    parser.add_argument('-c', '--code', 
                        help='Lottery code', default=None)
    parser.add_argument('-hh', '--hour', 
                        type=int, help='Target hour', default=10)
    parser.add_argument('-m', '--minute', 
                        type=int, help='Target minute', default=0)
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
    elif options.code != None:
        if not jd.login_by_QR():
            sys.exit(1)
        target = (options.hour * 3600) + (options.minute * 60)
        jd.relax_wait(options.code, target, 5)
        jd.busy_wait(target)
        #print jd.get_local_time()
        for i in range(3):
            jd.click_lottery("af555c28-4eaf-4ab4-9f9d-9feb818ce6e5", logging.WARNING)
        #print jd.get_local_time()
    else:
        logging.error(u'命令参数错误！！！')