KEY="92cdc857ef844b5ba07f2496a998c341"
ROLEID="7290231"
HOUR=20
MINUTE=00
PROCESS=32
COOKIEFILE="mobile_cookie.dat"
FILE="coupon.log"
TARGET="c/coupon"
ROOT=`pwd`
cd c
make clean && make
cd $ROOT
if [ ! -e $TARGET ]; then
    return
fi
if [ -e $FILE ]; then
    rm $FILE
fi
$TARGET "mobile_cookie.dat" $KEY $ROLEID $HOUR $MINUTE $PROCESS
