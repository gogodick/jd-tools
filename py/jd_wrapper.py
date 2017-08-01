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
import cookielib
import os
import time
import re
import math
import json
import random
import logging, logging.handlers
import subprocess
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
    mobile_cookie_file = "mobile_cookie.dat"
    pc_cookie_file = "pc_cookie.dat"
    def __init__(self):
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

    def get_network_time(self):
        try:
            data = {'r': random.random()}
            headers = {'Referer': 'http://a.jd.com/'}
            resp = self.sess.get('http://a.jd.com/ajax/queryServerData.html', params=data, headers=headers)
            as_json = resp.json()
        except Exception, e:
            logging.warning('Exp {0} : {1}'.format(FuncName(), e))
            return None
        else:
            return as_json['serverTime'] / 1000.0

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

    def save_cookie(self, filename):
        try:
            for ck in self.sess.cookies:
                if ck.expires == None:
                    ck.expires = int(time.time()) + 3600 * 24
            self.sess.cookies.save(filename, ignore_discard=True)
            return True
        except Exception, e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def load_cookie(self, filename):
        try:
            load_cookiejar = cookielib.MozillaCookieJar()
            try:
                load_cookiejar.load(filename, ignore_discard=True)
            except:
                pass
            self.sess.cookies = load_cookiejar
            return True
        except Exception, e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def open_image(self, filename):
        system_text = platform.system()
        handle = None
        if 'Linux' in system_text:
            handle = subprocess.Popen('eog ' + filename)
        elif 'CYGWIN' in system_text:
            os.system('explorer ' + filename)
            for i in range(10):
                task_list = os.popen("tasklist").read()
                pattern = re.compile(r'dllhost.exe(?P<pid>.*)Console')
                res = pattern.search(task_list)
                if res != None:
                    handle = int(res.group('pid'))
                    break;
                time.sleep(0.1)
        else:
            logging.error("Does not support this platform: "+system_text)
            sys.exit(1)
        return handle

    def close_image(self, handle):
        system_text = platform.system()
        if 'Linux' in system_text:
            handle.terminate()
        elif 'CYGWIN' in system_text:
            os.system("taskkill /PID " + str(handle))
        else:
            logging.error("Does not support this platform: "+system_text)
            sys.exit(1)

    def pc_login_by_QR(self):
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
            image_file = 'pc_qr.png'
            with open (image_file, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    f.write(chunk)
            
            ## scan QR code with phone
            image_handle = self.open_image(image_file)

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
            
            self.close_image(image_handle)
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

    def pc_login(self):
        self.sess.cookies.clear()
        if self.load_cookie(self.pc_cookie_file):
            if self.pc_verify_login():
                return True
        self.sess.cookies.clear()
        if not self.pc_login_by_QR():
            return False
        self.save_cookie(self.pc_cookie_file)
        return True
    
    def pc_verify_login(self):
        url = "https://vip.jd.com/member/myJingBean/index.html"
        try:
            resp = self.sess.get(url, allow_redirects=False)
            if resp.status_code != requests.codes.OK:
                return False
            if resp.is_redirect and 'passport' in resp.headers['Location']:
                return False
            else:
                soup = bs4.BeautifulSoup(resp.text, "html.parser")
                tags = soup.select('p.bean-total-num')
                logging.warning(u'账户有{}'.format(tags[0].text.strip(' \t\r\n')))
                return True
        except Exception, e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def hash33(self, t):
        e = 0
        for i in range(len(t)):
            e+=(e<<5)+ord(t[i])
        return 2147483647&e

    def g_tk(self):
        h = 5381
        cookies = self.sess.cookies
        s = ''
        for ck in self.sess.cookies:
            if ck.name == 'skey':
                s = ck.value
                break
            if ck.name == 'p_skey':
                s = ck.value
                break
        for c in s:
            h += (h << 5) + ord(c)
        return h & 0x7fffffff

    def mobile_verify_login(self):
        url = "https://home.m.jd.com/wallet/wallet.action"
        try:
            resp = self.sess.get(url, allow_redirects=False)
            if resp.status_code != requests.codes.OK:
                print resp.status_code
                return False
            if resp.is_redirect and 'passport' in resp.headers['Location']:
                print resp.headers
                return False
            else:
                soup = bs4.BeautifulSoup(resp.text, "html.parser")
                tags = soup.select('div.jingdou-num')
                info = tags[0].text.strip(' \t\r\n')
                if len(info) == 0:
                    return False
                logging.warning(u'账户有{}'.format(info))
                return True
        except Exception, e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_login_by_QR(self):
        try:
            logging.warning('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            logging.warning(u'{0} > 请打开QQ手机客户端，准备扫码登陆:'.format(time.ctime()))
            resp = self.sess.get("https://plogin.m.jd.com/cgi-bin/m/qqlogin",
                params = {
                    'appid': 100,
                    'returnurl': 'https://m.jd.com'
                }
            )
            if resp.status_code != requests.codes.OK:
                return False
            pattern = re.compile(r'client_id=(?P<client_id>.*)&redirect_uri=(?P<redirect_uri>.*)&state=(?P<state>.*)')
            res = pattern.search(resp.url)
            if res == None:
                logging.error(u'无法匹配URL')
                return False
            logging.warning(u'{}: {} : {}'.format(res.group('client_id'), res.group('redirect_uri'), res.group('state')))
            client_id = res.group('client_id')
            redirect_uri = res.group('redirect_uri')
            redirect_uri = redirect_uri.replace('%3A',':')
            redirect_uri = redirect_uri.replace('%2F','/')
            redirect_uri = redirect_uri.replace('%3F','?')
            redirect_uri = redirect_uri.replace('%3D','=')
            state = res.group('state')
             
            resp = self.sess.get(
                "https://ssl.ptlogin2.qq.com/ptqrshow",
                params = {
                    'appid': 716027609,
                    'e': 2,
                    'l': 'M',
                    's':3,
                    'd':72,
                    'v':4
                }
            )
            if resp.status_code != requests.codes.OK:
                return False
            image_file = 'mobile_qr.png'
            with open (image_file, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    f.write(chunk)
            ## scan QR code with phone
            image_handle = self.open_image(image_file)
             
            pattern = re.compile(r'\(\'(?P<status>\d+)\',\'.*\',\'.*\',\'(?P<info>.*)\',')
            # check if QR code scanned
            qr_ticket = None
            retry_times = 100
            qrsig = ''
            for ck in self.sess.cookies:
                if ck.name == 'qrsig':
                    qrsig = ck.value
                    break
            while retry_times:
                retry_times -= 1
                resp = self.sess.get("https://ssl.ptlogin2.qq.com/ptqrlogin",
                    params = {
                        'u1': 'https://graph.qq.com/oauth/login_jump',
                        'ptqrtoken': self.hash33(qrsig),
                        'ptredirect': 0,
                        'h': 1,
                        't': 1,
                        'g': 1,
                        'from_ui': 1,
                        'ptlang': 2052,
                        'action': 0-0-1498546581374,
                        'js_ver': 10222,
                        'js_type': 1,
                        'login_sig': '',
                        'pt_uistyle': 40,
                        'aid': 716027609,
                        'daid': 383,
                        'pt_3rd_aid': 100273020
                    }
                )
                if resp.status_code != requests.codes.OK:
                    logging.error(u'访问失败')
                    break
                res = pattern.search(resp.text)
                if res == None:
                    logging.error(u'无法匹配返回页面')
                    break
                logging.warning(u'{} : {}'.format(res.group('status'), res.group('info')))
                if res.group('status') == '0':
                    qr_ticket = res.group('status')
                    break;
                elif res.group('status') == '65':
                    break;
                time.sleep(3)

            self.close_image(image_handle)
            data = {
                'response_type': 'code',
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'state': state,
                'src': '1',
                'g_tk': str(self.g_tk()),
                'auth_time': int(time.time())
            }
            
            resp = self.sess.post('https://graph.qq.com/oauth2.0/authorize', data=data)
            if 'jd.com' not in resp.url:
                logging.error('通过 QQ 登录京东失败.')
                return False
            logging.warning('通过 QQ 登录京东成功.')        
            return True
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_login(self):
	self.sess.cookies.clear()
        if self.load_cookie(self.mobile_cookie_file):
            if self.mobile_verify_login():
                return True
        self.sess.cookies.clear()
        if not self.mobile_login_by_QR():
            return False
        self.save_cookie(self.mobile_cookie_file)
        return True

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - (%(levelname)s) %(message)s', datefmt='%H:%M:%S')
    jd = JDWrapper()
    if not jd.pc_login():
        sys.exit(1)
    if not jd.mobile_login():
        sys.exit(1)
