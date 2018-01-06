CODE="93b6d11c-4704-4add-8c02-872522aaabfd"
rm -rf cookies
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
