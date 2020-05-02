from patients import replace_nendai_format

import random
import sys
dic = ["1","2","3","4","5","6","7","8","9","0","未","年","就","園","学","高","幼","若","中","と"]

def make_word(length,words):
    word = ""
    for i in range(length):
        word += words[random.randint(0,len(words)-1)]
    return word

def test_koureidenaiseijin():
    assert "" == replace_nendai_format("高齢でない成人")

def test_koureisya():
    assert "" == replace_nendai_format("高齢者")

def test_miseinei():
    assert "" == replace_nendai_format("未成年（18歳未満）")

def test_jyakunensya():
    assert "" == replace_nendai_format("若年者")

def test_syouni():
    assert "" == replace_nendai_format("小児")

def test_misyuugakuji():
    assert "10歳未満" == replace_nendai_format("未就学児")

def test_misyuuennji():
    assert "10歳未満" == replace_nendai_format("未就園児")

def test_10saimiman():
    assert "10歳未満" == replace_nendai_format("10歳未満")

def test_10dai():
    assert "10代" == replace_nendai_format("10代")

def test_20dai():
    assert "90代" == replace_nendai_format("90代")

def test_null():
    assert "" == replace_nendai_format("")

def test_fumei():
    assert "不明" == replace_nendai_format("不明")

def test_xxx():
    assert "" == replace_nendai_format("XXX")

def test_randam3():
    assert "" == replace_nendai_format(make_word(3,dic))

def test_randam5():
    assert "" == replace_nendai_format(make_word(5,dic))