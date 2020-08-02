from patients import validate_opendata_dateformat


def test_correct():
    assert ("2020", "1", "1") == validate_opendata_dateformat("2020/1/1")


def test_notcorrect():
    assert None == validate_opendata_dateformat("/2020/1/1")
