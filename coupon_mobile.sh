URL=''
URL='http://api.m.jd.com/client.action?functionId=newBabelAwardCollection&clientVersion=6.5.2&build=53662&client=android&androidId=e6f3d6adfea10bdd&installtionId=cd2474c771884269a103c12652b948d9&sdkVersion=23&uuid=357755070126840-e458b88e8e4c&st=1509660876593&sign=11e7dddb8bdb03fb43ec9ef95437dbe8&sv=100&body=%7B%22activityId%22%3A%22o1SAPkr8McqBZ8N1N9LhevAGKQg%22%2C%22scene%22%3A%221%22%2C%22args%22%3A%22key%3Debbf381a37944e3f92ede837445d7172%2CroleId%3D8754258%22%7D'
KEY="ebbf381a37944e3f92ede837445d7172"
ROLEID="8754258"
HOUR=08
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
