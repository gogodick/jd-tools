URL="http://coupon.jd.com/ilink/couponSendFront/send_index.action?key=8ac0db8bf5224b3caad26e7241aa4ade&roleId=6966565&to=sale.jd.com/act/wh6aulr4ep7wv5.html&"
HOUR=10
MINUTE=00
DURATION=3
PROCESS=16
FILE="coupon.txt"
if [ -e $FILE ]; then
    rm $FILE
fi
echo "Login to JD ..."
python py/jd_coupon.py -u $URL -hh $HOUR -m $MINUTE -d $DURATION -p $PROCESS -l $FILE
USER="jd_coupon_log"
PASS="jd123456"
TO="jd_coupon_log@163.com"
if [ -e $FILE ]; then
    echo "Send email to $TO ..."
    python py/email163.py -u $USER -p $PASS -t $TO -f $FILE
fi
