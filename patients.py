# coding:utf-8
import re
import csv
import json
import sys
from collections import Counter, namedtuple
from datetime import datetime, timedelta


# data.jsonのテンプレート
ROOT_JSON_TEMPLATE = """
{
    "querents": {
        "date": "",
        "data": []
    },
    "patients": {
        "date": "",
        "data": []
    },
    "patients_summary": {
        "date": "",
        "data": []
    },
    "inspections_summary": {
        "date": "",
        "initial_cumulative": {
            "note": "2020/04/26まで",
            "count": 0
        },
        "data": {},
        "labels": []
    },
    "lastUpdate": "",
    "main_summary": {}
}
"""

MAIN_SUMMARY_JSON_TEMPLATE = """
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
                    "attr": "宿泊療養",
                    "value": 0
                },
                {
                    "attr": "入院・療養等調整中",
                    "value": 0
                },
                {
                    "attr": "死亡",
                    "value": 0
                },
                {
                    "attr": "退院",
                    "value": 0
                }
            ]
        }
    ]
}
"""

QUERENTS_DATA_JSON_TEMPLATE = """
{
    "日付": "",
    "曜日": 0,
    "9-17時": 0,
    "17-翌9時": 0,
    "date": "",
    "w": 0,
    "short_date": "",
    "小計": 0
}
"""

PATIENTS_DATA_JSON_TEMPLATE = """
{
    "リリース日": "",
    "居住地": "",
    "年代": "",
    "性別": "",
    "退院": "",
    "date": ""
}
"""

PATIENTS_SUMMARY_DATA_JSON_TEMPLATE = """
{
    "日付": "",
    "小計": 0
}
"""


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


def validate_opendata_dateformat(opendata_date_str):
    """
    オープンデータの日付が正しいフォーマットか検証する
    正しいフォーマットならtupleで（year, month, day)を出力する。
    そうでなければNoneを返す
    """

    # 日付の正規化

    dateformat_pattern = re.compile(r"(\d{4})\/(\d{1,2})\/(\d{1,2})")

    validate_result = dateformat_pattern.match(opendata_date_str)

    if not validate_result:
        return None
    else:
        result_ymd = validate_result.groups()
        return (result_ymd[0], result_ymd[1], result_ymd[2])


def gen_datelist(start_datetime, end_datetime):
    """
    日付のリストを生成する。start, endともにdatetimeオブジェクト
    """
    return [
        start_datetime + timedelta(days=n)
        for n in range((end_datetime - start_datetime).days)
    ]


def gen_main_summary_data(details_of_confirmed_cases_filename: str):
    """
    オープンデータを元にmain_summaryの数値を生成する
    ダウンロードしたファイルを読み込み結果を出力

    結果は辞書形式で、「検査陽性者の状況」の項目名をキーとする
    """

    with open(
        details_of_confirmed_cases_filename, "r", encoding="shift-jis"
    ) as details_of_confirmed_cases_file:
        case_count_csv = csv.DictReader(details_of_confirmed_cases_file)

        # コードの参考: https://github.com/aktnk/covid19/issues/44#issue-750619115
        case_count_list = {str(r["コード"]): int(r["人数"]) for r in case_count_csv}

        return {
            "陽性患者数": (
                case_count_list["0"]
                + case_count_list["2"]
                + case_count_list["3"]
                + case_count_list["4"]
                + case_count_list["5"]
            ),  # 陽性患者数 = 入院 + 療養 + 調整中 + 死亡 + 退院
            "入院中": case_count_list["0"],
            "軽症・中等症": case_count_list["0"]
            - case_count_list["1"],  # 軽症・中等症 = 入院中 - うち重症
            "重症": case_count_list["1"],
            "宿泊療養": case_count_list["2"],
            "入院・療養等調整中": case_count_list["3"],
            "死亡": case_count_list["4"],
            "退院": case_count_list["5"],
        }


def main():

    # 時間関係の生成
    dt_now = datetime.now()
    start_datetime = datetime.strptime("2020-01-22", "%Y-%m-%d").date()

    # data_jsonの更新日を生成
    latest_datetime_str = dt_now.replace(
        hour=19, minute=30, second=0, microsecond=0
    ).strftime("%Y/%m/%d %H:%M")

    tomorrow = dt_now + timedelta(days=1)

    # 何らかの終了日？ # TODO:2020-05-30 調査必要
    end_datetime = tomorrow.date()

    # 引数からファイル名を取得
    args = sys.argv
    call_center_filename = "./" + args[2]
    patients_filename = "./" + args[1]
    inspections_summary_filename = "./" + args[3]
    details_of_confirmed_cases_filename = "./" + args[4]

    # main_summary用の変数
    date_n = []  # 陽性者数をカウントする際に利用する

    # data.jsonルートのデータ構造を取得
    root_json = json.loads(ROOT_JSON_TEMPLATE)

    # 各データの更新日を設定
    root_json["querents"]["date"] = latest_datetime_str
    root_json["patients"]["date"] = latest_datetime_str
    root_json["patients_summary"]["date"] = latest_datetime_str
    root_json["inspections_summary"]["date"] = latest_datetime_str
    root_json["lastUpdate"] = latest_datetime_str

    #
    # querents: 検査件数
    #

    querent_data_list = list()
    with open(call_center_filename, "r", encoding="shift-jis") as call_center_file:
        call_center_csv = csv.DictReader(call_center_file)

        for call_center_row in call_center_csv:
            # 日付の正規化

            validate_result_date = validate_opendata_dateformat(
                call_center_row["受付_年月日"]
            )

            if not validate_result_date:
                break

            querent_date = datetime(
                year=int(validate_result_date[0]),
                month=int(validate_result_date[1]),
                day=int(validate_result_date[2]),
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
            querents_data_json = json.loads(QUERENTS_DATA_JSON_TEMPLATE)

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

    patients_data_list = list()
    with open(patients_filename, "r", encoding="shift-jis") as patients_file:
        patients_csv = csv.DictReader(patients_file)

        for patients_row in patients_csv:

            # 日付の正規化
            validate_result_date = validate_opendata_dateformat(patients_row["公表_年月日"])

            if not validate_result_date:
                break

            patients_date = datetime(
                year=int(validate_result_date[0]),
                month=int(validate_result_date[1]),
                day=int(validate_result_date[2]),
            )

            # jsonの"リリース日"を生成
            patients_release_date_jsonstr = (
                patients_date.strftime("%Y-%m-%d") + "T08:00:00.000Z"
            )
            # jsonの"date"
            patients_date_jsonstr = patients_date.strftime("%Y-%m-%d")

            # data_nに個数追加
            date_n.append(patients_date_jsonstr)

            patients_data_json = json.loads(PATIENTS_DATA_JSON_TEMPLATE)

            patients_data_json["リリース日"] = patients_release_date_jsonstr
            patients_data_json["居住地"] = patients_row["患者_居住地"]
            patients_data_json["年代"] = replace_nendai_format(patients_row["患者_年代"])
            patients_data_json["性別"] = patients_row["患者_性別"]

            if patients_row["患者_退院済フラグ"] == "1":
                patients_data_json["退院"] = "〇"
            else:
                # 空白、それ以外の値の場合の場合
                # patients_row["患者_退院済フラグ"] == "0"を含む
                patients_data_json["退院"] = ""

            patients_data_json["date"] = patients_date_jsonstr

            patients_data_list.append(patients_data_json)

    # ルートのpatients > dataに結合する
    root_json["patients"]["data"].extend(patients_data_list)

    #
    # patients_summary: 陽性者サマリー（人数
    #

    # startからendまでの毎日の日付と、陽性者数の数を生成する数は0で初期化
    patients_day_of_count_list = {
        d.strftime("%Y-%m-%d"): 0 for d in gen_datelist(start_datetime, end_datetime)
    }

    # data_n の個数でカウントして、count_listの個数をアップデートさせる
    patients_day_of_count_list.update(Counter(date_n))

    patients_summary_data_list = list()
    for patients_day, patients_count in patients_day_of_count_list.items():

        # TODO:2020-05-31 わかりづらいので、data_nに入るオブジェクトはdatetimeがいいかも
        patients_hiduke_jsonstr = patients_day + "T08:00:00.000Z"

        # dataの構造を読み込んで生成する
        patients_summary_data_json = json.loads(PATIENTS_SUMMARY_DATA_JSON_TEMPLATE)

        patients_summary_data_json["日付"] = patients_hiduke_jsonstr
        patients_summary_data_json["小計"] = patients_count

        patients_summary_data_list.append(patients_summary_data_json)

    # ルートのpatients_summary > dataに結合する
    root_json["patients_summary"]["data"].extend(patients_summary_data_list)

    #
    # inspections_summary: 検査実施件数
    #

    with open(
        inspections_summary_filename, "r", encoding="shift-jis"
    ) as inspections_summary_file:
        inspections_summary_csv = list(csv.DictReader(inspections_summary_file))

        # 1行目は4/26までの累計を記入

        root_json["inspections_summary"]["initial_cumulative"]["count"] = int(
            inspections_summary_csv[0]["検査実施_件数\n（地方衛生研究所）"].replace(",", "")
        ) + int(inspections_summary_csv[0]["検査実施_件数\n（医療機関等）"].replace(",", ""))

        # 2行目以降は日時データとして処理

        # 検査実施件数グラフ の生成:
        # info:2020-06-18: Python3は日本語も引数名で利用できます。python2はできないので注意
        inspections_summary_dataset = dict(医療機関等=list(), 地方衛生研究所=list())
        inspections_summary_labels = list()

        for index, inspections_summary_row in enumerate(inspections_summary_csv[1:]):

            # labelsの生成
            # 日付の正規化
            validate_result_date = validate_opendata_dateformat(
                inspections_summary_row["実施_年月日"]
            )

            if not validate_result_date:
                break

            inspections_summary_date = datetime(
                year=int(validate_result_date[0]),
                month=int(validate_result_date[1]),
                day=int(validate_result_date[2]),
            )
            # pythonの日付書式フォーマットだとゼロ埋めとなるので、一度分解して左側のゼロを消して文字列に戻す（力技です）
            inspections_summary_labels.append(
                "/".join(
                    n_s.lstrip("0")
                    for n_s in inspections_summary_date.strftime("%m/%d").split("/")
                )
            )

            # 件数:検査実施_件数 （医療機関等）の追加
            inspections_summary_dataset["医療機関等"].append(
                int(inspections_summary_row["検査実施_件数\n（医療機関等）"].replace(",", ""))
            )

            # 件数:検査実施_件数 （地方衛生研究所）の追加
            inspections_summary_dataset["地方衛生研究所"].append(
                int(inspections_summary_row["検査実施_件数\n（地方衛生研究所）"].replace(",", ""))
            )

    # データの更新
    root_json["inspections_summary"]["data"].update(inspections_summary_dataset)
    root_json["inspections_summary"]["labels"].extend(inspections_summary_labels)

    #
    # main_summary
    # details_of_confirmed_cases.csvからmain_summaryの数字を生成
    #

    main_summary_root_json = json.loads(MAIN_SUMMARY_JSON_TEMPLATE)

    # データがネスト構造なので、root>d1~d3まで名前をつけて構造を間違えないようにする
    # 検査実施数のネスト
    main_summary_d1 = main_summary_root_json["children"]
    # 用患者数のネスト
    main_summary_d2 = main_summary_d1[0]["children"]
    # 入院中のネスト
    main_summary_d3 = main_summary_d2[0]["children"]

    # 検査実施人数
    # INFO:2020-11-27 この数値は現在利用されていないが互換性のために0を入れておく
    main_summary_root_json["value"] = 0

    # 各数字の生成
    main_summary_counts = gen_main_summary_data(details_of_confirmed_cases_filename)

    # 陽性患者数
    main_summary_d1[0]["value"] = main_summary_counts["陽性患者数"]
    # 入院中
    main_summary_d2[0]["value"] = main_summary_counts["入院中"]
    # 軽症・中等症
    main_summary_d3[0]["value"] = main_summary_counts["軽症・中等症"]
    # 重症
    main_summary_d3[1]["value"] = main_summary_counts["重症"]
    # 宿泊療養
    main_summary_d2[1]["value"] = main_summary_counts["宿泊療養"]
    # 入院・療養等調整中 / 調査中
    main_summary_d2[2]["value"] = main_summary_counts["入院・療養等調整中"]
    # 死亡
    main_summary_d2[3]["value"] = main_summary_counts["死亡"]
    # 退院
    main_summary_d2[4]["value"] = main_summary_counts["退院"]

    # ルートのmain_summaryに結合する
    root_json["main_summary"].update(main_summary_root_json)

    # data.jsonを生成する
    with open("data.json", "w") as export_json:
        json.dump(root_json, export_json, indent="\t", ensure_ascii=False)


if __name__ == "__main__":
    main()
