rm -rf cookies
CODE="58ae2fca-88ce-4f44-9838-94ef4c490258"
python py/jd_lottery.py -c $CODE
CODE="bbe8cc6f-e5a8-4c8c-a069-a296e314de63"
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
python py/jd_shop_sign.py
