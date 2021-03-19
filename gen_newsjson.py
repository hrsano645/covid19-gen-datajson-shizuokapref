# coding: utf-8
import json
import sys
import re
from collections import namedtuple
import io
import csv

import requests
from bs4 import BeautifulSoup


# TODO:2021-03-17 静岡版と富士市版と両方対応するので、汎用挙動をクラスで対応しておく

# 汎用クラスに必要な物:
# ソース定義 get_newslist: ソースの取得手段: ここが唯一変更されて内部データを作る
# ニュース生成 generate_json: ニュース記事を生成する

# 富士市版用に、オープンデータの変換
# 静岡県版はスクレイピング対応

LocalGenCls = namedtuple("LocalGenCls", ["name", "cls"])


class News(object):
    def __init__(self, news_read_func):
        self.news_read_func = news_read_func
        self.news_item_list = []

    def _get_newslist(self):
        self.news_item_list = self.news_read_func()
        if not self.news_item_list:
            # error 的な物を返す
            print("ニュースが1行も生成されませんでした")
            sys.exit(1)

    def generate_json(self):
        # 出力するファイル名
        FILE_NAME = "news.json"
        with open(FILE_NAME, "w", encoding="utf-8") as newsjson:
            json.dump(
                {"newsItems": self.news_item_list},
                newsjson,
                ensure_ascii=False,
                indent=4,
            )


def get_shizuoka_newslist() -> list:
    """
    静岡の対策サイトの新着情報を探索して、新着情報のリスト一覧を生成する
    特定のタグを知りたいつもりだったけど、text属性に正規表現を渡して、日付が書いてある部分を探しています。

    > ・9/23 川勝知事からのメッセージを掲載しました
    """
    # 新着情報を入手するサイトのURL
    TARGET_URL = "https://www.pref.shizuoka.jp/kinkyu/covid-19.html"

    req = requests.get(TARGET_URL)
    req.encoding = req.apparent_encoding

    if not req.status_code == 200:
        print("サイトへのアクセスが出来ませんでした: status_code:{}".format(req.status_code))
        # TODO:2020-07-12 サイトのアクセスが出来ないエラーとして、slackに通知ポストする
        sys.exit(1)

    # サイトをBSでパース
    bs = BeautifulSoup(req.text, features="html.parser")

    # なるべくサイトの構造に依存しないでニュース記事を取りに行く
    # サイトの構造が変わり、pタグが取得できない場合はエラーとして終了する
    news_tag_list = bs.find_all(text=re.compile("・\\d{1,2}/\\d{1,2}.*"))
    if not news_tag_list:
        # TODO:2020-07-12 サイトのアクセスが出来ないエラーとして、slackに通知ポストする
        print("サイトの構造が変更されたようです")
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
    return news_list


def get_fujicity_newslist() -> list:
    """
    オープンデータを取得して、そこからニュースを生成
    """
    req = requests.get(TARGET_URL)
    req.encoding = req.apparent_encoding

    if not req.status_code == 200:
        print("サイトへのアクセスが出来ませんでした: status_code:{}".format(req.status_code))
        # TODO:2020-07-12 サイトのアクセスが出来ないエラーとして、slackに通知ポストする
        sys.exit(1)

    # csvファイルとして読み込む
    # メモリ上に展開する（少ないのでファイルにしなくてもいいと思う）
    # 辞書のkey名を変更
    with open(io.BytesIO(req.content), "r", encoding="shift-jis") as csvfile:
        news_list = list(csv(DictReader(csvfile)))

    # 生成結果のキーを変更する
    for item in news_list:
        item["date"] = item.pop()
        item["url"] = item.pop()
        item["text"] = item.pop()

    return news_list


def main():
    # 地域名と実行する生成クラスを用意
    local_func_map = [
        LocalGenCls("静岡県", News(get_shizuoka_newslist)),
        LocalGenCls("富士市", News(get_fujicity_newslist)),
    ]

    # ---[地域別フィルタ]---
    local_name = None
    if len(sys.argv) == 2:
        local_name = sys.argv[1]
    # 地域名がない場合は静岡県
    if not local_name:
        local_name = "静岡県"

    # 地域名を元にフィルターして実行
    for local_func in local_func_map:
        if local_name == local_func.name:
            print("{}のnews.jsonを生成します".format(local_name))
            local_func.cls.generate_json()
            break

    exit()


if __name__ == "__main__":
    main()
