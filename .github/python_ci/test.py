
# test_show.py
import pytest


def test_sample1():
    assert 1 == 1


def test_sample2():
    assert [1, 2, 3] != [3, 2, 1]


@pytest.mark.xfail()
def test_sample3():
    assert 1 != 1


@pytest.mark.xfail()
def test_sample4():
    assert 1 == 1