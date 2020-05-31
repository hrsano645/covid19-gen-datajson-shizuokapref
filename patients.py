# coding:utf-8
import csv
import json
import sys
from collections import Counter, namedtuple
from datetime import datetime, timedelta

# 置き換え用のルールを用意
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

    NENDAI_REPLACE_RULE: 置き換えルール:年代に分けられない情報を置き換えるルールセット

    ref:https://codefornumazu.slack.com/archives/C011YSQPQCA/p1587989876014200
    考え方：元の情報でオープンデータ項目定義書に当てはまるものがあれば、それに置き換える。当てはまるものがないものはNULL（空欄）とする。
    その結果、
    ・高齢でない成人　　⇒　NULL
    ・高齢者　　　　　　⇒　NULL
    ・未成年（18歳未満）⇒　NULL
    ・若年者　　　　　　⇒　NULL
    ・小児　　　　　　　⇒　NULL
    ・未就学児　　　　　⇒　10歳未満
    ・未就園児　　　　　⇒　10歳未満
    ・10歳未満　　　　　⇒　10歳未満（そのまま）
    ・〇0代　　　　　　⇒　〇0代（そのまま）
    ・NULL　　　　　　　⇒　NULL（そのまま）
    ・不明（現時点ではこのケース無し）　⇒　不明（そのまま）
    ・上記以外の記述が今後増えるかも…　⇒　NULL

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


# jsonのテンプレート

root_json_template = """
{
    "querents": {
        "date": "2020\/05\/30 19:30",
        "data": []
    },
    "patients": {
        "date": "2020\/05\/30 19:30",
        "data": []
    },
    "patients_summary": {
        "date": "2020\/05\/30 19:30",
        "data": []
    },
    "inspection_persons": {
        "date": "2020\/05\/30 19:30",
        "labels": [],
        "datasets": []
    },
    "lastUpdate": "2020\/05\/30 19:30",
    "main_summary": {}
}
"""

main_summary_json_template = """
{
    "attr": "検査実施人数",
    "value": 0,
    "children": [
        {
            "attr": "陽性患者数",
            "value": 0,
            "children": [
                {
                    "attr": "入院中",
                    "value": 0,
                    "children": [
                        {
                            "attr": "軽症・中等症",
                            "value": 0
                        },
                        {
                            "attr": "重症",
                            "value": 0
                        }
                    ]
                },
                {
                    "attr": "退院",
                    "value": 0
                },
                {
                    "attr": "死亡",
                    "value": 0
                }
            ]
        }
    ]
}
"""

querents_data_json_template = """
{
    "日付": "2020-02-10T08:00:00.000Z",
    "曜日": 0,
    "9-17時": 0,
    "17-翌9時": 0,
    "date": "2020-02-10",
    "w": 0,
    "short_date": "02\/10",
    "小計": 0
}
"""

patients_data_json_template = """
{
    "リリース日": "2020-02-28T08:00:00.000Z",
    "居住地": "静岡市",
    "年代": "60代",
    "性別": "男性",
    "退院": "〇",
    "date": "2020-02-28"
}
"""

patients_summary_data_json_template = """
{
    "日付": "2020-01-22T08:00:00.000Z",
    "小計": 0
}
"""

inspection_persons_dataset_json_template = """
{
    "label": "検査実施人数",
    "data": [
        0
    ]
}
"""


def main():

    # 時間関係の生成

    dt_now = datetime.now()
    start = datetime.strptime("2020-01-22", "%Y-%m-%d").date()

    latest_datetime = dt_now.replace(hour=19, minute=30, second=0, microsecond=0)

    # data_jsonの更新日
    now_date = latest_datetime.strftime("%Y/%m/%d %H:%M")

    tomorrow = dt_now + timedelta(days=1)

    # 何らかの終了日？ # TODO:2020-05-30 調査必要
    end = tomorrow.date()

    # 引数からファイル名を取得
    args = sys.argv

    filename = "./" + args[1]

    # 変数
    date_n = []  # TODO:2020-05-30 現時でこのリストが何かよくわかってない
    kensa = 0  # 検査実施人数
    kanzya = 0  # 陽性患者数
    nyuin = 0  # 入院中
    keisyo = 0  # 軽症・中症
    zyusyo = 0  # 重症
    taiin = 0  # 退院
    shibo = 0  # 死亡

    # data.jsonのルートデータ構造を取得

    root_json = json.loads(root_json_template)

    # 更新日を設定

    root_json["querents"]["date"] = now_date
    root_json["patients"]["date"] = now_date
    root_json["patients_summary"]["date"] = now_date
    root_json["inspection_persons"]["date"] = now_date

    # querents: 検査件数

    filename = "./" + args[3]

    # querents_data_jsonをロードして、毎回生成し続ける

    querent_data_list = list()

    with open(filename, "r", encoding="shift-jis") as f3:
        call_center_csv = csv.DictReader(f3)

        for call_center_row in call_center_csv:

            # 日付の正規化
            # TODO:2020-05-30 ここはreでちゃんとバリデーションしておく
            call_center_row_date_str = call_center_row["受付_年月日"].split("/")

            # 日付:フォーマットが不正なら飛ばす
            if call_center_row_date_str[0] == "":
                break

            querent_date = datetime(
                year=int(call_center_row_date_str[0]),
                month=int(call_center_row_date_str[1]),
                day=int(call_center_row_date_str[2]),
            )

            # jsonの"日付"を生成
            querent_hiduke_jsonstr = (
                querent_date.strftime("%Y-%m-%d") + "T08:00:00.000Z"
            )
            # jsonの"date"
            querent_date_jsonstr = querent_date.strftime("%Y-%m-%d")
            # jsonの"short_date"を生成
            querent_short_date_jsonstr = querent_date.strftime("%m/%d")

            querent_row_soudankensu = int(call_center_row["相談件数"].replace(",", ""))

            # querents > dataのデータを生成
            querents_data_json = json.loads(querents_data_json_template)

            querents_data_json["日付"] = querent_hiduke_jsonstr
            querents_data_json["曜日"] = 0
            querents_data_json["9-17時"] = querent_row_soudankensu
            querents_data_json["17-翌9時"] = 0
            querents_data_json["date"] = querent_date_jsonstr
            querents_data_json["w"] = 0
            querents_data_json["short_date"] = querent_short_date_jsonstr
            querents_data_json["小計"] = querent_row_soudankensu

            querent_data_list.append(querents_data_json)

    # ルートのquerents > dataに結合する
    root_json["querents"]["data"].extend(querent_data_list)

    #
    # patients: 陽性者
    #

    filename = "./" + args[1]

    patients_data_list = list()

    with open(filename, "r", encoding="shift-jis") as f1:
        patients_csv = csv.DictReader(f1)

        for patients_row in patients_csv:

            # 日付の正規化
            # TODO:2020-05-30 ここはreでちゃんとバリデーションしておく
            patients_row_date_str = patients_row["公表_年月日"].split("/")

            # 日付:フォーマットが不正なら飛ばす
            if patients_row_date_str[0] == "":
                break

            patients_date = datetime(
                year=int(patients_row_date_str[0]),
                month=int(patients_row_date_str[1]),
                day=int(patients_row_date_str[2]),
            )

            # jsonの"リリース日"を生成
            patients_release_date_jsonstr = (
                patients_date.strftime("%Y-%m-%d") + "T08:00:00.000Z"
            )
            # jsonの"date"
            patients_date_jsonstr = patients_date.strftime("%Y-%m-%d")

            # data_nに個数追加
            date_n.append(patients_date_jsonstr)

            patients_data_json = json.loads(patients_data_json_template)

            patients_data_json["リリース日"] = patients_release_date_jsonstr
            patients_data_json["居住地"] = patients_row["患者_居住地"]
            patients_data_json["年代"] = replace_nendai_format(patients_row["患者_年代"])
            patients_data_json["性別"] = patients_row["患者_性別"]

            # main_summary の必要な情報も取得している
            if patients_row["患者_退院済フラグ"] == "1":
                patients_data_json["退院"] = "〇"
                taiin += 1
            else:
                patients_data_json["退院"] = ""
                nyuin += 1

                if patients_row["患者_状態"] == "軽症・中等症":
                    keisyo += 1
                if patients_row["患者_状態"] == "重症":
                    zyusyo += 1
                if patients_row["患者_状態"] == "死亡":
                    shibo += 1
                    nyuin -= 1

            patients_data_json["date"] = patients_date_jsonstr

            kanzya += 1
            patients_data_list.append(patients_data_json)

    # ルートのpatients > dataに結合する
    root_json["patients"]["data"].extend(patients_data_list)

    #
    # patients_summary: 陽性者サマリー（人数
    #
    
    # startからendまでの毎日の日付と、陽性者数の数を生成する

    # datetimesのstartからendまでのリストを生成
    # TODO:2020-05-31 これは後でも使うので、最初に生成したほうがいいと思う
    date_list = [start + timedelta(days=n) for n in range((end - start).days)]

    # 毎日の日付を生成, 数は0で初期化
    patients_day_of_count_list = {d.strftime("%Y-%m-%d"): 0 for d in date_list}

    # data_n の個数でカウントして、count_listの個数をアップデートさせる
    patients_day_of_count_list.update(Counter(date_n))

    # print(patients_day_of_count_list)

    patients_summary_data_list = list()
    for patients_day, patients_count in patients_day_of_count_list.items():

        # TODO:2020-05-31 わかりづらいので、data_nに入るオブジェクトはdatetimeがいいかも
        patients_hiduke_jsonstr = patients_day + "T08:00:00.000Z"

        # dataの構造を読み込んで生成する
        patients_summary_data_json = json.loads(patients_summary_data_json_template)

        patients_summary_data_json["日付"] = patients_hiduke_jsonstr
        patients_summary_data_json["小計"] = patients_count

        patients_summary_data_list.append(patients_summary_data_json)

    # ルートのpatients_summary > dataに結合する
    root_json["patients_summary"]["data"].extend(patients_summary_data_list)

    with open("data_new.json", "w") as export_json:
        json.dump(root_json, export_json, indent=4, ensure_ascii=False)

    sys.exit(0)

    def daterange(_start, _end):
        for n in range((_end - _start).days):
            yield _start + timedelta(n)

    #
    # inspection_persons
    #
    filename = "./" + args[2]

    # labelsを生成

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
