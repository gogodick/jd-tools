CODE="3ee38a2b-f2c5-41b5-aa92-0cc7cbab73d7"
rm -rf cookies
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
python py/jd_shop_sign.py
