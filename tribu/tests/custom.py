import pytest
from django.template.defaultfilters import truncatewords
from django.utils.timesince import timesince
from model_bakery import baker
from pytest_django.asserts import assertContains, assertNotContains

from echos.models import Echo
from tests import conftest





@pytest.mark.django_db
def test_echo_waves_page_requires_authentication(client, user, echo):
    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f'/login/?next={url}'

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_echo_waves_page_contains_expected_echo_information(client, user, echo):
    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertContains(response, echo.content)
    assertContains(response, echo.user.username)
    assertContains(response, conftest.USER_DETAIL_URL.format(username=echo.user.username))
    assertContains(response, timesince(echo.created_at))


@pytest.mark.django_db
def test_echo_waves_page_shows_404_for_nonexistent_echo(client, user):
    non_existent_echo_pk = 9999
    url = conftest.ECHO_WAVES_URL.format(echo_pk=non_existent_echo_pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_echo_waves_page_shows_no_waves_message_when_no_waves(client, user, echo):
    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertContains(response, 'No waves yet')


@pytest.mark.django_db
def test_echo_waves_page_shows_up_all_waves(client, user, echo):
    baker.make_recipe('tests.wave', echo=echo, _quantity=8)

    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    wave_count = sum(wave.content in content for wave in echo.waves.all())
    assert wave_count == 8


@pytest.mark.django_db
def test_echo_waves_page_does_not_show_view_all_waves_link(client, user, echo):
    baker.make_recipe('tests.wave', echo=echo, _quantity=3)

    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertNotContains(response, 'View all waves')


@pytest.mark.django_db
def test_echo_waves_page_contains_delete_echo_link_when_logged_user_is_echo_author(
    client, user, echo
):
    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    delete_echo_url = conftest.ECHO_DELETE_URL.format(echo_pk=echo.pk)
    assertContains(response, 'Delete echo')
    assertContains(response, delete_echo_url)


@pytest.mark.django_db
def test_echo_waves_page_does_not_contain_delete_echo_link_when_logged_user_is_not_echo_author(
    client, another_user, echo
):
    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)

    client.force_login(another_user)
    response = client.get(url)
    assert response.status_code == 200

    delete_echo_url = conftest.ECHO_DELETE_URL.format(echo_pk=echo.pk)
    assertNotContains(response, 'Delete echo')
    assertNotContains(response, delete_echo_url)


@pytest.mark.django_db
def test_echo_waves_page_contains_edit_echo_link_when_logged_user_is_echo_author(
    client, user, echo
):
    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    edit_echo_url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)
    assertContains(response, 'Edit echo')
    assertContains(response, edit_echo_url)


@pytest.mark.django_db
def test_echo_waves_page_does_not_contain_edit_echo_link_when_logged_user_is_not_echo_author(
    client, another_user, echo
):
    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)

    client.force_login(another_user)
    response = client.get(url)
    assert response.status_code == 200

    edit_echo_url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)
    assertNotContains(response, 'Edit echo')
    assertNotContains(response, edit_echo_url)


@pytest.mark.django_db
def test_echo_waves_page_contains_delete_wave_link_when_logged_user_is_wave_author(
    client, user, echo, wave
):
    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    delete_wave_url = conftest.WAVE_DELETE_URL.format(wave_pk=wave.pk)
    assertContains(response, 'Delete wave')
    assertContains(response, delete_wave_url)


@pytest.mark.django_db
def test_echo_waves_page_does_not_contain_delete_wave_link_when_logged_user_is_not_wave_author(
    client, another_user, echo, wave
):
    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)

    client.force_login(another_user)
    response = client.get(url)
    assert response.status_code == 200

    delete_wave_url = conftest.WAVE_DELETE_URL.format(wave_pk=wave.pk)
    assertNotContains(response, 'Delete wave')
    assertNotContains(response, delete_wave_url)


@pytest.mark.django_db
def test_echo_waves_page_contains_edit_wave_link_when_logged_user_is_wave_author(
    client, user, echo, wave
):
    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    edit_wave_url = conftest.WAVE_EDIT_URL.format(wave_pk=wave.pk)
    assertContains(response, 'Edit wave')
    assertContains(response, edit_wave_url)


@pytest.mark.django_db
def test_echo_waves_page_does_not_contain_edit_wave_link_when_logged_user_is_not_wave_author(
    client, another_user, echo, wave
):
    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)

    client.force_login(another_user)
    response = client.get(url)
    assert response.status_code == 200

    edit_wave_url = conftest.WAVE_EDIT_URL.format(wave_pk=wave.pk)
    assertNotContains(response, 'Edit wave')
    assertNotContains(response, edit_wave_url)