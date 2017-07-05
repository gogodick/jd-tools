KEY="9aca78967d1f4595b292ff75bf2a92be"
ROLEID="7289727"
HOUR=12
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
