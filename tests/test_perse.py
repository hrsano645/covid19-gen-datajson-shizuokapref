from patients import (
    parse_call_center,
    parse_patients,
    parse_inspections_summary,
    parse_details_of_confirmed_cases,
)


def test_column_count_parse_call_center():
    load_matrix = parse_call_center("./tests/test_opendata/testdata_call_center.csv")
    # ファイルの列数
    assert 5 == len(load_matrix[0])


def test_column_count_parse_patients():

    load_matrix = parse_patients("./tests/test_opendata/testdata_patients.csv")
    # ファイルの列数
    assert 17 == len(load_matrix[0])


def test_column_count_parse_inspections_summary():

    load_matrix = parse_inspections_summary("./tests/test_opendata/testdata_test_number.csv")
    # ファイルの列数
    assert 6 == len(load_matrix[0])


def test_parse_details_of_confirmed_cases():
    main_summary_counts = parse_details_of_confirmed_cases(
        "./tests/test_opendata/testdata_details_of_confirmed_cases.csv"
    )

    # 陽性患者数 = 入院 + 療養 + 調整中 + 死亡 + 退院
    assert main_summary_counts["陽性患者数"] == 5082
    assert main_summary_counts["入院中"] == 92
    # 軽症・中等症 = 入院中 - うち重症
    assert main_summary_counts["軽症・中等症"] == 91
    assert main_summary_counts["重症"] == 1
    assert main_summary_counts["宿泊療養"] == 50
    assert main_summary_counts["自宅療養"] == 69
    assert main_summary_counts["入院等調整中"] == 17
    assert main_summary_counts["死亡"] == 93
    assert main_summary_counts["退院"] == 4761

