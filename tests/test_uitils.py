import datetime
from patients import isvalid_opendata_dateformat, validate_dataset, gen_datelist

import pytest

from patients import replace_nendai_format

import random
import csv


# 日付フォーマットのバリデート
@pytest.mark.parametrize(
    "data_str,expected", [("2020/1/1", True), ("/2020/1/1", False)],
)
def test_isvalid_opendata_dadeformat(data_str, expected):
    assert expected == isvalid_opendata_dateformat(data_str)


def test_validate_data():
    # 実際のCSVファイルを元にバリデートをする
    # バリデーション対象のデータ名, 列ヘッダ名と関係するバリデート関数をマッピング

    with open(
        "./tests/test_opendata/testdata_validate_call_center.csv",
        "r",
        encoding="shift-jis",
    ) as test_csv:
        testdata_csv_list = list(csv.DictReader(test_csv))

    result = validate_dataset(
        testdata_csv_list, {"受付_年月日": isvalid_opendata_dateformat}
    )

    assert len(result) == 2
    assert result[0] == "/2020/2/12"
    assert result[1] == "-2020/2/14"


def make_rand_word(length):
    # TODO:2021-02-23 ここの検証はランダム要素になるので、テストの結果が毎回異なる。必要かどうかも含めて検討しなおしたい
    words = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "0",
        "未",
        "年",
        "就",
        "園",
        "学",
        "高",
        "幼",
        "若",
        "中",
        "と",
    ]
    word = ""
    for i in range(length):
        word += words[random.randint(0, len(words) - 1)]
    return word


# 年代の置き換え機能
@pytest.mark.parametrize(
    "input,expected",
    [
        ("高齢でない成人", ""),
        ("高齢者", ""),
        ("未成年（18歳未満）", ""),
        ("若年者", ""),
        ("小児", ""),
        ("未就学児", "10歳未満"),
        ("未就園児", "10歳未満"),
        ("10歳未満", "10歳未満"),
        ("10代", "10代"),
        ("90代", "90代"),
        ("", ""),
        ("不明", "不明"),
        ("XXX", ""),
        (make_rand_word(3), ""),
        (make_rand_word(5), ""),
    ],
)
def test_replace_nendai_format(input, expected):
    assert expected == replace_nendai_format(input)


# 日付のリスト生成
@pytest.mark.parametrize(
    "start,end,expected",
    [
        (datetime.datetime(2021, 1, 1), datetime.datetime(2021, 1, 31), 31),
        (datetime.datetime(2021, 1, 1), datetime.datetime(2021, 12, 31), 365),
    ],
)
def test_gen_datelist(start, end, expected):
    datelist = gen_datelist(start, end)
    assert expected == len(datelist)
