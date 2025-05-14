"""
Additional functions for loading examples
"""

from os import path
from pathlib import Path
from typing import List

import pytest
from _pytest.mark import ParameterSet

from src.utils import json_load

data = json_load(Path(path.dirname(path.realpath(__file__)), 'data.json'))


def load_examples(
    testable_name: str,
    keys: List[str] = None
) -> List[ParameterSet]:
    """
    Load testing examples from dictionary(data).
    dictionary has a unique structure.

    {'testable_name':
        [{'example':some_example,'expected':expected_result,'status_code}]

    Parameters
    ----------
    testable_name: str
        name of the fist key (endpoint or function name)
    keys: list
        keys to parse from the examples

    Returns
    -------
    examples: list of dataclass
        list with examples and their expected results

    """
    test_case_id_name = "test_case_id"
    try:
        testable_examples = data.get(testable_name)
        if keys is None:
            keys = list(testable_examples[0].keys())
            if test_case_id_name in keys:
                keys.remove(test_case_id_name)
        examples = []
        for item in testable_examples:
            example = []
            for key in keys:
                if len(keys) == 1:
                    example = [item.get(key)]
                elif len(keys) > 1:
                    example.append(item.get(key))
                else:
                    raise ValueError
            example = pytest.param(*example,
                                   id=item.get(test_case_id_name, None))
            examples.append(example)
        return examples
    except KeyError as e:
        raise ValueError(f'Cannot parse examples:{str(e)}') from e
