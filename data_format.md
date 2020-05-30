# 各種データの定義

このドキュメントは静岡県のオープンデータの各種情報と、オープンデータから生成したdata.jsonのフォーマットについて扱っています。

※:このドキュメントはWork in Progressです。内容について間違いがあれば issueに登録お願いします。

## オープンデータ側

データ公開先: [新型コロナウイルス感染症県内感染動向 - 静岡県オープンデータ](https://opendata.pref.shizuoka.jp/dataset/8167.html)

### call_center.csv

県内における新型コロナウイルス感染症の相談件数

#### data.json側で利用されている部分

- main_summary
- querents

### patients.csv

県内における新型コロナウイルス感染症の感染動向

#### data.json側で利用されている部分

- main_summary
- patients
- patients_summary 

### test_people.csv

静岡県内における新型コロナウイルス感染症の検査人数

- main_summary
- inspection_persons

#### data.json側で利用されている部分

## data.jsonの構造

対応するカードも明記すること

### data.json ルート

```json

{
	"querents": {	}, // 新型コロナ受診相談窓口相談件数
	"patients": {	}, // 陽性者
	"patients_summary": {	}, // 陽性者サマリー（人数
	"inspection_persons": {	}, // 検査実施人数（グラフを重ね合わせ可能
	"lastUpdate": "2020\/05\/30 19:30", // data.jsonの更新日
	"main_summary": {} // 検査陽性者の状況
}

```

### lastUpdate: data.jsonの更新日

```json
	"lastUpdate": "2020\/05\/30 19:30" // 日付は "yyyy/mm/dd hh:mm"
```

### main_summary: 検査陽性者の状況

```json

	"main_summary": {
		"attr": "検査実施人数",
		"value": 0, // int
		"children": [
			{
				"attr": "陽性患者数",
				"value": 0, // int
				"children": [
					{
						"attr": "入院中",
						"value": 3, // int
						"children": [
							{
								"attr": "軽症・中等症",
								"value": 3 // int
							},
							{
								"attr": "重症",
								"value": 0 // int
							}
						]
					},
					{
						"attr": "退院",
						"value": 72 // int
					},
					{
						"attr": "死亡",
						"value": 1 // int
					}
				]
			}
		]
	}

```

### querents: 新型コロナ受診相談窓口相談件数

```json
"querents": {
    "date": "2020\/05\/30 19:30", // data.json更新日
    "data": [ // 実際のデータ 毎日一つ追加
        {
            "日付": "2020-02-10T08:00:00.000Z", // 検査日
            "曜日": 0, // メトロ版にある項目だが用途不明
            "9-17時": 0, // メトロ版にある項目だが用途不明
            "17-翌9時": 0, // メトロ版にある項目だが用途不明
            "date": "2020-02-10", // 日付 yyyy-mm-dd 表記
            "w": 0, // メトロ版にある項目だが用途不明
            "short_date": "02\/10", // 日付　mm/dd 表記
            "小計": 0 // int:検査件数
        },
    ]
},
```

### patients: 陽性者の属性

```json
"patients": {
    "date": "2020\/05\/30 19:30", // data.json更新日
    "data": [ // 実際のデータ 陽性者の数だけ追加される
        {
            "リリース日": "2020-02-28T08:00:00.000Z", // 陽性者の発表時, 日時は被ることもある
            "居住地": "静岡市", // 居住地
            "年代": "60代", // 年代, メトロ版は00年代 というフォーマットだが、静岡県は例外あり
            "性別": "男性", // 性別
            "退院": "〇",  // 退院している場合は〇が付く
            "date": "2020-02-28" // 日付 yyyy-mm-dd 表記
        },
    ]
},
```

### patients_summary: 陽性者サマリー（人数

```json
"patients_summary": { // data.json更新日
    "date": "2020\/05\/30 19:30", // 検査日
    "data": [ // 実際のデータ 毎日一つ追加
        {
            "日付": "2020-01-22T08:00:00.000Z", // 陽性者の発表時
            "小計": 0 // 検査人数の日ごとの合計
        },
    ]
},
```


### inspection_persons: 検査実施人数（グラフを重ね合わせ可能

重ね合わせが可能なデータ構造のようです。

```json
"inspection_persons": {
    "date": "2020\/05\/30 19:30", // data.json更新日
    "labels": [ // 複数データの統合されたラベル, 基本的に日付
        "2020-01-22T08:00:00.000Z",
    ],
    "datasets": [
        {
            "label": "検査実施人数", // データセットのデータの意味
            "data": [ // データセットのデータ, labelsと個数は一致する必要あり
                0, // int:データ
            ]
        }
    ]
},
```

## ほかにやること

inspections_summary（検査実施件数）の追加が必要 [#1](https://github.com/hrsano645/covid19-gen-datajson-shizuokapref/issues/1)