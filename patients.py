# coding:utf-8
import csv

# import random
import sys
from datetime import datetime
from datetime import timedelta

from collections import namedtuple

# 置き換えルール:年代に分けられない情報を置き換えるルールセット
#
# ref:https://codefornumazu.slack.com/archives/C011YSQPQCA/p1587989876014200
# 考え方：元の情報でオープンデータ項目定義書に当てはまるものがあれば、それに置き換える。当てはまるものがないものはNULL（空欄）とする。
# その結果、
# ・高齢でない成人　　⇒　NULL
# ・高齢者　　　　　　⇒　NULL
# ・未成年（18歳未満）⇒　NULL
# ・若年者　　　　　　⇒　NULL
# ・小児　　　　　　　⇒　NULL
# ・未就学児　　　　　⇒　10歳未満
# ・未就園児　　　　　⇒　10歳未満
# ・10歳未満　　　　　⇒　10歳未満（そのまま）
# ・〇0代　　　　　　⇒　〇0代（そのまま）
# ・NULL　　　　　　　⇒　NULL（そのまま）
# ・不明（現時点ではこのケース無し）　⇒　不明（そのまま）
# ・上記以外の記述が今後増えるかも…　⇒　NULL

# 置き換えのルールを用意
# ReplaceRule.pattern: 置き換え元の文字列パターン
# ReplaceRule.newstr: 置き換えする文字列
ReplaceRule = namedtuple("ReplaceRule", ["pattern", "newstr"])

NENDAI_REPLACE_RULE = [
    ReplaceRule("高齢でない成人", ""),
    ReplaceRule("高齢者", ""),
    ReplaceRule("未成年（18歳未満）", ""),
    ReplaceRule("若年者", ""),
    ReplaceRule("小児", ""),
    ReplaceRule("未就学児", "10歳未満"),
    ReplaceRule("未就園児", "10歳未満"),
    ReplaceRule("10歳未満", "10歳未満"),
    ReplaceRule("不明", "不明"),
]


def replace_nendai_format(src: str):
    """
    年代に対策サイト側で考慮されていない文字列がある場合に置き換えを行う
    """

    # *0代は正規のルールなので、スルーする
    if "0代" in src:
        return src

    rule_pattern = [r_r.pattern for r_r in NENDAI_REPLACE_RULE]
    # ルールにないものは空白
    if src not in rule_pattern:
        return ""
    # ルールにあるものは置き換える
    else:
        target_rule = NENDAI_REPLACE_RULE[rule_pattern.index(src)]
        return src.replace(target_rule.pattern, target_rule.newstr)


def main():
    # 時間関係の生成
    dt_now = datetime.now()
    start = datetime.strptime("2020-01-22", "%Y-%m-%d").date()

    date_month = dt_now.month
    date_day = dt_now.day
    date_month2 = str(date_month)
    date_day2 = str(date_day)

    tomorrow = dt_now + timedelta(days=1)
    tomorrow_str = datetime.strftime(tomorrow, "%Y-%m-%d")

    if date_month < 10:
        date_month2 = "0" + str(date_month)
    date_day = dt_now.day
    if date_day < 10:
        date_day2 = "0" + str(date_day)

    date_string = str(dt_now.year) + "-" + date_month2 + "-" + date_day2

    # data.json更新時のデータ
    now_date = str(dt_now.year) + "\/" + date_month2 + "\/" + date_day2 + " 19:30"

    end = datetime.strptime(tomorrow_str, "%Y-%m-%d").date()

    # 引数からファイル名を取得
    args = sys.argv

    filename = "./" + args[1]

    # 変数
    date_n = []
    kensa = 0  # 検査実施人数
    kanzya = 0  # 陽性患者数
    nyuin = 0  # 入院中
    keisyo = 0  # 軽症・中症
    zyusyo = 0  # 重症
    taiin = 0  # 退院
    shibo = 0  # 死亡

    print("{")

    # querents: 検査件数
    filename = "./" + args[3]
    print('\t"querents": {')

    output_str = '\t\t"date": "' + now_date + '",'
    print(output_str)
    print('\t\t"data": [')
    with open(filename, "r", encoding="shift-jis") as f3:
        reader = csv.reader(f3)
        header = next(reader)  # 読み込み

        # 1行目かのフラグ
        start_flg = 0

        for row in reader:

            # ===[日付の正規化]===
            # 日付を取り出す,splitして年月日に沸ける
            date1 = row[0].split("/")

            # 日付:フォーマットが不正なら飛ばす
            if date1[0] == "":
                break

            # 日付:フォーマットを再度分解: 必要ないかも
            date1 = row[0].split("/")

            # 日付:年
            date20 = date1[0]

            # 日付: 月の文字列長さが1桁しかない場合は0埋めする
            if len(date1[1]) == 1:
                date21 = "0" + date1[1]
            else:
                date21 = date1[1]

            # 日付: 日の文字列長さが1桁しかない場合は0埋めする
            if len(date1[2]) == 1:
                date22 = "0" + date1[2]
            else:
                date22 = date1[2]

            # 日付を再構成
            date3 = date20 + "-" + date21 + "-" + date22
            # short_dateを構成
            date4 = date21 + "\/" + date22
            # ===[日付の正規化終わり]===

            if start_flg != 0:
                print("\t\t\t,")

            # 相談件数, 例外を考慮している？
            row[4] = row[4].replace(",", "")

            print("\t\t\t{")
            str2 = '\t\t\t\t"日付": ' + '"' + date3 + 'T08:00:00.000Z",'
            print(str2)
            str2 = '\t\t\t\t"曜日": 0,'  # メトロ版にある項目だが用途不明
            print(str2)
            str2 = '\t\t\t\t"9-17時": ' + row[4] + ","  # 相談件数
            print(str2)
            str2 = '\t\t\t\t"17-翌9時": 0,'  # ここは相談の受付時間から外れているので毎回0になる
            print(str2)
            str2 = '\t\t\t\t"date": ' + '"' + date3 + '",'
            print(str2)
            str2 = '\t\t\t\t"w": 0,'  # メトロ版にある項目だが用途不明
            print(str2)
            str2 = '\t\t\t\t"short_date": ' + '"' + date4 + '",'
            print(str2)
            str2 = '\t\t\t\t"小計": ' + row[4]  # 9-17時の部分と同じになる
            print(str2)
            print("\t\t\t}")

            start_flg = 1

    print("\t\t]")
    print("\t},")

    #
    # patients: 陽性者
    #

    filename = "./" + args[1]
    print('\t"patients": {')
    output_str = '\t\t"date": "' + now_date + '",'
    print(output_str)
    print('\t\t"data": [')

    with open(filename, "r", encoding="shift-jis") as f:
        reader = csv.reader(f)
        header = next(reader)  # 読み込み

        start_flg = 0

        for row in reader:
            if start_flg != 0:
                print("\t\t\t,")

            print("\t\t\t{")

            # ===[日付の正規化]===
            date1 = row[4].split("/")

            date20 = date1[0]
            if len(date1[1]) == 1:
                date21 = "0" + date1[1]
            else:
                date21 = date1[1]

            if len(date1[2]) == 1:
                date22 = "0" + date1[2]
            else:
                date22 = date1[2]

            date3 = date20 + "-" + date21 + "-" + date22
            # ===[日付の正規化終わり]===

            date_n.append(date3)

            str2 = '\t\t\t\t"リリース日": ' + '"' + date3 + 'T08:00:00.000Z",'
            print(str2)
            str2 = '\t\t\t\t"居住地": ' + '"' + row[6] + '",'
            print(str2)

            # str2 = '\t\t\t\t"年代": ' + '"' + row[7] + '",'
            # print(str2)
            str2 = '\t\t\t\t"年代": ' + '"' + replace_nendai_format(row[7]) + '",'
            print(str2)
            str2 = '\t\t\t\t"性別": ' + '"' + row[8] + '",'
            print(str2)

            # main_summaryの必要な数値もしている
            if row[13] == "1":
                str2 = '\t\t\t\t"退院": ' + '"〇",'
                taiin = taiin + 1
            else:
                str2 = '\t\t\t\t"退院": ' + '"",'
                nyuin = nyuin + 1
                if row[10] == "軽症・中等症":
                    keisyo = keisyo + 1
                if row[10] == "重症":
                    zyusyo = zyusyo + 1
                if row[10] == "死亡":
                    shibo = shibo + 1
                    nyuin = nyuin - 1

            print(str2)
            str2 = '\t\t\t\t"date": ' + '"' + date3 + '"'
            print(str2)

            print("\t\t\t}")

            kanzya = kanzya + 1

            start_flg = 1

    print("\t\t]")
    print("\t},")

    #
    # patients_summary: 陽性者サマリー（人数
    #
    print('\t"patients_summary": {')
    output_str = '\t\t"date": "' + now_date + '",'
    print(output_str)
    print('\t\t"data": [')

    def daterange(_start, _end):
        for n in range((_end - _start).days):
            yield _start + timedelta(n)

    start_flg = 0

    for i in daterange(start, end):
        date_str2 = i.strftime("%Y-%m-%d")
        count = 0
        for date_str in date_n:
            # 一致する文字数をカウント
            if date_str2 == date_str:
                count = count + 1

        if start_flg != 0:
            print("\t\t\t,")

        print("\t\t\t{")
        str2 = '\t\t\t\t"日付" : "' + date_str2 + 'T08:00:00.000Z",'
        print(str2)
        str2 = '\t\t\t\t"小計" : ' + str(count)
        print(str2)
        print("\t\t\t}")

        start_flg = 1
    #   print (i)

    print("\t\t]")
    print("\t},")

    #
    # inspection_persons
    #
    filename = "./" + args[2]

    print('\t"inspection_persons": {')
    output_str = '\t\t"date": "' + now_date + '",'
    print(output_str)
    print('\t\t"labels": [')

    start_flg = 0
    for i in daterange(start, end):
        date_str2 = i.strftime("%Y-%m-%d")

        if start_flg != 0:
            print("\t\t\t\t,")

        str2 = '\t\t\t\t"' + date_str2 + 'T08:00:00.000Z"'
        print(str2)

        start_flg = 1

    print("\t\t],")
    print('\t\t"datasets": [')
    print("\t\t\t{")
    print('\t\t\t\t"label": "検査実施人数",')
    print('\t\t\t\t"data" : [')

    with open(filename, "r", encoding="shift-jis") as f2:
        reader = csv.reader(f2)
        header = next(reader)  # 読み込み

        start_flg = 0
        for row in reader:
            if start_flg != 0:
                str2 = "\t\t\t\t\t,"
                print(str2)

            str2 = "\t\t\t\t\t" + row[4]
            print(str2)
            kensa = kensa + int(row[4])

            start_flg = 1

    print("\t\t\t\t]")
    print("\t\t\t}")
    print("\t\t]")
    print("\t},")

    #
    #
    #
    output_str = '\t"lastUpdate": "' + now_date + '",'
    print(output_str)
    print('\t"main_summary": {')
    print('\t\t"attr": "検査実施人数",')
    print('\t\t"value": ' + str(kensa) + ",")
    print('\t\t"children": [')
    print("\t\t\t{")
    print('\t\t\t\t"attr": "陽性患者数",')
    str2 = '\t\t\t\t"value": ' + str(kanzya) + ","
    print(str2)
    str2 = '\t\t\t\t"children": ['
    print(str2)
    print("\t\t\t\t\t{")
    print('\t\t\t\t\t\t"attr": "入院中",')
    str2 = '\t\t\t\t\t\t"value": ' + str(nyuin) + ","
    print(str2)
    print('\t\t\t\t\t\t"children": [')
    print("\t\t\t\t\t\t\t{")
    print('\t\t\t\t\t\t\t\t"attr": "軽症・中等症",')
    str2 = '\t\t\t\t\t\t\t\t"value": ' + str(keisyo)
    print(str2)
    print("\t\t\t\t\t\t\t},")
    print("\t\t\t\t\t\t\t{")
    print('\t\t\t\t\t\t\t\t"attr": "重症",')
    str2 = '\t\t\t\t\t\t\t\t"value": ' + str(zyusyo)
    print(str2)
    print("\t\t\t\t\t\t\t}")
    print("\t\t\t\t\t\t]")
    print("\t\t\t\t\t},")
    print("\t\t\t\t\t{")
    print('\t\t\t\t\t\t"attr": "退院",')
    str2 = '\t\t\t\t\t\t"value": ' + str(taiin)
    print(str2)
    print("\t\t\t\t\t},")
    print("\t\t\t\t\t{")
    print('\t\t\t\t\t\t"attr": "死亡",')
    str2 = '\t\t\t\t\t\t"value": ' + str(shibo)
    print(str2)
    print("\t\t\t\t\t}")
    print("\t\t\t\t]")
    print("\t\t\t}")
    print("\t\t]")
    print("\t}")

    print("}")


if __name__ == "__main__":
    main()
