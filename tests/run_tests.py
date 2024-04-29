def test_sum():
    assert sum([1, 2, 3]) == 6


def test_len():
    assert len([1, 2, 3]) == 2


if __name__ == '__main__':
    test_sum()
    test_len()
    print('Everything passed')
