# jd-coupon
This Script is used to click the coupon on JD website.
And the original code is from https://github.com/Adyzng/jd-autobuy, his code is used to login to JD website.

## Enviroment
Please install Cygwin with python and pip, and use below commands to install modules:
``` cmd
python -m pip install requests
python -m pip install beautifulsoup4
```
## Usage
Please modify test.sh.
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
$ source test.sh
Login to JD ...
Namespace(duration=3, hour=14, minute=0, process=8, url='https://coupon.jd.com/ilink/couponSendFront/send_index.action?key=e6c7b0f611cb4af59c0cc028e80d90cc&roleId=6928644&to=sale.jd.com/act/wh6aulr4ep7wv5.html&')
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Sat Jun 10 12:17:44 2017 > 请打开京东手机客户端，准备扫码登陆:
201 : 二维码未扫描 ，请扫描二维码
201 : 二维码未扫描 ，请扫描二维码
201 : 二维码未扫描 ，请扫描二维码
200 : AAEAMD1ca-aAVdIEPZzLJ7PyOd96F1WZ1v46Gw06TRlcxIjc242nJadG-RNvqMAsF6obMQ
登陆成功
```
