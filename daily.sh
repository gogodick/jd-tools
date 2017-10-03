CODE="a9b4fd5b-47c9-4db8-83f8-e420a7631224"
rm -rf cookies
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
