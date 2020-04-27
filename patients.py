# coding:utf-8
import csv
import random
import sys
from datetime import datetime
from datetime import timedelta

# 期間
start = datetime.strptime('2020-01-22', '%Y-%m-%d').date()
end   = datetime.strptime('2020-04-15', '%Y-%m-%d').date()



args = sys.argv

filename = './' + args[1]

# 変数
date_n = []
kensa = 0		# 検査実施人数
kanzya = 0		# 陽性患者数
nyuin = 0		# 入院中
keisyo = 0		# 軽症・中症
zyusyo = 0		# 重症
taiin = 0		# 退院
shibo = 0		# 死亡

print( "{" )

filename = './' + args[3]
print( "\t\"querents\": {")
print( "\t\t\"date\": \"2020\/04\/17 23:30\"," )
print( "\t\t\"data\": [" )
with open(filename, 'r') as f3:
	reader = csv.reader(f3)
	header = next(reader)  # 読み込み

	start_flg = 0

	for row in reader:
		date1 = row[0].split("/")

		date20 = date1[ 0 ]
		if len(date1[1] )== 1  :
			date21 = '0' + date1[ 1 ]
		else :
			date21 = date1[ 1 ]

		if len(date1[2] ) == 1  :
			date22 = '0' + date1[ 2 ]
		else :
			date22 = date1[ 2 ]
		date3 = date20 + "-" + date21 + "-" + date22
		date4 = date21 + "\/" + date22

		if start_flg != 0 :
			print( "\t\t\t," )

		row[4] = row[4].replace(",", "")

		print( "\t\t\t{" )
		str2 = "\t\t\t\t\"日付\": " + "\"" + date3 + "T08:00:00.000Z\","
		print(str2)
		str2 = "\t\t\t\t\"曜日\": 0,"
		print(str2)
		str2 = "\t\t\t\t\"9-17時\": " + row[4] + ","
		print(str2)
		str2 = "\t\t\t\t\"17-翌9時\": 0,"
		print(str2)
		str2 = "\t\t\t\t\"date\": " + "\"" + date3 + "\","
		print(str2)
		str2 = "\t\t\t\t\"w\": 0,"
		print(str2)
		str2 = "\t\t\t\t\"short_date\": " + "\"" + date4 + "\","
		print(str2)
		str2 = "\t\t\t\t\"小計\": " + row[4]
		print(str2)
		print( "\t\t\t}" )

		start_flg = 1


print( "\t\t]" )
print( "\t},")


#
# patients
#
filename = './' + args[1]
print( "\t\"patients\": {")
print( "\t\t\"date\": \"2020\/04\/17 23:30\"," )
print( "\t\t\"data\": [" )

with open(filename, 'r') as f:
	reader = csv.reader(f)
	header = next(reader)  # 読み込み

	start_flg = 0

	for row in reader:
		if start_flg != 0 :
			print( "\t\t\t," )

		print( "\t\t\t{" )

		date1 = row[4].split("/")

		date20 = date1[ 0 ]
		if len(date1[1] )== 1  :
			date21 = '0' + date1[ 1 ]
		else :
			date21 = date1[ 1 ]

		if len(date1[2] ) == 1  :
			date22 = '0' + date1[ 2 ]
		else :
			date22 = date1[ 2 ]


		date3 = date20 + "-" + date21 + "-" + date22

		date_n.append( date3 )
		
		str2 = "\t\t\t\t\"リリース日\": " + "\"" + date3 + "T08:00:00.000Z\","
		print(str2)
		str2 = "\t\t\t\t\"居住地\": "  + "\"" + row[6] + "\","
		print(str2)
		str2 = "\t\t\t\t\"年代\": "  + "\"" + row[7] + "\","
		print(str2)
		str2 = "\t\t\t\t\"性別\": "  + "\"" + row[8] + "\","
		print(str2)
		if row[ 10 ] == '軽症・中等症' :
			keisyo = keisyo + 1
		if row[ 10 ] == '重症' :
			zyusyo = zyusyo + 1
		if row[ 10 ] == '重症' :
			shibo = shibo + 1

		if row[13] == '1' :
			str2 = "\t\t\t\t\"退院\": " + "\"〇\","
			taiin = taiin + 1
		else :
			str2 = "\t\t\t\t\"退院\": " + "\"\","
			nyuin = nyuin + 1

		print(str2)
		str2 = "\t\t\t\t\"date\": " + "\"" + date3 + "\"";
		print(str2)

		print( "\t\t\t}" )

		kanzya = kanzya + 1

		start_flg = 1

print( "\t\t]" )
print( "\t},")

#
# patients_summary
#
print( "\t\"patients_summary\": {")
print( "\t\t\"date\": \"2020\/04\/17 23:30\"," )
print( "\t\t\"data\": [" )

def daterange(_start, _end):
    for n in range((_end - _start).days):
        yield _start + timedelta(n)



start_flg = 0

for i in daterange(start, end):
	date_str2 = i.strftime('%Y-%m-%d')
	count = 0
	for date_str in date_n:
		# 一致する文字数をカウント
  		if date_str2 == date_str :
  			count = count + 1

	if start_flg != 0 :
		print( "\t\t\t," )  		

	print( "\t\t\t{" )
	str2 = "\t\t\t\t\"日付\" : \"" + date_str2 + "T08:00:00.000Z\","
	print(str2)
	str2 =  "\t\t\t\t\"小計\" : " + str(count)
	print(str2)
	print( "\t\t\t}" )

	start_flg = 1
#  	print (i)

print( "\t\t]" )
print( "\t},")

#
# inspection_persons
#
filename = './' + args[2]


print( "\t\"inspection_persons\": {" )
print( "\t\t\"date\": \"2020\/04\/17 11:00\"," )
print( "\t\t\"labels\": [" )

start_flg = 0
for i in daterange(start, end):
	date_str2 = i.strftime('%Y-%m-%d')

	if start_flg != 0 :
		print( "\t\t\t\t," )

	str2 = "\t\t\t\t\"" + date_str2 + "T08:00:00.000Z\""
	print(str2)


	start_flg = 1

print( "\t\t]," )
print( "\t\t\"datasets\": [" )
print( "\t\t\t{" )
print( "\t\t\t\t\"label\": \"検査実施人数\"," )
print( "\t\t\t\t\"data\" : [" )

with open(filename, 'r') as f2:
	reader = csv.reader(f2)
	header = next(reader)  # 読み込み

	start_flg = 0
	for row in reader:
		if start_flg != 0 :
			str2 = "\t\t\t\t\t,"
			print( str2 )

		str2 = "\t\t\t\t\t" + row[4]
		print( str2 )
		kensa = kensa + int( row[4] )


		start_flg = 1

print( "\t\t\t\t]" )
print( "\t\t\t}" )
print( "\t\t]" )
print( "\t}," )


#
#
#
print( "\t\"lastUpdate\": \"2020\/04\/17 23:30\"," )
print( "\t\"main_summary\": {" )
print( "\t\t\"attr\": \"検査実施人数\"," )
print( "\t\t\"value\": " + str(kensa) + "," )
print( "\t\t\"children\": [" )
print( "\t\t\t{" )
print( "\t\t\t\t\"attr\": \"陽性患者数\"," )
str2 = "\t\t\t\t\"value\": " + str(kanzya) + ","
print( str2 )
str2 = "\t\t\t\t\"children\": ["
print( str2 )
print( "\t\t\t\t\t{" )
print( "\t\t\t\t\t\t\"attr\": \"入院中\"," )
str2 = "\t\t\t\t\t\t\"value\": " + str(nyuin) + ","
print( str2 )
print( "\t\t\t\t\t\t\"children\": [" )
print( "\t\t\t\t\t\t\t{" );
print( "\t\t\t\t\t\t\t\t\"attr\": \"軽症・中等症\"," )
str2 = "\t\t\t\t\t\t\t\t\"value\": " + str(keisyo)
print( str2 )
print( "\t\t\t\t\t\t\t}," );
print( "\t\t\t\t\t\t\t{" );
print( "\t\t\t\t\t\t\t\t\"attr\": \"重症\"," )
str2 = "\t\t\t\t\t\t\t\t\"value\": " + str(zyusyo)
print( str2 )
print( "\t\t\t\t\t\t\t}" );
print( "\t\t\t\t\t\t]" );
print( "\t\t\t\t\t}," )
print( "\t\t\t\t\t{" )
print( "\t\t\t\t\t\t\"attr\": \"退院\"," )
str2 = "\t\t\t\t\t\t\"value\": " + str(taiin)
print( str2 )
print( "\t\t\t\t\t}," )
print( "\t\t\t\t\t{" )
print( "\t\t\t\t\t\t\"attr\": \"死亡\"," )
str2 = "\t\t\t\t\t\t\"value\": " + str(shibo)
print( str2 )
print( "\t\t\t\t\t}" )
print( "\t\t\t\t]" )
print( "\t\t\t}" )
print( "\t\t]" )
print( "\t}" )

print( "}" )
