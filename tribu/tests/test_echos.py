import pytest
from django.template.defaultfilters import truncatewords
from django.utils.timesince import timesince
from model_bakery import baker
from pytest_django.asserts import assertContains, assertNotContains

from echos.models import Echo
from tests import conftest


@pytest.mark.django_db
def test_echo_list_page_requires_authentication(client, user):
    response = client.get(conftest.ECHO_LIST_URL)
    assert response.status_code == 302
    assert response.url == f'/login/?next={conftest.ECHO_LIST_URL}'

    client.force_login(user)
    response = client.get(conftest.ECHO_LIST_URL)
    assert response.status_code == 200


@pytest.mark.django_db
def test_echo_list_page_contains_expected_echo_information(client, user):
    echos = baker.make_recipe('tests.echo', _quantity=10)
    # Add profile to each echo user
    for echo in echos:
        baker.make_recipe('tests.profile', user=echo.user)

    client.force_login(user)
    response = client.get(conftest.ECHO_LIST_URL)
    assert response.status_code == 200
    for echo in echos:
        assertContains(response, truncatewords(echo.content, 20))
        assertContains(response, echo.user.username)
        assertContains(response, conftest.USER_DETAIL_URL.format(username=echo.user.username))
        assertContains(response, conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk))
        assertContains(response, timesince(echo.created_at))


@pytest.mark.django_db
def test_echo_list_page_contains_echos_in_expected_order(client, user):
    echos = baker.make_recipe('tests.echo', _quantity=10)
    # Add profile to each echo user
    for echo in echos:
        baker.make_recipe('tests.profile', user=echo.user)
    echos = sorted(echos, key=lambda e: e.created_at, reverse=True)

    client.force_login(user)
    response = client.get(conftest.ECHO_LIST_URL)
    assert response.status_code == 200

    content = response.content.decode()
    last_index = -1
    for echo in echos:
        current_index = content.index(truncatewords(echo.content, 20))
        assert current_index > last_index
        last_index = current_index


@pytest.mark.django_db
def test_echo_list_page_contains_expected_number_of_echos(client, user):
    echos = baker.make_recipe('tests.echo', _quantity=7)
    # Add profile to each echo user
    for echo in echos:
        baker.make_recipe('tests.profile', user=echo.user)

    client.force_login(user)
    response = client.get(conftest.ECHO_LIST_URL)
    assert response.status_code == 200

    content = response.content.decode()
    echo_count = sum(1 for echo in echos if truncatewords(echo.content, 20) in content)
    assert echo_count == 7


@pytest.mark.django_db
def test_echo_list_page_contains_total_number_of_echos_plural(client, user):
    echos = baker.make_recipe('tests.echo', _quantity=15)
    # Add profile to each echo user
    for echo in echos:
        baker.make_recipe('tests.profile', user=echo.user)

    client.force_login(user)
    response = client.get(conftest.ECHO_LIST_URL)
    assert response.status_code == 200

    assertContains(response, f'Tribu has posted {len(echos)} echos so far!')


@pytest.mark.django_db
def test_echo_list_page_contains_total_number_of_echos_singular(client, user):
    echos = baker.make_recipe('tests.echo', _quantity=1)
    # Add profile to each echo user
    for echo in echos:
        baker.make_recipe('tests.profile', user=echo.user)

    client.force_login(user)
    response = client.get(conftest.ECHO_LIST_URL)
    assert response.status_code == 200

    assertContains(response, f'Tribu has posted {len(echos)} echo so far!')


@pytest.mark.django_db
def test_echo_list_page_shows_no_echos_message_when_empty(client, user):
    client.force_login(user)
    response = client.get(conftest.ECHO_LIST_URL)
    assert response.status_code == 200

    assertContains(response, 'No echos yet')


@pytest.mark.django_db
def test_echo_list_page_does_not_show_total_number_of_echos_when_empty(client, user):
    client.force_login(user)
    response = client.get(conftest.ECHO_LIST_URL)
    assert response.status_code == 200

    assertNotContains(response, 'Tribu has posted')


@pytest.mark.django_db
def test_echo_list_page_contains_add_echo_link(client, user):
    client.force_login(user)
    response = client.get(conftest.ECHO_LIST_URL)
    assert response.status_code == 200

    assertContains(response, 'Add echo')
    assertContains(response, conftest.ECHO_ADD_URL)


# ==============================================================================
# ADD ECHO
# ==============================================================================


@pytest.mark.django_db
def test_add_echo_page_requires_authentication(client, user):
    response = client.get(conftest.ECHO_ADD_URL)
    assert response.status_code == 302
    assert response.url == f'/login/?next={conftest.ECHO_ADD_URL}'

    client.force_login(user)
    response = client.get(conftest.ECHO_ADD_URL)
    assert response.status_code == 200


@pytest.mark.django_db
def test_add_echo_page_contains_form(client, user):
    client.force_login(user)
    response = client.get(conftest.ECHO_ADD_URL)
    assert response.status_code == 200

    assertContains(response, '<form')
    assertContains(response, 'name="content"')
    assertContains(response, 'type="submit"')
    assertContains(response, 'novalidate')


@pytest.mark.django_db
def test_add_echo_page_submits_form_and_creates_echo(client, user):
    client.force_login(user)
    response = client.post(
        conftest.ECHO_ADD_URL, data={'content': 'This is a test echo created during testing.'}
    )
    assert response.status_code == 302  # Redirect after successful form submission

    echo = Echo.objects.filter(content='This is a test echo created during testing.').first()
    assert echo is not None, 'El echo no fue creado correctamente.'
    assert echo.user == user, 'El echo no está asociado al usuario correcto.'


@pytest.mark.django_db
def test_add_echo_page_redirects_to_echo_detail_after_submission(client, user):
    client.force_login(user)
    response = client.post(
        conftest.ECHO_ADD_URL, data={'content': 'This is another test echo created during testing.'}
    )
    assert response.status_code == 302
    echo = Echo.objects.get(content='This is another test echo created during testing.')
    assert response.url == conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)


@pytest.mark.django_db
def test_add_echo_page_shows_form_errors_on_invalid_submission(client, user):
    client.force_login(user)
    response = client.post(conftest.ECHO_ADD_URL, data={'content': ''})  # Empty content
    assert response.status_code == 200  # Form re-rendered with errors

    assertContains(response, 'This field is required.')


@pytest.mark.django_db
def test_add_echo_page_contains_cancel_link(client, user):
    client.force_login(user)
    response = client.get(conftest.ECHO_ADD_URL)
    assert response.status_code == 200

    assertContains(response, 'Cancel')
    assertContains(response, conftest.ECHO_LIST_URL)


@pytest.mark.django_db
def test_add_echo_shows_confirmation_message_after_done(client, user):
    client.force_login(user)
    response = client.post(
        conftest.ECHO_ADD_URL, data={'content': 'This is a test echo for confirmation message.'}
    )
    assert response.status_code == 302  # Redirect after successful form submission

    # Follow the redirect to the echo detail page
    response = client.get(response.url)
    assert response.status_code == 200
    assertContains(response, 'Echo added successfully')


# ==============================================================================
# ECHO DETAIL
# ==============================================================================


@pytest.mark.django_db
def test_get_absolute_url_method_for_echo_works_correctly(user):
    echo = baker.make_recipe('tests.echo', user=user)
    expected_url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)
    assert echo.get_absolute_url() == expected_url


@pytest.mark.django_db
def test_echo_detail_page_requires_authentication(client, user, echo):
    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f'/login/?next={url}'

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_echo_detail_page_contains_expected_echo_information(client, user, echo):
    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertContains(response, echo.content)
    assertContains(response, echo.user.username)
    assertContains(response, conftest.USER_DETAIL_URL.format(username=echo.user.username))
    assertContains(response, timesince(echo.created_at))


@pytest.mark.django_db
def test_echo_detail_page_shows_404_for_nonexistent_echo(client, user):
    non_existent_echo_pk = 9999
    url = conftest.ECHO_DETAIL_URL.format(echo_pk=non_existent_echo_pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_echo_detail_page_shows_no_waves_message_when_no_waves(client, user, echo):
    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertContains(response, 'No waves yet')


@pytest.mark.django_db
def test_echo_detail_page_shows_up_to_limit_waves(client, user, echo):
    WAVE_LIMIT = 5
    waves = baker.make_recipe('tests.wave', echo=echo, _quantity=WAVE_LIMIT + 3)
    # Add profile to each wave user
    for wave in waves:
        baker.make_recipe('tests.profile', user=wave.user)

    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    wave_count = sum(wave.content in content for wave in echo.waves.all())
    assert wave_count == WAVE_LIMIT


@pytest.mark.django_db
def test_echo_detail_page_shows_view_all_waves_link_when_exceeding_limit(client, user, echo):
    WAVE_LIMIT = 5
    waves = baker.make_recipe('tests.wave', echo=echo, _quantity=WAVE_LIMIT + 2)
    # Add profile to each wave user
    for wave in waves:
        baker.make_recipe('tests.profile', user=wave.user)

    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertContains(response, 'View all waves')
    assertContains(response, conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk))


@pytest.mark.django_db
def test_echo_detail_page_does_not_show_view_all_waves_link_when_within_limit(client, user, echo):
    WAVE_LIMIT = 5
    waves = baker.make_recipe('tests.wave', echo=echo, _quantity=WAVE_LIMIT - 1)
    # Add profile to each wave user
    for wave in waves:
        baker.make_recipe('tests.profile', user=wave.user)

    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertNotContains(response, 'View all waves')


@pytest.mark.django_db
def test_echo_detail_page_shows_all_waves_when_within_limit(client, user, echo):
    WAVE_LIMIT = 5
    waves = baker.make_recipe('tests.wave', echo=echo, _quantity=WAVE_LIMIT - 1)
    # Add profile to each wave user
    for wave in waves:
        baker.make_recipe('tests.profile', user=wave.user)

    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    wave_count = sum(wave.content in content for wave in waves)
    assert wave_count == WAVE_LIMIT - 1


@pytest.mark.django_db
def test_echo_detail_page_shows_expected_info_about_related_waves(client, user, echo):
    waves = baker.make_recipe('tests.wave', echo=echo, _quantity=3)
    # Add profile to each wave user
    for wave in waves:
        baker.make_recipe('tests.profile', user=wave.user)

    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    for wave in waves:
        assertContains(response, wave.content)
        assertContains(response, wave.user.username)
        assertContains(response, conftest.USER_DETAIL_URL.format(username=wave.user.username))
        assertContains(response, timesince(wave.created_at))


@pytest.mark.django_db
def test_echo_detail_page_contains_add_wave_link(client, user, echo):
    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    add_wave_url = conftest.WAVE_ADD_URL.format(echo_pk=echo.pk)
    assertContains(response, 'Add wave')
    assertContains(response, add_wave_url)


@pytest.mark.django_db
def test_echo_detail_page_contains_delete_echo_link_when_logged_user_is_echo_author(
    client, user, echo
):
    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    delete_echo_url = conftest.ECHO_DELETE_URL.format(echo_pk=echo.pk)
    assertContains(response, 'Delete echo')
    assertContains(response, delete_echo_url)


@pytest.mark.django_db
def test_echo_detail_page_does_not_contain_delete_echo_link_when_logged_user_is_not_echo_author(
    client, another_user, echo
):
    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)

    client.force_login(another_user)
    response = client.get(url)
    assert response.status_code == 200

    delete_echo_url = conftest.ECHO_DELETE_URL.format(echo_pk=echo.pk)
    assertNotContains(response, 'Delete echo')
    assertNotContains(response, delete_echo_url)


@pytest.mark.django_db
def test_echo_detail_page_contains_edit_echo_link_when_logged_user_is_echo_author(
    client, user, echo
):
    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    edit_echo_url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)
    assertContains(response, 'Edit echo')
    assertContains(response, edit_echo_url)


@pytest.mark.django_db
def test_echo_detail_page_does_not_contain_edit_echo_link_when_logged_user_is_not_echo_author(
    client, another_user, echo
):
    url = conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)

    client.force_login(another_user)
    response = client.get(url)
    assert response.status_code == 200

    edit_echo_url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)
    assertNotContains(response, 'Edit echo')
    assertNotContains(response, edit_echo_url)


# ==============================================================================
# ECHO WAVES
# ==============================================================================


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
    waves = baker.make_recipe('tests.wave', echo=echo, _quantity=8)
    # Add profile to each wave user
    for wave in waves:
        baker.make_recipe('tests.profile', user=wave.user)

    url = conftest.ECHO_WAVES_URL.format(echo_pk=echo.pk)
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    wave_count = sum(wave.content in content for wave in echo.waves.all())
    assert wave_count == 8


@pytest.mark.django_db
def test_echo_waves_page_does_not_show_view_all_waves_link(client, user, echo):
    waves = baker.make_recipe('tests.wave', echo=echo, _quantity=3)
    # Add profile to each wave user
    for wave in waves:
        baker.make_recipe('tests.profile', user=wave.user)

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


# ==============================================================================
# EDIT ECHO
# ==============================================================================


@pytest.mark.django_db
def test_edit_echo_page_requires_authentication(client, user, echo):
    url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f'/login/?next={url}'

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_echo_page_contains_existing_echo_data_in_form(client, user, echo):
    url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertContains(response, '<form')
    assertContains(response, 'name="content"')
    assertContains(response, echo.content)
    assertContains(response, 'type="submit"')
    assertContains(response, 'novalidate')


@pytest.mark.django_db
def test_edit_echo_page_submits_form_and_updates_echo(client, user, echo):
    url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.post(url, data={'content': 'This is the updated content of the echo.'})
    assert response.status_code == 302  # Redirect after successful form submission

    echo.refresh_from_db()
    assert echo.content == 'This is the updated content of the echo.'


@pytest.mark.django_db
def test_edit_echo_page_redirects_to_echo_detail_after_submission(client, user, echo):
    url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.post(url, data={'content': 'This is another updated content of the echo.'})
    assert response.status_code == 302
    assert response.url == conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)


@pytest.mark.django_db
def test_edit_echo_page_shows_form_errors_on_invalid_submission(client, user, echo):
    url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.post(url, data={'content': ''})  # Empty content
    assert response.status_code == 200  # Form re-rendered with errors

    assertContains(response, 'This field is required.')


@pytest.mark.django_db
def test_edit_echo_page_contains_cancel_link(client, user, echo):
    url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertContains(response, 'Cancel')
    assertContains(response, conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk))


@pytest.mark.django_db
def test_edit_echo_page_forbidden_for_non_author(client, another_user, echo):
    url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)

    client.force_login(another_user)
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_edit_echo_page_shows_403_for_non_author_on_form_submission(client, another_user, echo):
    url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)

    client.force_login(another_user)
    response = client.post(url, data={'content': 'Attempted update by non-author.'})
    assert response.status_code == 403


@pytest.mark.django_db
def test_edit_echo_page_shows_404_for_nonexistent_echo(client, user):
    non_existent_echo_pk = 9999
    url = conftest.ECHO_EDIT_URL.format(echo_pk=non_existent_echo_pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_edit_echo_shows_confirmation_message_after_done(client, user, echo):
    url = conftest.ECHO_EDIT_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.post(
        url, data={'content': 'This is a test echo edit for confirmation message.'}
    )
    assert response.status_code == 302  # Redirect after successful form submission

    # Follow the redirect to the echo detail page
    response = client.get(response.url)
    assert response.status_code == 200
    assertContains(response, 'Echo updated successfully')


# ==============================================================================
# DELETE ECHO
# ==============================================================================


@pytest.mark.django_db
def test_delete_echo_requires_authentication(client, user, echo):
    url = conftest.ECHO_DELETE_URL.format(echo_pk=echo.pk)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f'/login/?next={url}'

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302  # Redirect after deletion


@pytest.mark.django_db
def test_delete_echo_deletes_echo_and_redirects(client, user, echo):
    url = conftest.ECHO_DELETE_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == conftest.ECHO_LIST_URL

    with pytest.raises(Echo.DoesNotExist):
        Echo.objects.get(pk=echo.pk)


@pytest.mark.django_db
def test_delete_echo_forbidden_for_non_author(client, another_user, echo):
    url = conftest.ECHO_DELETE_URL.format(echo_pk=echo.pk)

    client.force_login(another_user)
    response = client.get(url)
    assert response.status_code == 403

    # Ensure the echo still exists
    echo.refresh_from_db()


@pytest.mark.django_db
def test_delete_echo_shows_404_for_nonexistent_echo(client, user):
    non_existent_echo_pk = 9999
    url = conftest.ECHO_DELETE_URL.format(echo_pk=non_existent_echo_pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_echo_shows_confirmation_message_after_done(client, user, echo):
    url = conftest.ECHO_DELETE_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == conftest.ECHO_LIST_URL

    # Follow the redirect to the echo list page
    response = client.get(response.url)
    assert response.status_code == 200
    assertContains(response, 'Echo deleted successfully')


# ==============================================================================
# ADD WAVE
# ==============================================================================


@pytest.mark.django_db
def test_add_wave_page_requires_authentication(client, user, echo):
    url = conftest.WAVE_ADD_URL.format(echo_pk=echo.pk)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f'/login/?next={url}'

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_add_wave_page_contains_form(client, user, echo):
    url = conftest.WAVE_ADD_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertContains(response, '<form')
    assertContains(response, 'name="content"')
    assertContains(response, 'type="submit"')
    assertContains(response, 'novalidate')


@pytest.mark.django_db
def test_add_wave_page_submits_form_and_creates_wave(client, user, echo):
    url = conftest.WAVE_ADD_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.post(url, data={'content': 'This is a test wave created during testing.'})
    assert response.status_code == 302  # Redirect after successful form submission

    wave = echo.waves.filter(content='This is a test wave created during testing.').first()
    assert wave is not None, 'The wave was not created correctly.'
    assert wave.user == user, 'The wave is not associated with the correct user.'
    assert wave.echo == echo, 'The wave is not associated with the correct echo.'


@pytest.mark.django_db
def test_add_wave_page_redirects_to_echo_detail_after_submission(client, user, echo):
    url = conftest.WAVE_ADD_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.post(
        url, data={'content': 'This is another test wave created during testing.'}
    )
    assert response.status_code == 302
    assert response.url == conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk)


@pytest.mark.django_db
def test_add_wave_page_shows_form_errors_on_invalid_submission(client, user, echo):
    url = conftest.WAVE_ADD_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.post(url, data={'content': ''})  # Empty content
    assert response.status_code == 200  # Form re-rendered with errors

    assertContains(response, 'This field is required.')


@pytest.mark.django_db
def test_add_wave_page_contains_cancel_link(client, user, echo):
    url = conftest.WAVE_ADD_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertContains(response, 'Cancel')
    assertContains(response, conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk))


@pytest.mark.django_db
def test_add_wave_page_shows_404_for_nonexistent_echo(client, user):
    non_existent_echo_pk = 9999
    url = conftest.WAVE_ADD_URL.format(echo_pk=non_existent_echo_pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_add_wave_shows_confirmation_message_after_done(client, user, echo):
    url = conftest.WAVE_ADD_URL.format(echo_pk=echo.pk)

    client.force_login(user)
    response = client.post(url, data={'content': 'This is a test wave for confirmation message.'})
    assert response.status_code == 302  # Redirect after successful form submission

    # Follow the redirect to the echo detail page
    response = client.get(response.url)
    assert response.status_code == 200
    assertContains(response, 'Wave added successfully')


# ==============================================================================
# EDIT WAVE
# ==============================================================================


@pytest.mark.django_db
def test_edit_wave_page_requires_authentication(client, user, wave):
    url = conftest.WAVE_EDIT_URL.format(wave_pk=wave.pk)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f'/login/?next={url}'

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_wave_page_contains_existing_wave_data_in_form(client, user, wave):
    url = conftest.WAVE_EDIT_URL.format(wave_pk=wave.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertContains(response, '<form')
    assertContains(response, 'name="content"')
    assertContains(response, wave.content)
    assertContains(response, 'type="submit"')
    assertContains(response, 'novalidate')


@pytest.mark.django_db
def test_edit_wave_page_submits_form_and_updates_wave(client, user, wave):
    url = conftest.WAVE_EDIT_URL.format(wave_pk=wave.pk)

    client.force_login(user)
    response = client.post(url, data={'content': 'This is the updated content of the wave.'})
    assert response.status_code == 302  # Redirect after successful form submission

    wave.refresh_from_db()
    assert wave.content == 'This is the updated content of the wave.'


@pytest.mark.django_db
def test_edit_wave_page_redirects_to_echo_detail_after_submission(client, user, wave):
    url = conftest.WAVE_EDIT_URL.format(wave_pk=wave.pk)

    client.force_login(user)
    response = client.post(url, data={'content': 'This is another updated content of the wave.'})
    assert response.status_code == 302
    assert response.url == conftest.ECHO_DETAIL_URL.format(echo_pk=wave.echo.pk)


@pytest.mark.django_db
def test_edit_wave_page_shows_form_errors_on_invalid_submission(client, user, wave):
    url = conftest.WAVE_EDIT_URL.format(wave_pk=wave.pk)

    client.force_login(user)
    response = client.post(url, data={'content': ''})  # Empty content
    assert response.status_code == 200  # Form re-rendered with errors

    assertContains(response, 'This field is required.')


@pytest.mark.django_db
def test_edit_wave_page_contains_cancel_link(client, user, wave):
    url = conftest.WAVE_EDIT_URL.format(wave_pk=wave.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200

    assertContains(response, 'Cancel')
    assertContains(response, conftest.ECHO_DETAIL_URL.format(echo_pk=wave.echo.pk))


@pytest.mark.django_db
def test_edit_wave_page_forbidden_for_non_author(client, another_user, wave):
    url = conftest.WAVE_EDIT_URL.format(wave_pk=wave.pk)

    client.force_login(another_user)
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_edit_wave_page_shows_403_for_non_author_on_form_submission(client, another_user, wave):
    url = conftest.WAVE_EDIT_URL.format(wave_pk=wave.pk)

    client.force_login(another_user)
    response = client.post(url, data={'content': 'Attempted update by non-author.'})
    assert response.status_code == 403


@pytest.mark.django_db
def test_edit_wave_page_shows_404_for_nonexistent_wave(client, user):
    non_existent_wave_pk = 9999
    url = conftest.WAVE_EDIT_URL.format(wave_pk=non_existent_wave_pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_edit_wave_shows_confirmation_message_after_done(client, user, wave):
    url = conftest.WAVE_EDIT_URL.format(wave_pk=wave.pk)

    client.force_login(user)
    response = client.post(
        url, data={'content': 'This is a test wave edit for confirmation message.'}
    )
    assert response.status_code == 302  # Redirect after successful form submission

    # Follow the redirect to the echo detail page
    response = client.get(response.url)
    assert response.status_code == 200
    assertContains(response, 'Wave updated successfully')


# ==============================================================================
# DELETE WAVE
# ==============================================================================


@pytest.mark.django_db
def test_delete_wave_requires_authentication(client, user, wave):
    url = conftest.WAVE_DELETE_URL.format(wave_pk=wave.pk)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f'/login/?next={url}'

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302  # Redirect after deletion


@pytest.mark.django_db
def test_delete_wave_deletes_wave_and_redirects(client, user, wave):
    url = conftest.WAVE_DELETE_URL.format(wave_pk=wave.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == conftest.ECHO_DETAIL_URL.format(echo_pk=wave.echo.pk)

    with pytest.raises(wave._meta.model.DoesNotExist):
        wave._meta.model.objects.get(pk=wave.pk)


@pytest.mark.django_db
def test_delete_wave_redirects_to_echo_detail_after_submission(client, user, wave):
    url = conftest.WAVE_DELETE_URL.format(wave_pk=wave.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == conftest.ECHO_DETAIL_URL.format(echo_pk=wave.echo.pk)


@pytest.mark.django_db
def test_delete_wave_forbidden_for_non_author(client, another_user, wave):
    url = conftest.WAVE_DELETE_URL.format(wave_pk=wave.pk)

    client.force_login(another_user)
    response = client.get(url)
    assert response.status_code == 403

    # Ensure the wave still exists
    wave.refresh_from_db()


@pytest.mark.django_db
def test_delete_wave_shows_404_for_nonexistent_wave(client, user):
    non_existent_wave_pk = 9999
    url = conftest.WAVE_DELETE_URL.format(wave_pk=non_existent_wave_pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_wave_shows_confirmation_message_after_done(client, user, wave):
    url = conftest.WAVE_DELETE_URL.format(wave_pk=wave.pk)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == conftest.ECHO_DETAIL_URL.format(echo_pk=wave.echo.pk)

    # Follow the redirect to the echo detail page
    response = client.get(response.url)
    assert response.status_code == 200
    assertContains(response, 'Wave deleted successfully')
