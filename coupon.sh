URL="http://coupon.jd.com/ilink/couponSendFront/send_index.action?key=cf5ca79d97fa451b9554df5229d711e4&roleId=6965414&to=sale.jd.com/act/qts6qbhnoml0kj1b.html&"
HOUR=00
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
