import pytest
from django.template.defaultfilters import truncatewords
from django.utils.timesince import timesince
from model_bakery import baker
from pytest_django.asserts import assertContains

from tests import conftest


@pytest.mark.django_db
def test_echo_list_page_contains_expected_echo_information(client, user):
    echos = baker.make_recipe('tests.echo', _quantity=10)

    client.force_login(user)
    response = client.get(conftest.ECHO_LIST_URL)
    assert response.status_code == 200
    for echo in echos:
        assertContains(response, truncatewords(echo.content, 20))
        assertContains(response, echo.user.username)
        assertContains(response, f'/users/{echo.user.username}/')
        assertContains(response, conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk))
        assertContains(response, timesince(echo.created_at))