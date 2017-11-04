CODE="3e6c3e04-6dce-43dd-8e7f-8ca3094ae5eb"
rm -rf cookies
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
