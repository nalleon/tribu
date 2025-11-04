from pytest_django.asserts import assertContains

from tests import conftest


def test_index_contains_title(client):
    response = client.get('/')
    assert response.status_code == 200
    assertContains(response, 'Tribu')


def test_index_contains_link_to_echo_list(client):
    response = client.get('/')
    assert response.status_code == 200
    assertContains(response, conftest.ECHO_LIST_URL)
