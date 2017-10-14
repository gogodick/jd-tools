URL=''
URL='https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&body={"activityId":"fKh83rNgnrfx7id9gohjnkHrwfK","scene":"1","args":"key=768b4891fa9b48f79f704492467dee95,roleId=8549498","mitemAddrId":"","geo":{"lng":"","lat":""}}&client=wh5&clientVersion=1.0.0'
KEY="768b4891fa9b48f79f704492467dee95"
ROLEID="8549498"
HOUR=20
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
