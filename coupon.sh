URL="https://coupon.jd.com/ilink/couponActiveFront/front_index.action?key=33fc30cd907841f6ac8aed441986f067&roleId=6939376&to=sale.jd.com/act/ecksrp1q2wbwth.html&"
HOUR=20
MINUTE=00
DURATION=3
PROCESS=16
FILE="log.txt"
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
