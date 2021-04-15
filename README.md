# これは何？

[静岡県 新型コロナウイルス感染症対策サイト](https://stopcovid19.code4numazu.org/)で利用するオープンデータを、対策サイトで扱えるデータ（data.json）に変換するスクリプトです

オープンデータのDL先: [新型コロナウイルス感染症県内感染動向 - 静岡県オープンデータ](https://opendata.pref.shizuoka.jp/dataset/8167.html)

# 利用環境

- macOS/linux環境を推奨(シェルスクリプトを利用しています)
- Python: 3.7以降推奨
- 開発時利用モジュール
  - pytest
  - flake8
  - black
- dockerでスクリプト動作させることが可能です
  - Win環境で行う場合はdockerでの開発をおすすめします

# 使い方

```bash
$ bash bat.sh
# data.jsonが生成されます
```

Windows環境で実行する場合はDocker環境を利用してください。未確認ですがWSLでの動作も可能です。

# Docker

Docker環境はWin10での想定しています。


```bash
# ビルド
$ docker-compose build
# スクリプトを起動します。プロジェクトフォルダ内にjsonファイルが生成されます。
$ docker-compose run generator

# もしくはupコマンドで実行
$ docker-compose up -- build
```

Linux環境の場合、生成されたjsonファイルはホストとコンテナのユーザーIDグループIDの相違でファイルの所有ユーザーがrootになる可能性があります。ユーザーの変更(`chown`)やファイルコピーを行い利用ください。

# 開発方法

dockerで開発する場合は、ローカルのスクリプト等のファイルをコンテナ側に名前付きボリュームでマウントを行うので、ローカルの変更がそのままコンテナに反映されます。

## docker環境

テストはdocker内で生成されるPythonのvenv環境にあるpytestを利用してください。

```bash
$ docker-compose run generator pytest
```
## python venv

Mac, Linuxを想定しています

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -U pip
$ pip install -r requirements.txt
```

# data.jsonのデータフォーマットについて
こちらを参照してください -> [data_format.md](data_format.md)