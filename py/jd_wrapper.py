# -*- coding: utf-8 -*-

"""
JD website helper tool
-----------------------------------------------------
only support to login by QR code, 
"""


import bs4
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import ntplib
import os
import time
import json
import random
import logging, logging.handlers
import platform
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# get function name
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

class JDWrapper(object):
    '''
    This class used to simulate login JD
    '''
    
    def __init__(self):
        # init url related
        self.home = 'https://passport.jd.com/new/login.aspx'
        self.login = 'https://passport.jd.com/uc/loginService'
        self.imag = 'https://authcode.jd.com/verify/image'
        self.auth = 'https://passport.jd.com/uc/showAuthCode'
        
        self.sess = requests.Session()

        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'ContentType': 'text/html; charset=utf-8',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Connection' : 'keep-alive',
        }
        
        self.cookies = {

        }

    @staticmethod
    def print_json(resp_text):
        '''
        format the response content
        '''
        if resp_text[0] == '(':
            resp_text = resp_text[1:-1]
        
        for k,v in json.loads(resp_text).items():
            logging.warning(u'%s : %s' % (k, v))

    @staticmethod
    def response_status(resp):
        if resp.status_code != requests.codes.OK:
            logging.warning('Status: %u, Url: %s' % (resp.status_code, resp.url))
            return False
        return True

    def login_by_QR(self):
        # jd login by QR code
        try:
            logging.warning('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            logging.warning(u'{0} > 请打开京东手机客户端，准备扫码登陆:'.format(time.ctime()))

            urls = (
                'https://passport.jd.com/new/login.aspx',
                'https://qr.m.jd.com/show',
                'https://qr.m.jd.com/check',
                'https://passport.jd.com/uc/qrCodeTicketValidation'
            )

            # step 1: open login page
            resp = self.sess.get(
                urls[0], 
                headers = self.headers
            )
            if resp.status_code != requests.codes.OK:
                logging.warning(u'获取登录页失败: %u' % resp.status_code)
                return False

            ## save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v
            

            # step 2: get QR image
            resp = self.sess.get(
                urls[1], 
                headers = self.headers,
                cookies = self.cookies,
                params = {
                    'appid': 133,
                    'size': 147,
                    't': (long)(time.time() * 1000)
                }
            )
            if resp.status_code != requests.codes.OK:
                logging.warning(u'获取二维码失败: %u' % resp.status_code)
                return False

            ## save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            ## save QR code
            image_file = 'qr.png'
            with open (image_file, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    f.write(chunk)
            
            ## scan QR code with phone
            if 'Linux' in platform.system():
                os.system('eog ' + image_file + '&')
            else:
                os.system('explorer ' + image_file)

            # step 3： check scan result
            ## mush have
            self.headers['Host'] = 'qr.m.jd.com' 
            self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'

            # check if QR code scanned
            qr_ticket = None
            retry_times = 100
            while retry_times:
                retry_times -= 1
                resp = self.sess.get(
                    urls[2],
                    headers = self.headers,
                    cookies = self.cookies,
                    params = {
                        'callback': 'jQuery%u' % random.randint(100000, 999999),
                        'appid': 133,
                        'token': self.cookies['wlfstk_smdl'],
                        '_': (long)(time.time() * 1000)
                    }
                )

                if resp.status_code != requests.codes.OK:
                    continue

                n1 = resp.text.find('(')
                n2 = resp.text.find(')')
                rs = json.loads(resp.text[n1+1:n2])

                if rs['code'] == 200:
                    logging.warning(u'{} : {}'.format(rs['code'], rs['ticket']))
                    qr_ticket = rs['ticket']
                    break
                else:
                    logging.warning(u'{} : {}'.format(rs['code'], rs['msg']))
                    time.sleep(3)
            
            if not qr_ticket:
                logging.warning(u'二维码登陆失败')
                return False
            
            # step 4: validate scan result
            ## must have
            self.headers['Host'] = 'passport.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/uc/login?ltype=logout'
            resp = self.sess.get(
                urls[3], 
                headers = self.headers,
                cookies = self.cookies,
                params = {'t' : qr_ticket },
            )
            if resp.status_code != requests.codes.OK:
                logging.warning(u'二维码登陆校验失败: %u' % resp.status_code)
                return False
            
            ## login succeed
            self.headers['P3P'] = resp.headers.get('P3P')
            for k, v in resp.cookies.items():
                self.cookies[k] = v
            
            logging.warning(u'登陆成功')
            return True
        
        except Exception as e:
            logging.warning('Exp:', e)
            raise

        return False

    def get_network_time(self):
        try:
            client = ntplib.NTPClient()
            response = client.request('ntp2.aliyun.com')
        except Exception, e:
            logging.warning('Exp {0} : {1}'.format(FuncName(), e))
            return None
        else:
            #return response.tx_time + response.delay
            return response.tx_time

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
    
    def compare_local_time(self, target):
        one_day = 86400.0; # 24 * 60 *60
        local_time = self.get_local_time()
        fraction = local_time - math.floor(local_time)
        ttime = time.localtime(local_time)
        current = (ttime.tm_hour * 3600) + (ttime.tm_min * 60) + ttime.tm_sec + fraction
        if target < current:
            target += one_day
        return target - current
