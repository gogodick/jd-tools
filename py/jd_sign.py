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
    def sign_vip(self):
        index_url = 'https://vip.jd.com'
        sign_url = 'https://vip.jd.com/common/signin.html'

        logging.info(u'签到京东会员')
        try:
            html = self.sess.get(index_url).text
            pattern = re.compile(r'pageConfig.token="(?P<token>\d+)"')
            res = pattern.search(html)
            if res == None:
                logging.warning(u'没有找到token');
                return False
            if len(res.group('token')) == 0:
                logging.warning(u'没有找到token');
                return False
            payload = {'token': res.group('token')}
            response = self.sess.get(sign_url, params=payload).json()
            if response['success']:
                # 签到成功, 获得若干个京豆
                beans_get = response['result']['jdnum']
                logging.info(u'签到成功, 获得 {} 个京豆.'.format(beans_get))
                return True
            else:
                # 例如: 您已签到过，请勿重复签到！
                message = response['resultTips']
                logging.error(u'签到失败: {}'.format(message))
                return False
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def sign_finance(self):
        index_url = 'https://vip.jr.jd.com'
        sign_url = 'https://vip.jr.jd.com/newSign/doSign'

        logging.info(u'签到京东金融')
        try:
            headers = {'Referer': index_url}
            response = self.sess.post(sign_url, headers=headers).json()
            message = response['message']
            sign_success = False
            if response['success']:
                sign_result = response['sign']
                sign_success = sign_result['result']
                if sign_success:
                    count = sign_result['num']
                    logging.info(u'签到成功, 获得 {} 个京豆.'.format(count))
                else:
                    logging.error(u'签到失败: {}'.format(message))
            else:
                logging.error(u'签到失败: {}'.format(message))
            return sign_success
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - (%(levelname)s) %(message)s', datefmt='%H:%M:%S')  

    jd = JDSign()
    if not jd.pc_login():
        sys.exit(1)
    func_list = dir(jd)
    for func in func_list:
        if func.find('sign') == 0:
            jd.__getattribute__(func)()
