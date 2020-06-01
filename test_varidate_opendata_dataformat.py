from patients import varidate_opendata_dateformat


def test_correct():
    assert ("2020", "1", "1") == varidate_opendata_dateformat("2020/1/1")


def test_notcorrect():
    assert None == varidate_opendata_dateformat("/2020/1/1")
