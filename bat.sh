curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/46009/220001_shizuoka_covid19_call_center.csv > call_center.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/46279/220001_shizuoka_covid19_patients.csv > patients.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/45876/220001_shizuoka_covid19_test_number.csv > test_number.csv
# TODO:2020-11-26 オープンデータ公開されたとき用のDLリンク。想定URLで実際は違うかも
# curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/45876/220001_shizuoka_covid19_details_of_confirmed_cases.csv > details_of_confirmed_cases.csv

python patients.py patients.csv call_center.csv test_number.csv details_of_confirmed_cases.csv