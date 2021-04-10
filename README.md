# これは何？

[静岡県 新型コロナウイルス感染症対策サイト](https://stopcovid19.code4numazu.org/)で利用するオープンデータを、対策サイトで扱えるデータ（data.json）に変換するスクリプトです

オープンデータのDL先: [新型コロナウイルス感染症県内感染動向 - 静岡県オープンデータ](https://opendata.pref.shizuoka.jp/dataset/8167.html)

# 必要な物

- macOS/linux環境を推奨(シェルスクリプトを利用しています)
- Python: 3.7以降推奨
- 開発時利用モジュール
  - pipenv
  - pytest
  - flake8
  - black

# 使い方

bat.sh上でPythonの仮想環境のセットアップとスクリプトの実行を行います。

```bash
$ bash bat.sh
# data.json, news.jsonが生成されます
```

# docker-composeを使う場合

docker, docker-composeをインストールしたうえで以下のコマンドを実行してください。

実行時にdistディレクトリが生成され、data.json, news.jsonが生成されます。

```bash
$ docker-compose up --build
```

# 開発方法

venv+pipを利用してください。dockerを利用する場合は環境構築は必要ありません。

```bash
$ python3 -m venv .venv

# Linux, Macの例
$ source .venv/bin/activate
# Winの例
.venv/Scripts/activate

pip install -r requirements.txt
```

pipenv向けのPipfileも同梱していますが、メンテしておらず近日除去予定です。

# data.jsonのデータフォーマットについて
こちらを参照してください -> [data_format.md](data_format.md)