curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/44809/220001_shizuoka_covid19_call_center.csv > 220001_shizuoka_covid19_call_center.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/44807/220001_shizuoka_covid19_patients.csv > 220001_shizuoka_covid19_patients.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/44810/220001_shizuoka_covid19_test_people.csv > 220001_shizuoka_covid19_test_people.csv

nkf -w8 220001_shizuoka_covid19_patients.csv > patients.csv
nkf -w8 220001_shizuoka_covid19_call_center.csv > call_center.csv
nkf -w8 220001_shizuoka_covid19_test_people.csv > test_people.csv

python patients.py patients.csv test_people.csv call_center.csv > data.json