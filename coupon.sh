URL="https://coupon.jd.com/ilink/couponSendFront/send_index.action?key=5295463f6ce84ae8afce9624093e2fab&roleId=6932641&to=sale.jd.com/act/bgx0ywve5awmvnxp.html&"
HOUR=09
MINUTE=00
DURATION=3
PROCESS=32
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
