# これは何？

[静岡県 新型コロナウイルス感染症対策サイト](https://stopcovid19.code4numazu.org/)で利用するオープンデータを、対策サイトで扱えるデータ（data.json）に変換するスクリプトです

オープンデータのDL先: [新型コロナウイルス感染症県内感染動向 - 静岡県オープンデータ](https://opendata.pref.shizuoka.jp/dataset/8167.html)

# 利用環境

- macOS/linux環境を推奨(シェルスクリプトを利用しています)
- Python: 3.7以降推奨
- 開発時利用モジュール
  - pipenv
  - pytest
  - flake8
  - black

## オプション

- dockerでスクリプト動作させることが可能です
  - Win環境で行う場合はdockerでの開発をおすすめします

# 使い方

```bash
$ bash bat.sh
# data.jsonが生成されます
```

# Docker

Docker環境はWin, Macを想定しています。現時点ではテストは動作できません。
Linux環境の場合はホストとコンテナのユーザーIDグループIDの相違でファイルの所有ユーザーがrootになる可能性があります。ユーザーの変更(`chown`)やファイルコピーを行い利用ください。

```
$ docker-compose up --build
# distディレクトリが新規作成されてその中にjsonファイルが作成されます
```
# 開発方法

pipenvを利用してください。pipenv上ではpython3.7を利用しています。

```bash
$ pipenv install
```
# data.jsonのデータフォーマットについて
こちらを参照してください -> [data_format.md](data_format.md)