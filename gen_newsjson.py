# coding: utf-8
import json
import sys
import re

import requests
from bs4 import BeautifulSoup

# 新着情報を入手するサイトのURL
TARGET_URL = "https://www.pref.shizuoka.jp/kinkyu/covid-19.html"

# 出力するファイル名
FILE_NAME = "news.json"

# TODO:2021-03-17 静岡版と富士市版と両方対応するので、汎用挙動をクラスで対応しておく

# 汎用クラスに必要な物:
# ソース定義 get_newslist: ソースの取得手段: ここが唯一変更されて内部データを作る
# ニュース生成 generate_json: ニュース記事を生成する

# 富士市版用に、オープンデータの変換
# 静岡県版はスクレイピング対応


class GenerateNews(object):
    def __init__():
        pass

    def get_newslist():
        pass

    def generate_json():
        pass


def search_news_list(bs: BeautifulSoup) -> list:
    """
    静岡の対策サイトの新着情報を探索して、新着情報のリスト一覧を生成する

    特定のタグを知りたいつもりだったけど、text属性に正規表現を渡して、日付が書いてある部分を探しに行く

    > ・9/23 川勝知事からのメッセージを掲載しました
    """

    return bs.find_all(text=re.compile("・\\d{1,2}/\\d{1,2}.*"))


def main():
    shizuoka_covid19_req = requests.get(TARGET_URL)
    shizuoka_covid19_req.encoding = shizuoka_covid19_req.apparent_encoding

    if not shizuoka_covid19_req.status_code == 200:
        print("エラーが発生しました:サイトへのアクセスが出来ませんでした。")
        # TODO:2020-07-12 サイトのアクセスが出来ないエラーとして、slackに通知ポストする
        sys.exit(1)

    # サイトをBSでパース
    shizuoka_covid19_bs = BeautifulSoup(
        shizuoka_covid19_req.text, features="html.parser"
    )

    # なるべくサイトの構造に依存しないでニュース記事を取りに行く
    news_tag_list = search_news_list(shizuoka_covid19_bs)

    # サイトの構造が変わり、pタグが取得できない場合はエラーとして終了する
    if not news_tag_list:
        # TODO:2020-07-12 サイトのアクセスが出来ないエラーとして、slackに通知ポストする
        print("エラーが発生しました:サイトの構造が変更されたようです")
        sys.exit(1)

    news_list = list()
    for news_p_tag in news_tag_list:

        news_a_tag = news_p_tag.find_next()
        news_link = news_a_tag["href"]

        # urlの正規化:絶対アドレスではない場合の処理
        if "http" not in news_link:
            news_link = "https://www.pref.shizuoka.jp" + news_a_tag["href"]

        item = {
            # 日付文字列の先頭に"・"、最後に" "があるから省く
            "date": news_p_tag.strip()[1:],
            "url": news_link,
            "text": news_a_tag.text,
        }
        news_list.append(item)

    # ここまで来たらjsonファイルに保存する
    with open(FILE_NAME, "w", encoding="utf-8") as newsjson:
        json.dump({"newsItems": news_list}, newsjson, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
