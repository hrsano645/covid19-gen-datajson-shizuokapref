# data.jsonのテンプレート
ROOT = """
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

MAIN_SUMMARY = """
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

QUERENTS_DATA = """
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

PATIENTS_DATA = """
{
    "リリース日": "",
    "居住地": "",
    "年代": "",
    "性別": "",
    "退院": "",
    "date": ""
}
"""

PATIENTS_SUMMARY_DATA = """
{
    "日付": "",
    "小計": 0
}
"""
