#!/usr/bin/env bash

# 地域名を指定するときにはLOCALNAME変数に＊＊市と入力してください
LOCALNAME=""

# run scripts
echo "===[地域名: ${LOCALNAME}]==="

# check python venv and activate
cwd=$(cd $(dirname $0); pwd)
cd ${cwd}

if [ -d ${cwd}/.venv/ ]; then
    # if not venv, generate venv
    echo "===[activate python venv]==="
    source ${cwd}/.venv/bin/activate

else
    echo "===[generate python venv]==="
    python3 -m venv .venv
    source ${cwd}/.venv/bin/activate
    pip install -U pip
    pip install -r requirements.txt
fi

# デバッグ用
echo "pythonpath: `which python`"
echo "pythonversion: `python --version`"

# generate data.json
echo "===[generate data.json]==="
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/46009/220001_shizuoka_covid19_call_center.csv > call_center.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/46279/220001_shizuoka_covid19_patients.csv > patients.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/45876/220001_shizuoka_covid19_test_number.csv > test_number.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/48851/220001_new_shizuoka_covid19_patients.csv > details_of_confirmed_cases.csv

python patients.py patients.csv call_center.csv test_number.csv details_of_confirmed_cases.csv ${LOCALNAME}

# generate news.json
echo "===[generate news.json]==="
python gen_newsjson.py ${LOCALNAME}


# export json file
mkdir -p ./dist

cp data.json ./dist/data.json
cp news.json ./dist/news.json