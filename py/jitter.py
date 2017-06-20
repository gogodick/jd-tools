# -*- coding: utf-8 -*-

import ntplib
import os
import time
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class progressbar(object):
    def __init__(self, finalcount, block_char='.'):
        self.finalcount = finalcount
        self.blockcount = 0
        self.block = block_char
        self.f = sys.stdout
        if not self.finalcount: return
        self.f.write('\n------------------ % Progress -------------------1\n')
        self.f.write('    1    2    3    4    5    6    7    8    9    0\n')
        self.f.write('----0----0----0----0----0----0----0----0----0----0\n')
    def progress(self, count):
        count = min(count, self.finalcount)
        if self.finalcount:
            percentcomplete = int(round(100.0*count/self.finalcount))
            if percentcomplete < 1: percentcomplete = 1
        else:
            percentcomplete=100
        blockcount = int(percentcomplete//2)
        if blockcount <= self.blockcount:
            return
        for i in range(self.blockcount, blockcount):
            self.f.write(self.block)
        self.f.flush()
        self.blockcount = blockcount
        if percentcomplete == 100:
            self.f.write("\n")

def get_network_time():
    try:
        client = ntplib.NTPClient()
        response = client.request('ntp2.aliyun.com')
    except Exception, e:
        logging.warning('Exp {0} : {1}'.format(FuncName(), e))
        return None
    else:
        return response.tx_time

diff = get_network_time() - time.time()
min_diff = diff
max_diff = diff
pb = progressbar(60, "#")
for i in range(60):
    diff = get_network_time() - time.time()
    if diff > max_diff:
        max_diff = diff
    if diff < min_diff:
        min_diff = diff
    time.sleep(1)
    pb.progress(i)
pb.progress(60)
jitter = (max_diff - min_diff) * 1000
print 'Jitter is {} ms'.format(int(jitter))
