import pytest
from django.template.defaultfilters import truncatewords
from django.utils.timesince import timesince
from model_bakery import baker
from pytest_django.asserts import assertContains, assertNotContains

from tests import conftest

# ==============================================================================
# USER LIST
# ==============================================================================


@pytest.mark.django_db
def test_user_list_page_requires_authentication(client, user):
    response = client.get(conftest.USER_LIST_URL)
    assert response.status_code == 302
    assert response.url == f'/login/?next={conftest.USER_LIST_URL}'

    client.force_login(user)
    response = client.get(conftest.USER_LIST_URL)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_list_page_contains_expected_contents(client, user, django_user_model):
    client.force_login(user)
    response = client.get(conftest.USER_LIST_URL)
    assert response.status_code == 200
    for user in django_user_model.objects.filter(is_superuser=False, is_active=True):
        assertContains(response, user.username)
        assertContains(response, conftest.USER_DETAIL_URL.format(username=user.username))


# ==============================================================================
# USER DETAIL
# ==============================================================================


@pytest.mark.django_db
def test_user_detail_page_requires_authentication(client, user):
    url = conftest.USER_DETAIL_URL.format(username=user.username)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f'/login/?next={url}'

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_detail_page_contains_expected_user_info(client, user, another_user):
    client.force_login(user)

    url = conftest.USER_DETAIL_URL.format(username=another_user.username)
    response = client.get(url)

    assert response.status_code == 200
    assertContains(response, another_user.username)
    assertContains(response, another_user.first_name)
    assertContains(response, another_user.last_name)
    assertContains(response, another_user.email)
    assertContains(response, another_user.profile.bio)
    assertContains(response, another_user.profile.avatar.url)


@pytest.mark.django_db
def test_user_detail_page_contains_edit_profile_link_for_own_profile(client, user):
    client.force_login(user)

    url = conftest.USER_DETAIL_URL.format(username=user.username)
    response = client.get(url)

    assert response.status_code == 200
    edit_profile_url = f'/users/{user.username}/edit/'
    assertContains(response, edit_profile_url)


@pytest.mark.django_db
def test_user_detail_page_does_not_contain_edit_profile_link_for_another_profile(
    client, user, another_user
):
    client.force_login(user)

    url = conftest.USER_DETAIL_URL.format(username=another_user.username)
    response = client.get(url)

    assert response.status_code == 200
    edit_profile_url = f'/users/{another_user.username}/edit/'
    assertNotContains(response, edit_profile_url)


@pytest.mark.django_db
def test_user_detail_page_contains_latest_echos(client, user, another_user):
    echos = baker.make_recipe('tests.echo', user=another_user, _quantity=10)
    client.force_login(user)

    url = conftest.USER_DETAIL_URL.format(username=another_user.username)
    response = client.get(url)

    echos = sorted(echos, key=lambda e: e.created_at, reverse=True)
    for echo in echos[:5]:
        assertContains(response, truncatewords(echo.content, 20))
        assertContains(response, another_user.username)
        assertContains(response, conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk))
        assertContains(response, timesince(echo.created_at))
    for echo in echos[5:]:
        assertNotContains(response, truncatewords(echo.content, 20))
        assertNotContains(response, conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk))


@pytest.mark.django_db
def test_user_detail_page_shows_view_all_echos_link_when_exceeding_limit(
    client, user, another_user
):
    baker.make_recipe('tests.echo', user=another_user, _quantity=10)
    client.force_login(user)

    url = conftest.USER_DETAIL_URL.format(username=another_user.username)
    response = client.get(url)

    assert response.status_code == 200
    view_all_echos_url = conftest.USER_ECHOS_URL.format(username=another_user.username)
    assertContains(response, view_all_echos_url)


@pytest.mark.django_db
def test_user_detail_page_does_not_show_view_all_echos_link_when_within_limit(
    client, user, another_user
):
    baker.make_recipe('tests.echo', user=another_user, _quantity=3)
    client.force_login(user)

    url = conftest.USER_DETAIL_URL.format(username=another_user.username)
    response = client.get(url)

    assert response.status_code == 200
    view_all_echos_url = conftest.USER_ECHOS_URL.format(username=another_user.username)
    assertNotContains(response, view_all_echos_url)


@pytest.mark.django_db
def test_user_detail_page_contains_echos_in_expected_order(client, user, another_user):
    echos = baker.make_recipe('tests.echo', user=another_user, _quantity=10)
    echos = sorted(echos, key=lambda e: e.created_at, reverse=True)

    client.force_login(user)
    response = client.get(conftest.USER_DETAIL_URL.format(username=another_user.username))
    assert response.status_code == 200

    content = response.content.decode()
    last_index = -1
    for echo in echos[:5]:
        current_index = content.index(truncatewords(echo.content, 20))
        assert current_index > last_index
        last_index = current_index


@pytest.mark.django_db
def test_user_detail_page_shows_expected_message_when_no_echos(client, user, another_user):
    client.force_login(user)

    url = conftest.USER_DETAIL_URL.format(username=another_user.username)
    response = client.get(url)

    assert response.status_code == 200
    assertContains(response, 'No echos yet')


@pytest.mark.django_db
def test_user_detail_page_shows_404_for_nonexistent_user(client, user):
    non_existent_username = 'nonexistentuser'
    url = conftest.USER_DETAIL_URL.format(username=non_existent_username)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


# ==============================================================================
# USER ECHOS
# ==============================================================================


@pytest.mark.django_db
def test_user_echos_page_requires_authentication(client, user, another_user):
    url = conftest.USER_ECHOS_URL.format(username=another_user.username)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f'/login/?next={url}'

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_echos_page_contains_expected_user_info(client, user, another_user):
    client.force_login(user)

    url = conftest.USER_ECHOS_URL.format(username=another_user.username)
    response = client.get(url)

    assert response.status_code == 200
    assertContains(response, another_user.username)
    assertContains(response, another_user.first_name)
    assertContains(response, another_user.last_name)
    assertContains(response, another_user.email)
    assertContains(response, another_user.profile.bio)
    assertContains(response, another_user.profile.avatar.url)


@pytest.mark.django_db
def test_user_echos_page_contains_edit_profile_link_for_own_profile(client, user):
    client.force_login(user)

    url = conftest.USER_ECHOS_URL.format(username=user.username)
    response = client.get(url)

    assert response.status_code == 200
    edit_profile_url = conftest.PROFILE_EDIT_URL.format(username=user.username)
    assertContains(response, edit_profile_url)


@pytest.mark.django_db
def test_user_echos_page_does_not_contain_edit_profile_link_for_another_profile(
    client, user, another_user
):
    client.force_login(user)

    url = conftest.USER_ECHOS_URL.format(username=another_user.username)
    response = client.get(url)

    assert response.status_code == 200
    edit_profile_url = conftest.PROFILE_EDIT_URL.format(username=another_user.username)
    assertNotContains(response, edit_profile_url)


@pytest.mark.django_db
def test_user_echos_page_contains_all_echos(client, user, another_user):
    echos = baker.make_recipe('tests.echo', user=another_user, _quantity=7)
    client.force_login(user)

    url = conftest.USER_ECHOS_URL.format(username=another_user.username)
    response = client.get(url)

    echos = sorted(echos, key=lambda e: e.created_at, reverse=True)
    for echo in echos:
        assertContains(response, truncatewords(echo.content, 20))
        assertContains(response, another_user.username)
        assertContains(response, conftest.ECHO_DETAIL_URL.format(echo_pk=echo.pk))
        assertContains(response, timesince(echo.created_at))


@pytest.mark.django_db
def test_user_echos_page_contains_echos_in_expected_order(client, user, another_user):
    echos = baker.make_recipe('tests.echo', user=another_user, _quantity=7)
    echos = sorted(echos, key=lambda e: e.created_at, reverse=True)

    client.force_login(user)
    response = client.get(conftest.USER_ECHOS_URL.format(username=another_user.username))
    assert response.status_code == 200

    content = response.content.decode()
    last_index = -1
    for echo in echos:
        current_index = content.index(truncatewords(echo.content, 20))
        assert current_index > last_index
        last_index = current_index


@pytest.mark.django_db
def test_user_echos_page_shows_expected_message_when_no_echos(client, user, another_user):
    client.force_login(user)

    url = conftest.USER_ECHOS_URL.format(username=another_user.username)
    response = client.get(url)

    assert response.status_code == 200
    assertContains(response, 'No echos yet')


@pytest.mark.django_db
def test_user_echos_page_shows_404_for_nonexistent_user(client, user):
    non_existent_username = 'nonexistentuser'
    url = conftest.USER_ECHOS_URL.format(username=non_existent_username)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


# ==============================================================================
# ME PROFILE
# ==============================================================================


@pytest.mark.django_db
def test_my_user_detail_redirects_to_own_profile(client, user):
    client.force_login(user)

    response = client.get(conftest.PROFILE_ME_URL)
    assert response.status_code == 302
    assert response.url == conftest.USER_DETAIL_URL.format(username=user.username)


# ==============================================================================
# EDIT PROFILE
# ==============================================================================


@pytest.mark.django_db
def test_edit_profile_page_requires_authentication(client, user):
    url = conftest.PROFILE_EDIT_URL.format(username=user.username)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f'/login/?next={url}'

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_profile_page_contains_expected_form_fields(client, user):
    client.force_login(user)
    url = conftest.PROFILE_EDIT_URL.format(username=user.username)
    response = client.get(url)

    assert response.status_code == 200

    assertContains(response, '<form')
    assertContains(response, 'name="bio"')
    assertContains(response, 'name="avatar"')
    assertContains(response, 'novalidate')


@pytest.mark.django_db
def test_edit_profile_page_shows_404_for_nonexistent_user(client, user):
    non_existent_username = 'nonexistentuser'
    url = conftest.PROFILE_EDIT_URL.format(username=non_existent_username)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_edit_profile_page_forbids_editing_another_users_profile(client, user, another_user):
    client.force_login(user)
    url = conftest.PROFILE_EDIT_URL.format(username=another_user.username)
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_edit_profile_page_allows_updating_profile(
    client,
    user,
    image,
    uploads_folder,  # noqa F811
):
    client.force_login(user)
    url = conftest.PROFILE_EDIT_URL.format(username=user.username)
    new_bio = 'This is my new bio.'
    payload = {'bio': new_bio, 'avatar': image}
    response = client.post(url, payload)

    assert response.status_code == 302
    assert response.url == conftest.PROFILE_ME_URL

    user.refresh_from_db()
    assert user.profile.bio == new_bio
    assert user.profile.avatar.size == image.size, (
        'La imagen de avatar que se ha subido no se ha guardado correctamente en el perfil.'
    )


@pytest.mark.django_db
def test_edit_profile_shows_confirmation_message_after_done(client, user):
    client.force_login(user)
    url = conftest.PROFILE_EDIT_URL.format(username=user.username)
    new_bio = 'This is my new bio.'
    payload = {'bio': new_bio}
    response = client.post(url, payload, follow=True)

    assert response.status_code == 200
    assertContains(response, 'Profile updated successfully')
