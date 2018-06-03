URL=''
URL='http://payhome.jd.com//my/raffle/exchangeCoupon?couponId=503f1230e350a0a8a919cd1f11102a87&fp=082c4acee50b224decc6aec857003ce2&eid=VR6F2MWREACHLIKZCYWOADH2KVZSFWO5VDYDU7CM2Y2IA27FEPTNEWNE4PELNN4VDZGOKWTFJBONK2Z7G2SSE2HXXY'
KEY="3472bd7400804b01b6d5bd8162289d85"
ROLEID="10117929"
HOUR=09
MINUTE=00
PROCESS=32
FILE="mobile_coupon.txt"
if [ -e $FILE ]; then
    rm -f $FILE
fi
echo "Login to JD ..."
if [ -z "$URL" ]; then
    python py/jd_coupon_mobile.py -k $KEY -r $ROLEID -hh $HOUR -m $MINUTE -p $PROCESS -l $FILE
else
    python py/jd_coupon_mobile.py -u $URL -k $KEY -r $ROLEID -hh $HOUR -m $MINUTE -p $PROCESS -l $FILE
fi
USER="jd_coupon_log"
PASS="jd123456"
TO="jd_coupon_log@163.com"
if [ -e $FILE ]; then
    echo "Send email to $TO ..."
    python py/email163.py -u $USER -p $PASS -t $TO -f $FILE
fi
