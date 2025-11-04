from pytest_django.asserts import assertContains


def test_index_page_contains_expected_elements(client):
    response = client.get('/')
    assert response.status_code == 200
    assertContains(response, 'Tribu')
