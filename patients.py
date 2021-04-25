# coding:utf-8
import re
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


def replace_nendai_format(src: str) -> str:
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


def isvalid_opendata_dateformat(opendata_date_str: str) -> bool:
    """
    オープンデータの日付が正しいフォーマットか検証する。boolで結果を返す
    """
    dateformat_pattern = re.compile(r"(\d{4})\/(\d{1,2})\/(\d{1,2})")

    validate_result = dateformat_pattern.match(opendata_date_str)

    if validate_result:
        return True
    else:
        return False


# バリデート結果でエラーを出すためのクラス
class ValidateError(Exception):
    """ バリデートエラーの基底クラス """

    pass


class DateValidateError(ValidateError):
    """
    日付のエラーを出すときの例外クラス
    """

    pass


def gen_datelist(start_datetime: datetime, end_datetime: datetime) -> list:
    """
    startからendまでの日付オブジェクトを生成するしてリストで返す
    start_datetime, end_datetimeともにdatetimeオブジェクト
    """
    return [
        start_datetime + timedelta(days=n)
        for n in range((end_datetime - start_datetime).days + 1)
    ]


def suppress_zero(target_datetime: datetime) -> str:
    """
    pythonの日付書式フォーマットだとゼロ埋めとなるので、一度分解して左側のゼロを消して文字列に戻す（力技です）
    """

    return "/".join(
        n_s.lstrip("0") for n_s in target_datetime.strftime("%Y/%m/%d").split("/")
    )


def gen_jsonformat_datetime(t_datetime: datetime) -> str:
    """
    datetimeオブジェクトをjsonの日付フォーマットに変換する
    """
    return t_datetime.strftime("%Y-%m-%d") + "T08:00:00.000Z"


# オープンデータの読み込みとパース処理
def parse_details_of_confirmed_cases(filename: str) -> dict:
    """
    オープンデータを元にmain_summary用の数値を生成する
    ダウンロードしたファイルを読み込み結果を出力

    結果は辞書形式で、「検査陽性者の状況」の項目名をキーとする

    コードとコードの意味との対応一覧
    ----

    入院: 0
    うち重症: 1
    宿泊療養: 2
    自宅療養: 3
    入院等調整中: 4
    死亡: 5
    退院: 6
    """

    with open(filename, "r", encoding="shift-jis") as details_of_confirmed_cases_file:
        case_count_csv = list(csv.DictReader(details_of_confirmed_cases_file))

        # 読み込むCSVファイルの行数を指定
        case_count_list = {str(r["コード"]): int(r["人数"]) for r in case_count_csv[:7]}

        return {
            # 陽性患者数 = 入院 + 療養 + 調整中 + 死亡 + 退院
            "陽性患者数": sum(
                (
                    case_count_list["0"],
                    case_count_list["2"],
                    case_count_list["3"],
                    case_count_list["4"],
                    case_count_list["5"],
                    case_count_list["6"],
                )
            ),
            "入院中": case_count_list["0"],
            # 軽症・中等症 = 入院中 - うち重症
            "軽症・中等症": case_count_list["0"] - case_count_list["1"],
            "重症": case_count_list["1"],
            "宿泊療養": case_count_list["2"],
            "自宅療養": case_count_list["3"],
            "入院等調整中": case_count_list["4"],
            "死亡": case_count_list["5"],
            "退院": case_count_list["6"],
        }


def parse_call_center(filename):
    """
    call_center.csvを読み込んで表データを作成する
    """
    with open(filename, "r", encoding="shift-jis") as call_center_file:
        return list(csv.DictReader(call_center_file))


def parse_inspections_summary(filename):

    """
    inspections_summary.csvを読み込んで表データを作成する
    """
    with open(filename, "r", encoding="shift-jis") as inspections_summary_file:
        return list(csv.DictReader(inspections_summary_file))


def parse_patients(filename):

    """
    patients.csvを読み込んで表データを作成する
    """
    with open(filename, "r", encoding="shift-jis") as patients_file:

        # INFO:2021-01-30: issue#39参照 オープンデータ側に説明情報が追加されているのでその行数を無視する
        for _ in range(8):
            next(patients_file)

        return list(csv.DictReader(patients_file))


def validate_dataset(csv_list: list, func_map: dict) -> list:
    """
    オープンデータのバリデーションを行う。エラーを起こしている該当の文字列。
    複数のバリデートに対応する。func_mapは辞書形式で、CSVファイルの列ラベルとバリデート関数を指定する必要がある

    >>> func_map = {"公表_年月日": isvalid_opendata_dateformat}
    """
    validate_errors = list()

    for row_header, validate_func in func_map.items():
        for row in csv_list:
            if not validate_func(row[row_header]):
                validate_errors.append(row[row_header])

    return validate_errors


def gen_querents(**dataset) -> dict:
    """
    data.json > querents: 検査件数のデータを生成する。
    """

    # datasetに必要なデータがない場合にはNoneを返す
    if "call_center" not in dataset:
        return None
    call_center = dataset["call_center"]

    querents_data_json_template = """
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

    querent_data_list = list()
    for call_center_row in call_center:

        querent_date = datetime.strptime(call_center_row["受付_年月日"], "%Y/%m/%d")

        # querents > dataのデータを生成
        querents_data_item = json.loads(querents_data_json_template)

        querents_data_item["日付"] = gen_jsonformat_datetime(querent_date)
        querents_data_item["曜日"] = 0
        querents_data_item["9-17時"] = int(call_center_row["相談件数"].replace(",", ""))
        querents_data_item["17-翌9時"] = 0
        querents_data_item["date"] = querent_date.strftime("%Y-%m-%d")
        querents_data_item["w"] = 0

        querents_data_item["short_date"] = querent_date.strftime("%m/%d")
        querents_data_item["小計"] = int(call_center_row["相談件数"].replace(",", ""))

        querent_data_list.append(querents_data_item)

    return dict(data=querent_data_list)


def gen_patient(**dataset) -> dict:
    """
    data.json > patients: 陽性者のデータを生成する
    """

    # datasetに必要なデータがない場合にはNoneを返す
    if "patients" not in dataset:
        return None
    patients = dataset["patients"]

    patients_data_json_template = """
    {
        "リリース日": "",
        "居住地": "",
        "年代": "",
        "性別": "",
        "退院": "",
        "date": ""
    }
    """

    patients_data_list = list()
    for patients_row in patients:

        patients_date = datetime.strptime(patients_row["公表_年月日"], "%Y/%m/%d")

        patients_data_item = json.loads(patients_data_json_template)

        patients_data_item["リリース日"] = gen_jsonformat_datetime(patients_date)
        patients_data_item["居住地"] = patients_row["患者_居住地"]
        patients_data_item["年代"] = replace_nendai_format(patients_row["患者_年代"])
        patients_data_item["性別"] = patients_row["患者_性別"]
        patients_data_item["date"] = patients_date.strftime("%Y-%m-%d")

        if patients_row["患者_退院済フラグ"] == "1":
            patients_data_item["退院"] = "〇"
        else:
            # 空白、それ以外の値の場合の場合
            # patients_row["患者_退院済フラグ"] == "0"を含む
            patients_data_item["退院"] = ""

        patients_data_list.append(patients_data_item)

    return dict(data=patients_data_list)


def gen_patient_summary(start_dt, **dataset) -> dict:
    """
    data.json > patients_summary: 陽性者サマリー（人数
    """

    # TODO: 2021/02/25 startの日付は現在は固定の日付だが、グラフの開始日になるのでpatientsの最初の日付に変更する
    #   issue#https://github.com/aktnk/covid19/issues/68 にて対応予定

    # datasetに必要なデータがない場合にはNoneを返す
    if "patients" not in dataset:
        return None
    patients = dataset["patients"]

    # グラフの終了日時を生成
    end_datetime = datetime.strptime(dataset["patients"][-1]["公表_年月日"], "%Y/%m/%d")

    patients_summary_data_json_template = """
    {
        "日付": "",
        "小計": 0
    }
    """

    # patientsから日付のみを取り出す
    patients_date_list = list()
    for patients_row in patients:

        patients_date_list.append(datetime.strptime(patients_row["公表_年月日"], "%Y/%m/%d"))

    # 日ごとの陽性者数をカウントしてリスト作成
    patients_day_of_count_list = {d: 0 for d in gen_datelist(start_dt, end_datetime)}
    patients_day_of_count_list.update(Counter(patients_date_list))

    # jsonデータの生成
    patients_summary_data_list = list()
    for patients_day, patients_count in patients_day_of_count_list.items():

        # dataの構造を読み込んで生成する
        patients_summary_data_item = json.loads(patients_summary_data_json_template)

        patients_summary_data_item["日付"] = gen_jsonformat_datetime(patients_day)
        patients_summary_data_item["小計"] = patients_count

        patients_summary_data_list.append(patients_summary_data_item)

    return dict(data=patients_summary_data_list)


def gen_inspections_summary(**dataset) -> dict:
    """
    data.json > inspections_summary: 検査実施人数のデータを生成する
    """

    # TODO:2021-02-23 このinspection_summaryが対策サイトとの名称通りかを確認する。（オープンデータファイル名としてはtest_numberとなってる）
    # datasetに必要なデータがない場合にはNoneを返す
    if "inspections_summary" not in dataset:
        return None
    inspections_summary = dataset["inspections_summary"]

    inspection_summary_data_json_template = """
    {
            "initial_cumulative": {
                "note": "2020/04/26まで",
                "count": 0
            },
            "data": {},
            "labels": []
    }
    """

    inspections_summary_jsondata = json.loads(inspection_summary_data_json_template)

    # 1行目は4/26までの累計を記入
    inspections_summary_jsondata["initial_cumulative"]["count"] = int(
        inspections_summary[0]["検査実施_人数\n（医療機関等）"].replace(",", "")
    ) + int(inspections_summary[0]["検査実施_人数\n（保健所）"].replace(",", ""))

    # 2行目以降は日時データとして処理
    # INFO:2020-06-18: Python3は日本語も引数名で利用できます。python2はできないので注意
    inspections_summary_data = dict(医療機関等=list(), 地方衛生研究所=list())
    inspections_summary_labels = list()

    for inspections_summary_row in inspections_summary[1:]:

        # labelsの生成
        inspections_summary_date = datetime.strptime(
            inspections_summary_row["実施_年月日"], "%Y/%m/%d"
        )

        inspections_summary_labels.append(suppress_zero(inspections_summary_date))

        # 件数の追加
        inspections_summary_data["医療機関等"].append(
            int(inspections_summary_row["検査実施_人数\n（医療機関等）"].replace(",", ""))
        )
        inspections_summary_data["地方衛生研究所"].append(
            int(inspections_summary_row["検査実施_人数\n（保健所）"].replace(",", ""))
        )

    inspections_summary_jsondata["data"] = inspections_summary_data
    inspections_summary_jsondata["labels"] = inspections_summary_labels

    return inspections_summary_jsondata


def gen_main_summary(**dataset) -> dict:
    """
    data.json > main_summary 検査陽性者の状況のデータを生成する
    """

    # datasetに必要なデータがない場合にはNoneを返す
    if "details_of_confirmed_cases" not in dataset:
        return None
    details_of_confirmed_cases = dataset["details_of_confirmed_cases"]

    # テンプレート読み込み
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
                        "attr": "宿泊療養",
                        "value": 0
                    },
                    {
                        "attr": "自宅療養",
                        "value": 0
                    },
                    {
                        "attr": "入院等調整中",
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

    main_summary_root_json = json.loads(main_summary_json_template)

    # データがネスト構造なので、root>d1~d3まで名前をつけて構造を間違えないようにする
    # 検査実施数のネスト
    main_summary_d1 = main_summary_root_json["children"]
    # 用患者数のネスト
    main_summary_d2 = main_summary_d1[0]["children"]
    # 入院中のネスト
    main_summary_d3 = main_summary_d2[0]["children"]

    # 数値の入力
    # INFO:2020-11-27 この数値は現在利用されていないが互換性のために0を入れておく
    main_summary_root_json["value"] = 0

    main_summary_d1[0]["value"] = details_of_confirmed_cases["陽性患者数"]
    main_summary_d2[0]["value"] = details_of_confirmed_cases["入院中"]
    main_summary_d3[0]["value"] = details_of_confirmed_cases["軽症・中等症"]
    main_summary_d3[1]["value"] = details_of_confirmed_cases["重症"]
    main_summary_d2[1]["value"] = details_of_confirmed_cases["宿泊療養"]
    main_summary_d2[2]["value"] = details_of_confirmed_cases["自宅療養"]
    main_summary_d2[3]["value"] = details_of_confirmed_cases["入院等調整中"]
    main_summary_d2[4]["value"] = details_of_confirmed_cases["死亡"]
    main_summary_d2[5]["value"] = details_of_confirmed_cases["退院"]

    # ルートのmain_summaryに結合する
    return dict(main_summary_root_json)


def main():

    # TODO: 2021/02/19 latest（更新日時）は全て統一ではなく、それぞれのカードに関係するjson側の更新側で行う
    # data_jsonの更新日を生成
    latest_datetime_str = (
        datetime.now()
        .replace(hour=19, minute=30, second=0, microsecond=0)
        .strftime("%Y/%m/%d %H:%M")
    )

    # TODO: start_datetimeは実際にgen_patient_summaryにしか使っていないため、ここで生成させる必要はないかも
    start_datetime = datetime.strptime("2020-01-22", "%Y-%m-%d")

    # 引数からファイル名を取得
    args = sys.argv

    # ---[データセットの作成]---
    # データのみをdatasetとしてまとめる
    dataset = {
        "call_center": parse_call_center("./" + args[2]),
        "patients": parse_patients("./" + args[1]),
        "inspections_summary": parse_inspections_summary("./" + args[3]),
        "details_of_confirmed_cases": parse_details_of_confirmed_cases("./" + args[4]),
    }

    # ---[各データセットのバリデーション]---
    # バリデーション用のデータセットを作成、データセットの不要なデータを除去
    _dataset = dataset.copy()
    _dataset.pop("details_of_confirmed_cases")
    # 検査実施件数の最初の行を外したリストを生成
    _dataset["inspections_summary"] = dataset["inspections_summary"][1:]

    # バリデーション対象のデータ名, 列ヘッダ名と関係するバリデート関数を辞書でマッピング
    validate_funcmaps = {
        "call_center": {"受付_年月日": isvalid_opendata_dateformat},
        "patients": {"公表_年月日": isvalid_opendata_dateformat},
        "inspections_summary": {"実施_年月日": isvalid_opendata_dateformat},
    }

    error_msg_body = ""
    for data_name, funcmaps in validate_funcmaps.items():
        # バリデーションのマップを元に対象の列名と関数を処理
        validate_errors = validate_dataset(_dataset[data_name], funcmaps)
        if validate_errors:
            for error_str in validate_errors:
                error_msg_body += "{}: {}\n".format(data_name, error_str)

    if error_msg_body:
        error_msg = "バリデーションの結果、処理出来ない行があります。処理を終了します。\n"
        error_msg += error_msg_body
        raise DateValidateError(error_msg)

    # ---[地域別フィルタ]---
    local_name = None
    if len(args) == 6:
        local_name = args[5]

    # INFO:2021-03-09 patientsのみフィルター
    if local_name == "静岡県" or local_name is None:
        print("静岡県の陽性者属性情報の一覧を生成します")
    elif local_name in set([row["患者_居住地"] for row in dataset["patients"]]):
        dataset["patients"] = [
            row for row in dataset["patients"] if row["患者_居住地"] == local_name
        ]
        print("{}の陽性者属性情報の一覧を生成します".format(local_name))
    else:
        print(
            "指定の地域名「{}」では陽性者属性の情報が見つかりませんでした。処理を終了します。".format(local_name),
            file=sys.stderr,
        )
        exit(1)

    # ---[data.json生成]---
    querents_jsondata = gen_querents(**dataset)
    patient_jsondata = gen_patient(**dataset)
    patient_summary_jsondata = gen_patient_summary(start_datetime, **dataset)
    inspections_summary_jsondata = gen_inspections_summary(**dataset)
    main_summary_jsondata = gen_main_summary(**dataset)

    # data.jsonルートのデータ構造を取得
    root_json_template = """
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
            "date": ""
        },
        "lastUpdate": "",
        "main_summary": {}
    }
    """
    root_json = json.loads(root_json_template)

    # 各データの更新日を設定
    root_json["querents"]["date"] = latest_datetime_str
    root_json["patients"]["date"] = latest_datetime_str
    root_json["patients_summary"]["date"] = latest_datetime_str
    root_json["inspections_summary"]["date"] = latest_datetime_str
    root_json["lastUpdate"] = latest_datetime_str

    # 各データの更新を行う
    root_json["querents"].update(querents_jsondata)
    root_json["patients"].update(patient_jsondata)
    root_json["patients_summary"].update(patient_summary_jsondata)
    root_json["inspections_summary"].update(inspections_summary_jsondata)
    root_json["main_summary"].update(main_summary_jsondata)

    # data.jsonを生成する
    with open("data.json", "w") as export_json:
        json.dump(root_json, export_json, indent="\t", ensure_ascii=False)


if __name__ == "__main__":
    main()
