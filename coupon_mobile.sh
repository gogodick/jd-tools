URL=''
KEY="450ccbe232a94f3cbdc852978048f213"
ROLEID="8839369"
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
