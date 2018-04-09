CODE="db935d8c-6dd1-41dc-b103-5417bf5b73a8"
rm -rf cookies
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
python py/jd_shop_sign.py
