CODE="07d035b5-8808-405a-a85a-1d967534cffc"
rm -rf cookies
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
