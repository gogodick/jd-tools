CODE="0a30a537-c0ae-45e7-94e5-282a2a1b17cd"
rm -rf cookies
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
