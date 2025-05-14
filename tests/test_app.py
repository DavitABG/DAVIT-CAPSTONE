"""
API integration testing
"""

import pytest
from fastapi import status

from tests.data_parser import load_examples


def test_check_status(client):
    response = client.get(f'/health/check_status')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize('example, expected', load_examples(testable_name='example_endpoint_happy_path'))
def test_chat_happy_path(client, example, expected):
    response = client.post(f'/example_router/example_post', json=example)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected
