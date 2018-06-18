URL=''
URL='https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&body=%7B%22activityId%22%3A%22VmS8hRGkx44BVfPKv5JffRYitrG%22%2C%22from%22%3A%22H5node%22%2C%22scene%22%3A%221%22%2C%22args%22%3A%22key%3D136b2bf4b7d149bbbad37c4f06a2cdc2%2CroleId%3D12481420%22%2C%22platform%22%3A%223%22%2C%22orgType%22%3A%222%22%2C%22openId%22%3A%22-1%22%2C%22pageClickKey%22%3A%22Babel_Coupon%22%2C%22eid%22%3A%22FHQXARXVXNOAD6W36QL23X3WQY324PSPMIWNREJ6L4LUXTTRB7E36QPV67UWTWBUFGJKMFH55JE6E4DKHZXSBF62LY%22%2C%22fp%22%3A%22277020ee87ca58c10dc60011931c8a5a%22%2C%22shshshfp%22%3A%220cf4feec85d726fa9681dbe452b3de0f%22%2C%22shshshfpa%22%3A%2275009a55-8684-8fec-9c6b-c17f5c0b9c38-1516107391%22%2C%22shshshfpb%22%3A%22158d5400fddfe4326bc69923c9353803b4c31f1c662d623e1598b94005%22%2C%22childActivityUrl%22%3A%22https%253A%252F%252Fpro.m.jd.com%252Fmall%252Factive%252FVmS8hRGkx44BVfPKv5JffRYitrG%252Findex.html%253Fsid%253Dce35a5008e68def72e7896205df21c33%22%2C%22mitemAddrId%22%3A%22%22%2C%22geo%22%3A%7B%22lng%22%3A%22%22%2C%22lat%22%3A%22%22%7D%2C%22addressId%22%3A%22%22%2C%22posLng%22%3A%22%22%2C%22posLat%22%3A%22%22%2C%22focus%22%3A%22%22%2C%22innerAnchor%22%3A%22%22%7D&client=wh5&clientVersion=1.0.0&sid=ce35a5008e68def72e7896205df21c33&uuid=15161073911521468790382'
KEY="136b2bf4b7d149bbbad37c4f06a2cdc2"
ROLEID="12481420"
HOUR=15
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
