#!/usr/bin/env bash

# [設定]
# 地域名を指定するときには "bash bat.sh [地域名]" といった形式で引数をひとつ追加してください
# 引数を指定しない場合は静岡県のデータを作成します。

SHELL_ARG_LOCALNAME=$1

if [ $# == 0 ]; then
    LOCALNAME="静岡県"
elif [ $# == 1 ]; then
    LOCALNAME=${SHELL_ARG_LOCALNAME}
else
    echo "引数指定が正しくありません。\"bash bat.sh [地域名]\" といった形式で入力してください"
    echo "例: \"bash bat.sh 富士市\""
    exit 1
fi

# [スクリプトスタート]
echo "===[地域名: ${LOCALNAME}]==="

# システムにパッケージを入れないためにvenv環境を用意する。既にある場合は有効化
cwd=$(cd $(dirname $0); pwd)
cd ${cwd}

if [ -d ${cwd}/.venv/ ]; then
    # venvがある場合は有効化
    echo "===[Python venv 有効化]==="
    source ${cwd}/.venv/bin/activate

else
    echo "===[Python venv 作成]==="
    python3 -m venv .venv
    source ${cwd}/.venv/bin/activate
    pip install -r requirements.txt
fi

# Python実行環境の表示
echo "Using Pythonpath: `which python`"
echo "pythonversion: `python --version`"

echo "===[data.json 生成]==="
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/46009/220001_shizuoka_covid19_call_center.csv > call_center.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/46279/220001_shizuoka_covid19_patients.csv > patients.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/45876/220001_shizuoka_covid19_test_number.csv > test_number.csv
curl https://opendata.pref.shizuoka.jp/dataset/8167/resource/48851/220001_new_shizuoka_covid19_patients.csv > details_of_confirmed_cases.csv

python patients.py patients.csv call_center.csv test_number.csv details_of_confirmed_cases.csv ${LOCALNAME}

echo "===[news.json生成]==="
python gen_newsjson.py ${LOCALNAME}
