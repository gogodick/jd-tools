KEY="37813f3c2d3f4ce5aa507ea73780ca2d"
ROLEID="7212398"
HOUR=12
MINUTE=00
PROCESS=32
FILE="mobile_coupon.txt"
if [ -e $FILE ]; then
    rm $FILE
fi
echo "Login to JD ..."
python py/jd_coupon_mobile.py -k $KEY -r $ROLEID -hh $HOUR -m $MINUTE -p $PROCESS -l $FILE
USER="jd_coupon_log"
PASS="jd123456"
TO="jd_coupon_log@163.com"
if [ -e $FILE ]; then
    echo "Send email to $TO ..."
    python py/email163.py -u $USER -p $PASS -t $TO -f $FILE
fi
