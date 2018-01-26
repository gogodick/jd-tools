CODE="732641a3-5d43-4d39-b9dc-291f551171f8"
rm -rf cookies
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
