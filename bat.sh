LOCALNAME=""

# run scripts
echo "===[地域名: ${LOCALNAME}]==="

# generate data.json
echo "===[generate data.json]==="
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/46009/220001_shizuoka_covid19_call_center.csv > call_center.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/46279/220001_shizuoka_covid19_patients.csv > patients.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/45876/220001_shizuoka_covid19_test_number.csv > test_number.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/48851/220001_new_shizuoka_covid19_patients.csv > details_of_confirmed_cases.csv

python patients.py patients.csv call_center.csv test_number.csv details_of_confirmed_cases.csv ${LOCALNAME}

# export json file
mkdir -p ./dist

cp data.json ./dist/data.json