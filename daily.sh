CODE="91b3a9d7-2a05-4d6b-9ebc-05d3918fc3e1"
rm -rf cookies
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
python py/jd_shop_sign.py
