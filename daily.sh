CODE="b542e458-807b-4e16-8f6f-f8c5608f857d"
rm -rf cookies
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
