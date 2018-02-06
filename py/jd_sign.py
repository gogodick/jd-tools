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
    def find_key_str(self, text, key):
        str = u'"{}":"(?P<value>.*?)"'.format(key)
        pattern = re.compile(str)
        res = pattern.findall(text)
        return res
    
    def find_key_num(self, text, key):
        str = u'"{}":(?P<value>\d+)'.format(key)
        pattern = re.compile(str)
        res = pattern.findall(text)
        return res

    def pc_sign_vip(self):
        index_url = 'https://vip.jd.com'
        sign_url = 'https://vip.jd.com/common/signin.html'

        logging.info(u'签到京东会员')
        try:
            html = self.sess.get(index_url).text
            pattern = re.compile(r'token: "(?P<token>\d+)"')
            res = pattern.search(html)
            if res == None:
                logging.warning(u'没有找到token')
                return False
            if len(res.group('token')) == 0:
                logging.warning(u'没有找到token')
                return False
            payload = {'token': res.group('token')}
            response = self.sess.get(sign_url, params=payload).json()
            if response['success']:
                # 签到成功, 获得若干个京豆
                if 'jdnum' in response['result']:
                    beans_get = response['result']['jdnum']
                    logging.info(u'签到成功, 获得 {} 个京豆.'.format(beans_get))
                else:
                    logging.warning(u'{}'.format(response))
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

    def mobile_sign_jr(self):
        sign_url = 'http://home.jdpay.com/my/signIn/'
        logging.info(u'签到京东金融')
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
            resp_json = response.json()
            if 'data' in resp_json:
                if 'resBusiData' in resp_json['data']:
                    logging.info('签到成功: {}'.format(resp_json['data']['resBusiData']))
                else:
                    logging.info('签到结果: {}'.format(resp_json['data']['resBusiMsg']))
            else:
                logging.info('无法识别: {}'.format(resp_json))
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_month(self):
        sign_url = 'http://ms.jr.jd.com/newjrmactivity/base/appdownload/lottery.action'
        logging.info(u'签到10月每天领京豆')
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

    '''
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
    '''

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
            if response['code'] == '00':
                logging.info('领取成功, 获得 {} 元.'.format(message))
                return True
            else:
                logging.error('领取失败: {}'.format(message))
                return False
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_wx(self):
        sign_url = 'http://ms.jr.jd.com/newjrmactivity/base/signWX/sign.action'
        logging.info(u'签到京东微信')
        try:
            sid = ''
            for ck in self.sess.cookies:
                if ck.name == 'sid':
                    sid = ck.value
                    break
            data = {
                'sid': sid,
                'openid': 'oOCe-uJOrFc0pHT3r43-pJLy7a40'
            }
            response = self.sess.post(sign_url, data=data)
            resp_json = response.json()
            if resp_json['resultCode'] == 0:
                sign_success = resp_json['resultData']['result']
                if sign_success:
                    logging.info('领取成功, 获得 {} 京豆.'.format(resp_json['resultData']['num']))
                else:
                    message = resp_json['resultData'].get('msg') or resp_json.get('resultMsg')
                    logging.info('领取结果: {}'.format(message))
                    if resp_json['resultData'].get('code') == '03':
                        # 当 code 为 03 时, 表示今天已领过了, 因为领取前无法知道是否领过, 此处也当做任务成功返回
                        sign_success = True
                return sign_success
            else:
                message = resp_json.get('resultMsg')
                logging.error('领取失败: {}'.format(message))
                return False
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_jrdraw(self):
        index_url = 'http://ms.jr.jd.com/gw/generic/activity/h5/m/myRewardsAndLeftTimes1'
        sign_url = 'http://ms.jr.jd.com/gw/generic/activity/h5/m/recieveRewad1'
        logging.info(u'签到京东金融抽奖')
        try:
            sid = ''
            for ck in self.sess.cookies:
                if ck.name == 'sid':
                    sid = ck.value
                    break
            data = {
                'sid': sid,
            }
            response = self.sess.get(index_url, params=data)
            resp_json = response.json()
            left_times = None
            if 'resultData' in resp_json:
                if "data" in resp_json['resultData']:
                    if 'leftTimes' in resp_json['resultData']['data']:
                        left_times = resp_json['resultData']['data']['leftTimes']
            if left_times != None and left_times < 3:
                message = resp_json['resultMsg']
                logging.info('领取结果: {}'.format(message))
                return False
            response = self.sess.get(sign_url, params=data)
            resp_json = response.json()
            if resp_json['resultCode'] == 0:
                sign_success = resp_json['resultData']['success']
                if sign_success:
                    logging.info('领取成功, 获得 {}.'.format(resp_json['resultData']['data']['reward']['rewardName']))
                else:
                    message = resp_json['resultData'].get('msg') or resp_json.get('resultMsg')
                    logging.info('领取结果: {}'.format(message))
                return sign_success
            else:
                message = resp_json.get('resultMsg')
                logging.error('领取失败: {}'.format(message))
                return False
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_bank1(self):
        sign_url = 'https://kx.jd.com/dzp/go'
        logging.info(u'签到京东小金库抽奖')
        try:
            sid = ''
            for ck in self.sess.cookies:
                if ck.name == 'sid':
                    sid = ck.value
                    break
            data = {
                'activityno': '16-131171113162144348162',
                'sid': sid,
            }
            response = self.sess.get(sign_url, params=data)
            pattern = re.compile(r'"success":(?P<success>\w+)')
            res = pattern.search(response.text)
            if res == None:
                logging.warning(u'没有找到success');
                return False
            if res.group('success') == "false":
                pattern = re.compile(r'"msg":"(?P<msg>.*?)"')
                res = pattern.search(response.text)
                if res == None:
                    logging.warning(u'没有找到msg');
                    return False
                message = res.group('msg')
                logging.info('领取结果: {}'.format(message))
                return True
            pattern = re.compile(r'"benefitName":"(?P<benefitName>.*?)"')
            res = pattern.search(response.text)
            if res == None:
                logging.warning(u'没有找到benefitName');
                return False
            logging.info('领取成功, 获得 {}.'.format(res.group('benefitName')))
            return True
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_shake(self):
        sign_url = 'http://ms.jr.jd.com/newjrmactivity/base/shake0801/shake2award.action'
        logging.info(u'签到京东摇一摇')
        try:
            sid = ''
            for ck in self.sess.cookies:
                if ck.name == 'sid':
                    sid = ck.value
                    break
            data = {
                'sid': sid,
            }
            for i in range(3):
                response = self.sess.post(sign_url, data=data)
                resp_json = response.json()
                if resp_json['resultCode'] == 200 and resp_json['status'] == 0:
                    logging.info('领取成功, 获得 {}.'.format(resp_json['name']))
                else:
                    logging.info('领取结果: {}'.format(resp_json['resultMsg']))
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_zdouble(self):
        sign_url = 'http://ljd.m.jd.com/countersign/receiveAward.json'
        logging.info(u'签到京东双签')
        try:
            response = self.sess.get(sign_url)
            resp_json = response.json()
            if 'res' in resp_json and 'data' in resp_json['res']:
                data = resp_json['res']['data'][0]
                logging.info('领取成功: {} {}'.format(data['awardCount'], data['awardName']))
            else:
                logging.info('领取失败: {}'.format(resp_json))
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_lottery(self):
        sign_url = 'http://lottery.jd.com/award/lottery?actKey=a2Ybe2'
        logging.info(u'签到京东抽奖')
        try:
            for i in range(1):
                response = self.sess.get(sign_url)
                resp_json = response.json()
                if 'data' in resp_json:
                    logging.info('领取结果: {} {}'.format(resp_json['msg'], resp_json['data']['awardName']))
                else:
                    logging.info('领取结果: {}'.format(resp_json['msg']))
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_game(self):
        index_url = 'https://gamecenter.m.jd.com/hall/verify'
        sign_url = 'https://gamecenter.m.jd.com/hall/play'
        logging.info(u'签到京东游戏')
        try:
            headers = {'Referer': 'https://gamecenter.m.jd.com'}
            response = self.sess.get(index_url, headers=headers)
            resp_json = response.json()
            if 'valid' in resp_json and resp_json['valid'] == True:
                data = {
                    'token': resp_json['timestamp'],
                }
                response = self.sess.get(sign_url, params=data, headers=headers)
                resp_json = response.json()
                logging.info('领取结果: {}'.format(resp_json))
            else:
                logging.info('领取结果: {}'.format(resp_json['message']))
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def mobile_sign_draw(self):
        sign_url = 'https://s.m.jd.com/activemcenter/muserwelfare/draw?active=Mjiugongge&type=2'
        logging.info(u'签到京东每日抽奖')
        try:
            headers = {'Referer': 'https://wqs.jd.com/promote/201712/mwelfare/m.html?sceneval=2&logintag='}
            response = self.sess.get(sign_url, headers=headers)
            pattern = re.compile(r'"prize":\[(?P<prize>.*)\]')
            res = pattern.search(response.text)
            if res == None:
                logging.warning(u'没有找到prize');
                return False
            prize = res.group('prize')
            pattern = re.compile(r'"retmsg":"(?P<retmsg>.*)"')
            res = pattern.search(response.text)
            if res == None:
                logging.warning(u'没有找到retmsg');
                return False
            retmsg = res.group('retmsg')
            logging.info('领取结果: {} {}'.format(retmsg, prize))
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

    def get_token(self):
        e = ''
        for ck in self.sess.cookies:
            if ck.name == 'wq_skey':
                e = ck.value
                break
        r = len(e)
        a = 5381
        for t in range(r):
            a+=(a<<5)+ord(e[t])
        return a&2147483647

    def mobile_sign_beangame(self):
        sign_url = 'https://wq.jd.com/mlogin/mpage/Login?rurl=http%3A%2F%2Fwqs.jd.com%2Fmy%2Findexv2.shtml%3Fshownav%3D1%26ptag%3D137652.25.3'
        token_url = 'https://wq.jd.com/active/getfunction'
        index_url = 'https://wqs.jd.com/promote/201711/beangame/index.html'
        sp_url = 'https://wq.jd.com/activepersistent/jdbeans/welfaredrawv2'
        out_url = 'https://wq.jd.com/activepersistent/jdbeans/outboxv2'
        in_url = 'https://wq.jd.com/activepersistent/jdbeans/inboxv2'
        logging.info(u'签到京豆培养仓')
        try:
            resp = self.sess.get(sign_url)
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False
        g_tk = self.get_token()
        try:
            data = {
                'g_tk': g_tk,
            }
            resp = self.sess.get(token_url, params=data)
            pattern = re.compile(r'"TOKEN":"(?P<token>.*?)".*a =(?P<a>.*?);')
            res = pattern.search(resp.text)
            if res == None:
                logging.warning(u'没有找到token');
                return False
            token = res.group('token')
            a = res.group('a')
            array = a.split('+')
            array = map(eval, array)
            array = map(str, array)
            promotejs = token + ''.join(array)
            logging.info("token={}, a={}, promotejs={}".format(token, a, promotejs))
            nc = cookielib.Cookie(
                version=0,
                name='promotejs',
                value=promotejs,
                port=None,
                port_specified=False,
                domain=".jd.com",
                domain_specified=True,
                domain_initial_dot=False,
                path="/",
                path_specified=True,
                secure=False,
                expires=None,
                discard=False,
                comment=None,
                comment_url=None,
                rest=None
            )
            self.sess.cookies.set_cookie(nc)
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False
        try:
            resp = self.sess.get(index_url)
            res = self.find_key_str(resp.text, "beanid")
            if len(res) == 0:
                logging.warning(u'没有找到beanid');
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
        for act in res:
            try:
                data = {
                    'active': act,
                    'g_tk': g_tk,
                }
                resp = self.sess.get(sp_url, params=data)
                ret = self.find_key_num(resp.text, "ret")
                if len(ret) == 0:
                    logging.warning(u'{},没有ret'.format(resp.text))
                    continue
                retmsg = self.find_key_str(resp.text, "retmsg")
                if len(retmsg) == 0:
                    logging.warning(u'{},没有retmsg'.format(resp.text))
                    continue
                beansnumber = self.find_key_num(resp.text, "beansnumber")
                if len(beansnumber) == 0:
                    logging.warning(u'{},没有beansnumber'.format(resp.text))
                    continue
                logging.info(u'周末活动{}: {}, ret {}, bean {}'.format(act, retmsg[0], ret[0], beansnumber[0]))
            except Exception as e:
                logging.error('Exp {0} : {1}'.format(FuncName(), e))
        for i in range(1,10,1):
            box_data = {
                'boxindex': str(i),
                'g_tk': g_tk,
            }
            try:
                resp = self.sess.get(out_url, params=box_data)
                ret = self.find_key_num(resp.text, "ret")
                if len(ret) == 0:
                    logging.warning(u'{},没有ret'.format(resp.text))
                    continue
                retmsg = self.find_key_str(resp.text, "retmsg")
                if len(retmsg) == 0:
                    logging.warning(u'{},没有retmsg'.format(resp.text))
                    continue
                outcome = self.find_key_num(resp.text, "outcome")
                if len(outcome) == 0:
                    logging.warning(u'{},没有outcome'.format(resp.text))
                    continue
                logging.info(u'{}号: {}, ret {}, outcome {}'.format(i, retmsg[0], ret[0], outcome[0]))
            except Exception as e:
                logging.error('Exp {0} : {1}'.format(FuncName(), e))
                return False
        for i in range(1,10,1):
            box_data = {
                'boxindex': str(i),
                'g_tk': g_tk,
            }
            try:
                resp = self.sess.get(in_url, params=box_data)
                ret = self.find_key_num(resp.text, "ret")
                if len(ret) == 0:
                    logging.warning(u'{},没有ret'.format(resp.text));
                    continue
                retmsg = self.find_key_str(resp.text, "retmsg")
                if len(retmsg) == 0:
                    logging.warning(u'{},没有retmsg'.format(resp.text));
                    continue
                logging.info(u'{}号: {}, ret {}'.format(i, retmsg[0], ret[0]))
            except Exception as e:
                logging.error('Exp {0} : {1}'.format(FuncName(), e))
                return False

    def mobile_sign_year(self):
        index_url = 'http://jshopscene.jd.com/view/sign/getSignInDetailAndRule?uuid=63ebcf3e-b479-4182-aad6-05f051d9b0b2'
        sign_url = 'http://jshopscene.jd.com/view/sign/signin?uuid=63ebcf3e-b479-4182-aad6-05f051d9b0b2'
        logging.info(u'签到京东年货节')
        try:
            resp = self.sess.get(index_url)
            resp = self.sess.get(sign_url)
            resp_json = resp.json()
            if "result" in resp_json:
                if resp_json["result"] == False:
                    logging.warning(u'签到失败: {}, {}'.format(resp_json["message"], resp_json["result"]))
                if "prize_result" in resp_json:
                    basic = resp_json["prize_result"]["basicPrize"]["prizeName"]
                    if "message" in resp_json["prize_result"]["extendPrize"]:
                        extend = resp_json["prize_result"]["extendPrize"]["message"]
                    elif "prizeName" in resp_json["prize_result"]["extendPrize"]:
                        extend = resp_json["prize_result"]["extendPrize"]["prizeName"]
                    else:
                        extend = "What the hell?"
                    logging.info(u'签到结果: {}, {}'.format(basic, extend))
            else:
                logging.warning(u'{},没有result'.format(resp_json));
        except Exception as e:
            logging.error('Exp {0} : {1}'.format(FuncName(), e))
            return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - (%(levelname)s) %(message)s', datefmt='%H:%M:%S')  

    jd = JDSign()
    func_list = dir(jd)
    func_list = sorted(func_list)
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
