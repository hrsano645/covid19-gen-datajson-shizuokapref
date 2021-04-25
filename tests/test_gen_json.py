from patients import (
    gen_querents,
    gen_patient,
    gen_patient_summary,
    gen_inspections_summary,
    gen_main_summary,
)
from patients import (
    parse_call_center,
    parse_patients,
    parse_inspections_summary,
    parse_details_of_confirmed_cases,
)

import datetime
import pytest


@pytest.fixture
def load_testdataset():
    dataset = {
        "call_center": parse_call_center("./tests/test_opendata/testdata_call_center.csv"),
        "patients": parse_patients("./tests/test_opendata/testdata_patients.csv"),
        "inspections_summary": parse_inspections_summary(
            "./tests/test_opendata/testdata_test_number.csv"
        ),
        "details_of_confirmed_cases": parse_details_of_confirmed_cases(
            "./tests/test_opendata/testdata_details_of_confirmed_cases.csv"
        ),
    }
    return dataset


def test_gen_querents(load_testdataset):

    querents_jsondata = gen_querents(**load_testdataset)
    assert type(querents_jsondata) == dict
    assert "data" in querents_jsondata.keys()

    querents_datalist = querents_jsondata["data"]
    assert type(querents_datalist) == list

    data_keys = (
        "日付",
        "曜日",
        "9-17時",
        "17-翌9時",
        "date",
        "w",
        "short_date",
        "小計",
    )

    assert tuple(querents_datalist[0].keys()) == data_keys

    # TODO: 2021/02/25 行数確認する


def test_gen_patient(load_testdataset):

    patient_jsondata = gen_patient(**load_testdataset)

    assert type(patient_jsondata) == dict
    assert "data" in patient_jsondata.keys()

    patient_data_list = patient_jsondata["data"]
    assert type(patient_data_list) == list

    data_keys = (
        "リリース日",
        "居住地",
        "年代",
        "性別",
        "退院",
        "date",
    )

    assert tuple(patient_data_list[0].keys()) == data_keys

    # TODO: 2021/02/25 行数確認する


def test_gen_patient_summary(load_testdataset):

    start_datetime = datetime.datetime(2020, 1, 22)

    patient_summary_jsondata = gen_patient_summary(start_datetime, **load_testdataset)

    assert type(patient_summary_jsondata) == dict
    assert "data" in patient_summary_jsondata.keys()

    patient_summary_data_list = patient_summary_jsondata["data"]
    assert type(patient_summary_data_list) == list

    data_keys = (
        "日付",
        "小計",
    )

    assert tuple(patient_summary_data_list[0].keys()) == data_keys

    # TODO: 2021/02/25 行数確認する


def test_gen_inspections_summary(load_testdataset):

    inspections_summary_jsondata = gen_inspections_summary(**load_testdataset)

    # 必要なキーがあるかと、その中の値の型を調べる
    assert type(inspections_summary_jsondata) == dict
    assert "initial_cumulative" in inspections_summary_jsondata.keys()

    initial_cumulative = inspections_summary_jsondata["initial_cumulative"]
    assert "count" in initial_cumulative.keys()
    assert "note" in initial_cumulative.keys()

    assert "data" in inspections_summary_jsondata.keys()
    assert "labels" in inspections_summary_jsondata.keys()

    inspections_summary_data_lists = inspections_summary_jsondata["data"]
    assert type(inspections_summary_data_lists) == dict

    data_keys = (
        "医療機関等",
        "地方衛生研究所",
    )

    assert tuple(inspections_summary_data_lists.keys()) == data_keys

    # TODO: 2021/02/25 行数確認する


def test_gen_main_summary(load_testdataset):

    # 構造を調べる
    main_summary_jsondata = gen_main_summary(**load_testdataset)

    assert type(main_summary_jsondata) == dict

    m_s_d1 = main_summary_jsondata["children"]
    assert type(m_s_d1) == list
    assert len(m_s_d1) == 1

    m_s_d2 = m_s_d1[0]["children"]
    assert type(m_s_d2) == list
    assert len(m_s_d2) == 6

    m_s_d3 = m_s_d2[0]["children"]
    assert type(m_s_d3) == list
    assert len(m_s_d3) == 2
