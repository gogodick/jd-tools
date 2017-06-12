# jd-coupon
These scripts are used to search and click the coupon on JD website.
And the original code is from https://github.com/Adyzng/jd-autobuy, and his code is used to login to JD website.

## Enviroment
Please install Cygwin with python and pip, and use below commands to install modules:
``` cmd
python -m pip install requests
python -m pip install beautifulsoup4
```
## Usage
### jd_coupon.py
Please refer to coupon.sh.
1. URL is your coupon url.
2. HOUR is hour for coupon release time.
3. MINUTE is minute for coupon release time.
4. DURATION is the click duration in minutes.
5. PROCESS is the number of processes used for click.
6. FILE is used for log.
7. USER is the email account for 163.
8. PASS is the email password for 163.
9. TO is the email address for receiver.

And the result is like this:
``` cmd
$ source coupon.sh
Login to JD ...
11:35:58 - (WARNING) +++++++++++++++++++++++++++++++++++++++++++++++++++++++
11:35:58 - (WARNING) Mon Jun 12 11:35:58 2017 > 请打开京东手机客户端，准备扫码登陆:
11:36:01 - (WARNING) 201 : 二维码未扫描 ，请扫描二维码
11:36:04 - (WARNING) 201 : 二维码未扫描 ，请扫描二维码
11:36:07 - (WARNING) 201 : 二维码未扫描 ，请扫描二维码
11:36:10 - (WARNING) 200 : AAEAMFe35heU8_RoHJ5VmRD-rKfPQOejQwLSb3DtInT457JInXYVvLWR5PeUx-xCb1BnwQ
11:36:11 - (WARNING) 登陆成功
11:36:14 - (WARNING) 活动已结束或不存在，看下其他活动吧~
```
### jd_crawler.py
Please refer to crawler.sh.
