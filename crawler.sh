DEPTH=5
PROCESS=16
LOG_FILE="log_crawler.txt"
COUPON_FILE="my_coupon.csv"
LOTTERY_FILE="my_lottery.csv"
if [ -e $LOG_FILE ]; then
    rm $LOG_FILE
fi
if [ -e $COUPON_FILE ]; then
    rm $COUPON_FILE
fi
if [ -e $LOTTERY_FILE ]; then
    rm $LOTTERY_FILE
fi
python py/jd_crawler.py -p $PROCESS -d $DEPTH -cf $COUPON_FILE -lf $LOTTERY_FILE
python py/jd_lottery.py -f $LOTTERY_FILE -l $LOG_FILE
USER="jd_coupon_log"
PASS="jd123456"
TO="jd_coupon_log@163.com"
if [ -e $LOG_FILE ]; then
    echo "Send email to $TO ..."
    python py/email163.py -u $USER -p $PASS -t $TO -f $LOG_FILE
fi
