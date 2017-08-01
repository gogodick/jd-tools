CODE="c5d9ba46-d1fd-4c8d-959c-b74589541c3d"
rm -rf cookies
python py/jd_lottery.py -c $CODE
python py/jd_sign.py
