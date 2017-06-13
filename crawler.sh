URL="https://sale.jd.com/act/XUh2CDEPdI6YuzZf.html"
HOUR=0
FILE="crawler.txt"
if [ -e $FILE ]; then
    rm $FILE
fi
echo "Login to JD ..."
python py/jd_crawler.py -u $URL -l $FILE
#python py/jd_crawler.py -u $URL -hh $HOUR -l $FILE
USER="jd_coupon_log"
PASS="jd123456"
TO="jd_coupon_log@163.com"
if [ -e $FILE ]; then
    echo "Send email to $TO ..."
    python py/email163.py -u $USER -p $PASS -t $TO -f $FILE
fi
