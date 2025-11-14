import pytest
from pytest_django.asserts import assertContains, assertNotContains

from tests import conftest

# ==============================================================================
# LOGIN
# ==============================================================================


@pytest.mark.django_db
def test_login_page_contains_expected_elements(client):
    response = client.get(conftest.LOGIN_URL)
    assert response.status_code == 200
    assertContains(response, 'username')
    assertContains(response, 'password')
    assertContains(response, 'novalidate')
    assertContains(response, 'Login')


@pytest.mark.django_db
def test_login_fails_with_empty_credentials(client):
    response = client.post(conftest.LOGIN_URL, {})
    assert response.status_code == 200
    assertContains(response, 'This field is required.', count=2)


@pytest.mark.django_db
def test_login_fails_with_invalid_credentials(client):
    response = client.post(conftest.LOGIN_URL, {'username': 'wrong', 'password': 'wrong'})
    assert response.status_code == 200
    assertContains(response, 'Incorrect username or password')


@pytest.mark.django_db
def test_login_succeeds_with_valid_credentials(client, django_user_model):
    username, password = 'testuser', 'testpassword'
    user = django_user_model.objects.create_user(username=username, password=password)

    response = client.post(conftest.LOGIN_URL, {'username': username, 'password': password})
    assert response.status_code == 302  # Redirect on successful login

    # Check if session is created
    assert '_auth_user_id' in client.session, (
        'La sesión no se creó correctamente después del inicio de sesión'
    )
    assert str(user.id) == client.session['_auth_user_id'], (
        'El ID de usuario en la sesión no coincide con el usuario autenticado'
    )


@pytest.mark.django_db
def test_login_redirects_after_succeed_login(client, django_user_model):
    username, password = 'testuser', 'testpassword'
    django_user_model.objects.create_user(username=username, password=password)

    response = client.post('/login/', {'username': username, 'password': password})
    assert response.status_code == 302
    assert response.url == '/'


@pytest.mark.django_db
def test_login_redirects_after_succeed_login_with_next_parameter(client, django_user_model):
    username, password = 'testuser', 'testpassword'
    django_user_model.objects.create_user(username=username, password=password)

    next_url = '/echos/'
    response = client.post(f'/login/?next={next_url}', {'username': username, 'password': password})
    assert response.status_code == 302
    assert response.url == next_url


@pytest.mark.django_db
def test_login_page_contains_signup_link(client):
    response = client.get(conftest.LOGIN_URL)
    assert response.status_code == 200
    assertContains(response, conftest.SIGNUP_URL)


@pytest.mark.django_db
def test_login_page_does_not_contains_login_link(client):
    response = client.get(conftest.LOGIN_URL)
    assert response.status_code == 200
    assertNotContains(response, conftest.LOGIN_URL)


# ==============================================================================
# LOGOUT
# ==============================================================================


@pytest.mark.django_db
def test_logout_succeeds(client, django_user_model):
    username, password = 'testuser', 'testpassword'
    django_user_model.objects.create_user(username=username, password=password)

    client.login(username=username, password=password)
    response = client.get('/logout/')
    assert response.status_code == 302  # Redirect on logout
    assert '_auth_user_id' not in client.session, (
        'La sesión no se limpió correctamente después del cierre de sesión'
    )


@pytest.mark.django_db
def test_logout_redirects_after_succeed_logout(client, django_user_model):
    username, password = 'testuser', 'testpassword'
    django_user_model.objects.create_user(username=username, password=password)

    client.login(username=username, password=password)
    response = client.get('/logout/')
    assert response.status_code == 302
    assert response.url == '/'


# ==============================================================================
# SIGNUP
# ==============================================================================


@pytest.mark.django_db
def test_signup_page_contains_expected_elements(client):
    response = client.get('/signup/')
    assert response.status_code == 200
    assertContains(response, 'username')
    assertContains(response, 'password')
    assertContains(response, 'first_name')
    assertContains(response, 'last_name')
    assertContains(response, 'email')
    assertContains(response, 'novalidate')
    assertContains(response, 'Sign up')


@pytest.mark.django_db
def test_signup_fails_with_empty_data(client):
    response = client.post(conftest.SIGNUP_URL, {})
    assert response.status_code == 200
    assertContains(response, 'This field is required.', count=2)


@pytest.mark.django_db
def test_signup_succeeds_with_valid_data(client):
    signup_data = {
        'username': 'newuser',
        'password': 'strongpassword123',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newuser@example.com',
    }
    response = client.post(conftest.SIGNUP_URL, data=signup_data)
    assert response.status_code == 302
    assert '_auth_user_id' in client.session, (
        'La sesión no se creó correctamente después del registro'
    )


@pytest.mark.django_db
def test_signup_creates_empty_profile_for_new_user(client, django_user_model):
    signup_data = {
        'username': 'newuser',
        'password': 'strongpassword123',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newuser@example.com',
    }
    response = client.post(conftest.SIGNUP_URL, data=signup_data)
    assert response.status_code == 302
    user = django_user_model.objects.get(username='newuser')
    assert user.profile is not None
    assert user.profile.bio == ''
    assert user.profile.avatar == 'avatars/noavatar.png'


@pytest.mark.django_db
def test_signup_redirects_after_succeed_signup(client):
    signup_data = {
        'username': 'newuser',
        'password': 'strongpassword123',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newuser@example.com',
    }
    response = client.post(conftest.SIGNUP_URL, data=signup_data)
    assert response.status_code == 302
    assert response.url == '/'


@pytest.mark.django_db
def test_signup_fails_with_existing_username(client, django_user_model):
    existing_username = 'existinguser'
    django_user_model.objects.create_user(username=existing_username, password='password123')

    signup_data = {
        'username': existing_username,
        'password': 'newpassword123',
        'first_name': 'Existing',
        'last_name': 'User',
        'email': 'existinguser@example.com',
    }
    response = client.post(conftest.SIGNUP_URL, data=signup_data)
    assert response.status_code == 200
    assertContains(response, 'A user with that username already exists.')


@pytest.mark.django_db
def test_signup_page_contains_login_link(client):
    response = client.get(conftest.SIGNUP_URL)
    assert response.status_code == 200
    assertContains(response, conftest.LOGIN_URL)


@pytest.mark.django_db
def test_signup_page_does_not_contains_signup_link(client):
    response = client.get(conftest.SIGNUP_URL)
    assert response.status_code == 200
    assertNotContains(response, conftest.SIGNUP_URL)
