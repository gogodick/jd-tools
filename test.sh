URL="https://coupon.jd.com/ilink/couponSendFront/send_index.action?key=e6c7b0f611cb4af59c0cc028e80d90cc&roleId=6928644&to=sale.jd.com/act/wh6aulr4ep7wv5.html&"
HOUR=14
MINUTE=00
DURATION=3
PROCESS=8
FILE="log.txt"
if [ -e $FILE ]; then
    rm $FILE
fi
echo "Login to JD ..."
#python py/jd_coupon.py -u $URL -hh $HOUR -m $MINUTE -d $DURATION -p $PROCESS
python py/jd_coupon.py -u $URL -hh $HOUR -m $MINUTE -d $DURATION -p $PROCESS | tee $FILE
USER="jd_coupon_log"
PASS="jd123456"
TO="jd_coupon_log@163.com"
if [ -e $FILE ]; then
    echo "Send email to $TO ..."
    python py/email163.py -u $USER -p $PASS -t $TO -f $FILE
fi