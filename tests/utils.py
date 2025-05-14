"""
Helpers for testing
"""

from typing import Union

import numpy.testing as npt

EPS = 10e-5


def listit(to_convert: Union[list, tuple]) -> list:
    """Convert a nested tuple of tuples/lists into a list of lists"""
    return list(map(listit, to_convert)) if isinstance(to_convert, (list, tuple)) else to_convert


def nested_dict_allclose(actual, expected):
    """Recursively compare two nested dicts. Iterates over values and if they are lists, checks their (near) equality
    using nested_list_allclose function. The rest of the values are compared directly"""
    assert actual.keys() == expected.keys()
    order = list(actual.keys())
    for k in order:
        actual_item = actual[k]
        expected_item = expected[k]
        if isinstance(actual_item, list):
            nested_list_allclose(actual_item, expected_item)
        elif isinstance(actual_item, dict):
            nested_allclose(actual_item, expected_item)
        else:
            assert actual_item == expected_item


def nested_list_allclose(actual, expected):
    """Recursively compare two nested lists. Iterates over values and if they are lists, checks their (near) equality
    using numpy.testing.allclose. If the values are dicts, passes them to the nested_dict_allclose"""
    try:
        npt.assert_allclose(actual, expected)
    except TypeError:
        pass
    for actual_item, expected_item in zip(actual, expected):
        if isinstance(actual_item, dict):
            nested_dict_allclose(actual_item, expected_item)
        elif isinstance(actual_item, list):
            nested_list_allclose(actual_item, expected_item)
        elif isinstance(actual_item, str):
            assert actual_item == expected_item
        else:
            npt.assert_allclose(actual_item, expected_item, atol=EPS)


def nested_allclose(actual: Union[dict, list, tuple], expected: Union[dict, list, tuple]):
    """Compares two nested tuple/list/dict. Numerical values are compared using np.testing.allclose"""
    assert len(actual) == len(expected)
    if isinstance(actual, tuple):
        actual = listit(actual)
        expected = listit(expected)
    assert type(actual) is type(expected)  # If expected parsed from json it cant be tuple

    if isinstance(actual, dict):
        nested_dict_allclose(actual, expected)
    elif isinstance(actual, list):
        try:
            npt.assert_allclose(actual, expected, atol=EPS)
        except TypeError:
            nested_list_allclose(actual, expected)
    else:
        raise ValueError("Please pass dictionary, tuple or list to test")
