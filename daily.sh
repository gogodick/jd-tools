rm -rf cookies
CODE="bbe8cc6f-e5a8-4c8c-a069-a296e314de63"
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
python py/jd_shop_sign.py
