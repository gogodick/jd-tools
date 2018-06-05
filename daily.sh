CODE="58ae2fca-88ce-4f44-9838-94ef4c490258"
rm -rf cookies
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
python py/jd_shop_sign.py
