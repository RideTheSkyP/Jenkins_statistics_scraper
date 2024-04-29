def test_sum():
    assert sum([1, 2, 3]) == 5


def test_count_occurrences():
    assert [1, 2, 3].count(2) == 2


if __name__ == '__main__':
    test_sum()
    test_count_occurrences()
    print('Everything passed')
