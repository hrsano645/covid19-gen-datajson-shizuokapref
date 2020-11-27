from patients import gen_main_summary_data

# {
#     "陽性患者数": (
#         case_count_list["0"]
#         + case_count_list["2"]
#         + case_count_list["3"]
#         + case_count_list["4"]
#         + case_count_list["5"]
#     ),  # 陽性患者数 = 入院 + 療養 + 調整中 + 死亡 + 退院
#     "入院中": case_count_list["0"],
#     "軽症・中等症": case_count_list["0"]
#     - case_count_list["1"],  # 軽症・中等症 = 入院中 - うち重症
#     "重症": case_count_list["1"],
#     "宿泊療養": case_count_list["2"],
#     "入院・療養等調整中": case_count_list["3"],
#     "死亡": case_count_list["4"],
#     "退院": case_count_list["5"],
# }


def test_gen_main_summary_data():

    main_summary_counts = gen_main_summary_data("./details_of_confirmed_cases.csv")

    # 陽性患者数 = 入院 + 療養 + 調整中 + 死亡 + 退院
    assert main_summary_counts["陽性患者数"] == 1334
    assert main_summary_counts["入院中"] == 115
    # 軽症・中等症 = 入院中 - うち重症
    assert main_summary_counts["軽症・中等症"] == 111
    assert main_summary_counts["重症"] == 4
    assert main_summary_counts["宿泊療養"] == 66
    assert main_summary_counts["入院・療養等調整中"] == 289
    assert main_summary_counts["死亡"] == 4
    assert main_summary_counts["退院"] == 860

