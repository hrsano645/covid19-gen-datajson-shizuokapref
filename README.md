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
- docker-composeでスクリプト動作させることが可能です
  - Win環境で行う場合はDockerでの開発をおすすめします

# 使い方

MacとLinux環境ではbat.shを実行することでjsonファイルを生成します。

```bash
$ bash bat.sh
# data.jsonが生成されます
```

Windows環境で実行する場合はWSL（未確認ですが動作するはずです）、もしくはDocker環境を用意して実行してください。

# 開発方法

## Docker(docker-compose)

Dockerで開発する場合は、ローカルのスクリプト等のファイルをコンテナ側に名前付きボリュームでマウントを行うので、ローカルの変更がそのままコンテナに反映されます。

```
# コンテナを起動
$ docker-compose up -d --build

# 実行中のコンテナでbashを起動しコンテナに入ります
$ docker-compose exec generator /bin/bash

# data.json生成
$ bash bat.sh
```

生成されたjsonファイルもローカル側に作成されます。

Linux環境の場合、生成されたjsonファイルはホストとコンテナのユーザーIDグループIDの相違でファイルの所有ユーザーがrootになる可能性があります。

jsonファイルを別の場所で使いたい場合はファイルコピーをしてください。

## python venv

主にMac, Linuxを想定しています。

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

## テストの実行

`pytest` コマンドでテストできます。

# data.jsonのデータフォーマットについて
こちらを参照してください -> [data_format.md](data_format.md)