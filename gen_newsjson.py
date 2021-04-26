# coding: utf-8
import json
import sys
import re
from collections import namedtuple
import io
import csv
import datetime

import requests
from bs4 import BeautifulSoup

# 地域名と対応するNewsクラスをセットするコンテナ
LocalGenCls = namedtuple("LocalGenCls", ["name", "cls"])


class News(object):
    """
    news.jsonを生成するクラス。必要なデータを取得する関数を渡してインスタンス化し、generate_jsonメソッドを実行することにより、news.jsonを生成します。

    news_read_funcは戻り値に"date", "url", "text" の三つのkeyが入る辞書オブジェクトのリストである必要があります。
    # TODO:2021-03-19 news_read_funcの戻り値は現在は厳密に調べていません。実装予定です。
    """

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
        self._get_newslist()
        with open("news.json", "w", encoding="utf-8") as newsjson:
            json.dump(
                {"newsItems": self.news_item_list},
                newsjson,
                ensure_ascii=False,
                indent=4,
            )


def get_shizuoka_newslist() -> list:
    """
    静岡県の新型コロナ対策サイトの新着情報を、静岡県の新型コロナの情報サイトからスクレイピングしてnews.jsonに使うデータを作成します
    なるべく失敗しにくくするために、正規表現を使って特定のタグを取り込めるようにしています。

    例:
    <p>・3/19 <a href="/kinkyu/covid-19-tyuumokujouhou.html">新型コロナウイルス陽性者が13名確認されました</a></p>

    結果は"date", "url", "text" の三つのkeyが入る辞書オブジェクトのリストが作成されます。
    取得に失敗した場合は標準エラーとして終了します。
    """
    # 新着情報を入手するサイトのURL
    TARGET_URL = "https://www.pref.shizuoka.jp/kinkyu/covid-19.html"

    req = requests.get(TARGET_URL)
    req.encoding = req.apparent_encoding

    if not req.status_code == 200:
        # TODO:2021-03-19 ここのprintは例外として処理する。NotConnectError的な例外名
        print("サイトへのアクセスが出来ませんでした: status_code:{}".format(req.status_code))
        sys.exit(1)

    # サイトをBSでパース
    bs = BeautifulSoup(req.text, features="html.parser")

    # サイトの構造が変わり、pタグが取得できない場合はエラーとして終了する
    news_tag_list = bs.find_all(text=re.compile("・\\d{1,2}/\\d{1,2}.*"))
    if not news_tag_list:
        # TODO:2021-03-19 ここのprintは例外として処理する。CantParseSiteError的な例外名
        print("サイトの構造が変更されたようです")
        sys.exit(1)

    news_list = list()
    for news_p_tag in news_tag_list:
        news_a_tag = news_p_tag.find_next()

        # urlの正規化:絶対アドレスではない場合の処理
        news_link = news_a_tag["href"]
        if "http" not in news_link:
            news_link = "https://www.pref.shizuoka.jp" + news_a_tag["href"]

        # 日付に西暦を加える
        # 日付文字列の先頭に"・"、最後に" "があるから省く
        news_date = datetime.datetime.strptime(news_p_tag.strip()[1:], "%m/%d")
        # 無条件に今年の西暦に変更
        now_dt = datetime.datetime.now()
        news_date = news_date.replace(year=now_dt.year)

        # 今の月より大きい月がある場合は無条件で去年にする
        if now_dt.month < int(news_date.month):
            news_date = news_date.replace(year=now_dt.year - 1)
        item = {
            "date": news_date.strftime("%Y/%m/%d"),
            "url": news_link,
            "text": news_a_tag.text,
        }
        news_list.append(item)
    return news_list


def get_fujicity_newslist() -> list:
    """

    富士市の新型コロナ対策サイトに使う新着情報を富士市のオープンデータから取得してnews.jsonに使うデータを作成します
    結果は"date", "url", "text" の三つのkeyが入る辞書オブジェクトのリストが作成されます。
    取得に失敗した場合は標準エラーとして終了します。
    """

    TARGET_URL = "https://opendata.pref.shizuoka.jp/dataset/8484/resource/50885/%E5%AF%8C%E5%A3%AB%E5%B8%82%E6%96%B0%E5%9E%8B%E3%82%B3%E3%83%AD%E3%83%8A%E3%82%A6%E3%82%A4%E3%83%AB%E3%82%B9%E9%96%A2%E9%80%A3%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9.csv"
    req = requests.get(TARGET_URL)
    # requestのencodingがDLするファイルと合わないので、
    req.encoding = req.apparent_encoding

    if not req.status_code == 200:
        # TODO:2021-03-19 ここのprintは例外として処理する。NotConnectError的な例外名
        print("サイトへのアクセスが出来ませんでした: status_code:{}".format(req.status_code))
        sys.exit(1)

    news_list = []
    # 富士市のオープンデータには列ヘッダがないので、あらかじめ指定する
    with io.StringIO(req.text) as csvfile:
        news_list = list(csv.DictReader(csvfile, ("date", "url", "text")))

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

    # 定義されていない地域名を指定された場合はメッセージを出して終了
    if local_name not in (item.name for item in local_func_map):
        print("指定の地域名「{}」には対応していません".format(local_name))
        sys.exit(1)

    # 地域名を元にフィルターして実行
    for local_func in local_func_map:
        if local_name == local_func.name:
            print("{}のnews.jsonを生成します".format(local_name))
            local_func.cls.generate_json()
            break

    sys.exit(0)


if __name__ == "__main__":
    main()
