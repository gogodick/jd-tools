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
    def pc_sign_vip(self):
        index_url = 'https://vip.jd.com'
        sign_url = 'https://vip.jd.com/common/signin.html'

        logging.info(u'签到京东会员')
        try:
            html = self.sess.get(index_url).text
            pattern = re.compile(r'token: "(?P<token>\d+)"')
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

    def pc_sign_finance(self):
        index_url = 'https://jr.jd.com'
        sign_url = 'https://jrai.jd.com/index/vip-user/sign'

        logging.info(u'签到京东金融')
        try:
            headers = {'Referer': index_url}
            response = self.sess.get(sign_url, headers=headers)
            as_json = response.json()
            if 'data' in as_json:
                if 'signData' in as_json['data']:
                    if 'isSuccess' in as_json['data']['signData']:
                        num = as_json['data']['signData']['thisAmount']
                        logging.info(u'签到成功, 获得 {} 个京豆.'.format(num))
                        return True
                    else:
                        num = as_json['data']['signData']['accountBalance']
                        logging.error(u'今日已签到: 账户有{}个钢蹦'.format(num))
                        return False
            print as_json
            return False
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def pick_poker(self):
        try:
            poker_url = 'http://api.m.jd.com/client.action?functionId=getCardResult&client=ld&clientVersion=1.0.0&body={"index":'
            poker_to_pick = random.randint(1, 6)
            poker_url += str(poker_to_pick)
            poker_url += '}'
            headers = {'Referer': "http://bean.m.jd.com/"}
            resp = self.sess.get(poker_url)
            pick_success = False
            as_json = resp.json()
            pick_success = not as_json['code']
            if 'data' in as_json:
                message = as_json['data']['signText']
                award = as_json['data']['signAward']
                message = message.replace(u'signAward', award)
                logging.info('翻牌成功: {}; Message: {}'.format(pick_success, message))
            return pick_success
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_bean(self):
        sign_url = 'http://api.m.jd.com/client.action?functionId=signBeanStart&client=ld&clientVersion=1.0.0'
        logging.info(u'签到京东客户端')
        try:
            resp = self.sess.get(sign_url)
            sign_success = False
            if resp.ok:
                as_json = resp.json()
                sign_success = (as_json['data']['status'] == 1)
                message = as_json['data']['signShowBean']['signText']
                award = as_json['data']['signShowBean']['signAward']
                message = message.replace(u'signAward', award)
                logging.info('签到成功: {}; Message: {}'.format(sign_success, message))
                # "complated": 原文如此, 服务端的拼写错误...
                poker_picked = as_json['data']['signShowBean']['complated']
                if not poker_picked:
                    self.pick_poker()
            else:
                logging.error('签到失败: Status code: {}; Reason: {}'.format(resp.status_code, resp.reason))
            return sign_success
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_gb(self):
        sign_url = 'https://ms.jr.jd.com/gw/generic/base/h5/m/baseSignInEncrypt'
        logging.info(u'签到京东客户端钢蹦')
        try:
            payload = {
                'reqData': '{}',
                'source': 'jrm'
            }
            resp = self.sess.post(sign_url, data=payload)
            as_json = resp.json()
            if 'resultData' in as_json:
                result_data = as_json['resultData']
                sign_success = result_data['isSuccess']
                message = result_data['showMsg']
                # 参见 daka_app_min.js, 第 1893 行
                continuity_days = result_data['continuityDays']
                if continuity_days > 1:
                    message += '; 签到天数: {}'.format(continuity_days)
            else:
                sign_success = False
                message = as_json.get('resultMsg') or as_json.get('resultMessage')
            logging.info('打卡成功: {}; Message: {}'.format(sign_success, message))
            return sign_success
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_j9(self):
        sign_url = 'http://ms.jr.jd.com/newjrmactivity/base/appdownload/lottery.action'
        logging.info(u'签到9月每天领京豆')
        try:
            sid = ''
            for ck in self.sess.cookies:
                if ck.name == 'sid':
                    sid = ck.value
                    break
            data = {
                'sid': sid,
            }
            response = self.sess.get(sign_url, params=data)
            if response.status_code == requests.codes.OK:
                as_json = response.json()
                if 'status' in as_json and as_json['status'] == 0:
                    logging.info('获得京豆: {}; Message: {}'.format(as_json['count'], as_json['resultMsg']))
                else:
                    logging.info('今日已经领取过; Message: {}'.format(as_json['resultMsg']))
            else:
                logging.error('签到失败: Status code: {}; Reason: {}'.format(response.status_code, response.reason))
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_redpacket(self):
        sign_url = 'https://ms.jr.jd.com/gw/generic/activity/h5/m/receiveZhiBoXjkRedPacket'
        logging.info(u'签到京东直播红包')
        try:
            # 参见 red_packet_index.js
            payload = {
                'reqData': '{"activityCode":"ying_yong_bao_618"}',
            }
            response = self.sess.post(sign_url, data=payload).json()
            if response['resultCode'] == 0:
                sign_success = response['resultData']['success']
                if sign_success:
                    logging.info('领取成功, 获得 {} 元.'.format(response['resultData']['data']))
                else:
                    message = response['resultData'].get('msg') or response.get('resultMsg')
                    logging.info('领取结果: {}'.format(message))
                    if response['resultData'].get('code') == '03':
                        # 当 code 为 03 时, 表示今天已领过了, 因为领取前无法知道是否领过, 此处也当做任务成功返回
                        sign_success = True
                return sign_success
            else:
                message = response.get('resultMsg')
                logging.error('领取失败: {}'.format(message))
                return False
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_cash(self):
        sign_url = 'http://wyyl.jd.com/xjk/receiveReward'
        logging.info(u'签到京东现金红包')
        try:
            sid = ''
            for ck in self.sess.cookies:
                if ck.name == 'sid':
                    sid = ck.value
                    break
            data = {
                'sid': sid,
            }
            response = self.sess.post(sign_url, data=data).json()
            message = response.get('message')
            if response['code'] == 0:
                logging.info('领取成功, 获得 {} 元.'.format(message))
                return True
            else:
                logging.error('领取失败: {}'.format(message))
                return False
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - (%(levelname)s) %(message)s', datefmt='%H:%M:%S')  

    jd = JDSign()
    func_list = dir(jd)
    if not jd.pc_login():
        sys.exit(1)
    for func in func_list:
        if func.find('pc_sign') == 0:
            jd.__getattribute__(func)()
    if not jd.mobile_login():
        sys.exit(1)
    for func in func_list:
        if func.find('mobile_sign') == 0:
            jd.__getattribute__(func)()
