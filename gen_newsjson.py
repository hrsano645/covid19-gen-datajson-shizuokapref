# coding: utf-8
import json
import sys

import requests
from bs4 import BeautifulSoup

# 新着情報を入手するサイトのURL
TARGET_URL = "https://www.pref.shizuoka.jp/kinkyu/covid-19.html"

NEW_ITEM_PTAG_SELECTOR = (
    "#tmp_read_contents > table:nth-child(5) > tbody > tr:nth-child(2) > td p"
)
# 出力するファイル名
FILE_NAME = "news.json"


def main():
    shizuoka_covid19_req = requests.get(TARGET_URL)
    shizuoka_covid19_req.encoding = shizuoka_covid19_req.apparent_encoding

    if not shizuoka_covid19_req.status_code == 200:
        print("エラーが発生しました:サイトへのアクセスが出来ませんでした。")
        # TODO:2020-07-12 サイトのアクセスが出来ないエラーとして、slackに通知ポストする
        sys.exit(1)

    # サイトの構造を取る
    shizuoka_covid19_bs = BeautifulSoup(
        shizuoka_covid19_req.text, features="html.parser"
    )

    # なるべくサイトの構造に依存しないでニュース記事を取りに行く
    news_p_tag_list = shizuoka_covid19_bs.select(NEW_ITEM_PTAG_SELECTOR)

    # サイトの構造が変わり、pタグが取得できない場合はエラーとして終了する
    if not news_p_tag_list:
        # TODO:2020-07-12 サイトのアクセスが出来ないエラーとして、slackに通知ポストする
        print("エラーが発生しました:サイトの構造が変更されたようです")
        sys.exit(1)

    news_list = list()
    for news_p_tag in news_p_tag_list:

        news_a_tag = news_p_tag.find("a")
        news_link = news_a_tag["href"]

        # urlの正規化:絶対アドレスではない場合の処理
        if "http" not in news_link:
            news_link = "https://www.pref.shizuoka.jp" + news_a_tag["href"]

        item = {
            # 日付文字列の先頭に"・"、最後に" "があるから省く
            "date": news_p_tag.contents[0][1:],
            "url": news_link,
            "text": news_a_tag.text,
        }
        news_list.append(item)

    # TODO:2020-07-12 サイトの構造が中途半端に変更があったとき用に値のバリデーションを入れたほうがいいかも。

    # ここまで来たらjsonファイルに保存する
    with open(FILE_NAME, "w", encoding="utf-8") as newsjson:
        json.dump({"newsItems": news_list}, newsjson, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
