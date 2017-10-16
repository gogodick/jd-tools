URL=''
URL='http://api.m.jd.com/client.action?functionId=newBabelAwardCollection&clientVersion=6.5.0&client=android&uuid=357755070126840-e458b88e8e4c&st=1508155368481&sign=13bdfc854b9010954ca27e09837b8cbe&sv=121&body={"activityId":"2kdsbHwauQ2kDj8rQghLZAdTWHei","scene":"1","args":"key=01c8d88792ca4ab2aaed8a65795a1768,roleId=8554538"}'
KEY="01c8d88792ca4ab2aaed8a65795a1768"
ROLEID="8554538"
HOUR=00
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
