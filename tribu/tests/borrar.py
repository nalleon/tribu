import io
import re
import shutil
from functools import partial

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from model_bakery import baker
from PIL import Image
from pytest_django.asserts import assertContains, assertRedirects

from echos.models import Echo
from users.models import Profile
from waves.models import Wave

# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture
def user(django_user_model):
    u = baker.make(django_user_model, _fill_optional=True)
    baker.make(Profile, user=u, _fill_optional=True)
    return u


@pytest.fixture
def another_user(django_user_model):
    u = baker.make(django_user_model, _fill_optional=True)
    baker.make(Profile, user=u, _fill_optional=True)
    return u


@pytest.fixture
def echo(fake):
    return baker.make(Echo, content=partial(fake.paragraph, nb_sentences=10))


@pytest.fixture
def wave(fake):
    return baker.make(Wave, content=partial(fake.paragraph, nb_sentences=10))


@pytest.fixture
def fake():
    return Faker()


@pytest.fixture
def image():
    img = Image.new('RGBA', size=(200, 200), color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return SimpleUploadedFile(
        name='test_image.png',
        content=buffer.getvalue(),
        content_type='image/png',
    )


@pytest.fixture
def uploads_folder(settings):
    settings.MEDIA_ROOT = settings.BASE_DIR / 'tests/uploads/'
    uploads_folder = settings.MEDIA_ROOT
    uploads_folder.mkdir(parents=True, exist_ok=True)
    yield
    shutil.rmtree(uploads_folder, ignore_errors=True)


# ==============================================================================
# TESTS
# ==============================================================================


@pytest.mark.django_db
def test_echo_detail(client, echo, user, fake):
    TARGET_URL = f'/echos/{echo.pk}/'
    ALL_WAVES_URL = f'/echos/{echo.pk}/waves/'

    response = client.get(TARGET_URL, follow=True)
    assertRedirects(response, f'/login/?next={TARGET_URL}')
    client.force_login(user)

    # Test with 10 waves
    waves = list(
        reversed(
            baker.make(
                Wave,
                _quantity=10,
                echo=echo,
                content=partial(fake.paragraph, nb_sentences=10),
            )
        )
    )
    response = client.get(TARGET_URL)
    assert response.status_code == 200
    assertContains(response, echo.content, count=1)
    assertContains(response, echo.user.username)
    assertContains(response, ALL_WAVES_URL)
    sliced_waves = waves[:5]
    for wave in sliced_waves:
        assertContains(response, wave.content, count=1)
        assertContains(response, wave.user.username)

    # Check if waves are sorted in the right way
    assert list(response.context['waves']) == sliced_waves, (
        'El listado de "waves" no coincide con el que se esperaría.'
    )

    # Test with 2 waves
    Wave.objects.filter(pk__in=[wave.pk for wave in waves]).delete()
    waves = list(
        reversed(
            baker.make(
                Wave,
                _quantity=2,
                echo=echo,
                content=partial(fake.paragraph, nb_sentences=10),
            )
        )
    )
    response = client.get(TARGET_URL)
    assert response.status_code == 200
    assertContains(response, echo.content, count=1)
    assertContains(response, echo.user.username)
    assert re.search(rf'"{ALL_WAVES_URL}"', str(response.content)) is None, (
        'Aparece el botón de ver más "waves" cuando no debería porque ya estamos viendo todos los "waves".'
    )
    for wave in waves:
        assertContains(response, wave.content, count=1)
        assertContains(response, wave.user.username)

    # Check if waves are sorted in the right way
    assert list(response.context['waves']) == waves, (
        'El listado de "waves" no coincide con el que se esperaría.'
    )


@pytest.mark.django_db
def test_echo_waves(client, echo, user, fake):
    TARGET_URL = f'/echos/{echo.pk}/waves/'

    response = client.get(TARGET_URL, follow=True)
    assertRedirects(response, f'/login/?next={TARGET_URL}')
    client.force_login(user)

    # Test with 10 waves
    waves = list(
        reversed(
            baker.make(
                Wave,
                echo=echo,
                content=lambda: fake.paragraph(10),
                _quantity=10,
            )
        )
    )
    response = client.get(TARGET_URL)
    assert response.status_code == 200
    assertContains(response, echo.content, count=1)
    assertContains(response, echo.user.username)
    for wave in waves:
        assertContains(response, wave.content, count=1)
        assertContains(response, wave.user.username)

    # Check if waves are sorted in the right way
    assert list(response.context['waves']) == waves, (
        'El listado de "waves" no coincide con el que se esperaría.'
    )


@pytest.mark.django_db
def test_add_echo(client, user):
    TARGET_URL = '/echos/add/'
    ECHO_CONTENT = 'pytest'

    # Test NO AUTH request
    response = client.get(TARGET_URL, follow=True)
    assertRedirects(response, f'/login/?next={TARGET_URL}')

    # Test GET request
    client.force_login(user)
    response = client.get(TARGET_URL)
    assert response.status_code == 200
    assertContains(response, 'form')
    assertContains(response, 'content')

    # Test POST request
    payload = dict(content=ECHO_CONTENT)
    response = client.post(TARGET_URL, payload, follow=True)
    assert response.status_code == 200
    echo = Echo.objects.latest('pk')
    assert echo.user == user
    assert echo.content == ECHO_CONTENT
    assert echo.updated_at >= echo.created_at, (
        'La fecha de actualización de un "echo" debe ser mayor que su fecha de creación.'
    )


@pytest.mark.django_db
def test_edit_echo(client, echo, django_user_model):
    TARGET_URL = f'/echos/{echo.pk}/edit/'
    ECHO_CONTENT = 'pytest'

    # Test NO AUTH request
    response = client.get(TARGET_URL, follow=True)
    assertRedirects(response, f'/login/?next={TARGET_URL}')

    # Test edit echo with no echo author
    user = baker.make(django_user_model)
    client.force_login(user)
    response = client.get(TARGET_URL, follow=True)
    assert response.status_code == 403

    # Test GET request
    client.force_login(echo.user)
    response = client.get(TARGET_URL)
    assertContains(response, echo.content, 1, 200)

    # Test POST request
    payload = dict(content=ECHO_CONTENT)
    response = client.post(TARGET_URL, payload, follow=True)
    assert response.status_code == 200
    edited_echo = Echo.objects.get(pk=echo.pk)
    assert edited_echo.user == echo.user
    assert edited_echo.content == ECHO_CONTENT
    assert edited_echo.updated_at >= echo.created_at, (
        'La fecha de actualización de un "echo" debe ser mayor que su fecha de creación.'
    )


@pytest.mark.django_db
def test_delete_echo(client, echo, django_user_model):
    TARGET_URL = f'/echos/{echo.pk}/delete/'

    # Test NO AUTH request
    response = client.get(TARGET_URL, follow=True)
    assertRedirects(response, f'/login/?next={TARGET_URL}')

    # Test delete echo with no echo author
    user = baker.make(django_user_model)
    client.force_login(user)
    response = client.get(TARGET_URL, follow=True)
    assert response.status_code == 403
    echo = Echo.objects.get(pk=echo.pk)
    assert echo is not None, 'El "echo" no se ha borrado tras la petición.'

    # Test delete echo with echo author
    client.force_login(echo.user)
    response = client.get(TARGET_URL, follow=True)
    assert response.status_code == 200
    with pytest.raises(Echo.DoesNotExist):
        Echo.objects.get(pk=echo.pk)


@pytest.mark.django_db
def test_add_wave(client, echo, user):
    TARGET_URL = f'/echos/{echo.pk}/waves/add/'
    WAVE_CONTENT = 'pytest'

    # Test NO AUTH request
    response = client.get(TARGET_URL, follow=True)
    assertRedirects(response, f'/login/?next={TARGET_URL}')

    # Test GET request
    client.force_login(user)
    response = client.get(TARGET_URL)
    assert response.status_code == 200
    assertContains(response, 'form')
    assertContains(response, 'content')

    # Test POST request
    payload = dict(content=WAVE_CONTENT)
    response = client.post(TARGET_URL, payload, follow=True)
    assert response.status_code == 200
    wave = Wave.objects.latest('pk')
    assert wave.echo == echo
    assert wave.user == user
    assert wave.content == WAVE_CONTENT
    assert wave.updated_at >= wave.created_at, (
        'La fecha de actualización de un "wave" debe ser mayor que su fecha de creación.'
    )


@pytest.mark.django_db
def test_edit_wave(client, wave, django_user_model):
    TARGET_URL = f'/waves/{wave.pk}/edit/'
    WAVE_CONTENT = 'pytest'

    # Test NO AUTH request
    response = client.get(TARGET_URL, follow=True)
    assertRedirects(response, f'/login/?next={TARGET_URL}')

    # Test edit wave with no wave author
    user = baker.make(django_user_model)
    client.force_login(user)
    response = client.get(TARGET_URL, follow=True)
    assert response.status_code == 403

    # Test GET request
    client.force_login(wave.user)
    response = client.get(TARGET_URL)
    assertContains(response, wave.content, 1, 200)

    # Test POST request
    payload = dict(content=WAVE_CONTENT)
    response = client.post(TARGET_URL, payload, follow=True)
    assert response.status_code == 200
    edited_wave = Wave.objects.get(pk=wave.pk)
    assert edited_wave.echo == wave.echo
    assert edited_wave.user == wave.user
    assert edited_wave.content == WAVE_CONTENT
    assert edited_wave.updated_at >= edited_wave.created_at, (
        'La fecha de actualización de un "wave" debe ser mayor que su fecha de creación.'
    )


@pytest.mark.django_db
def test_delete_wave(client, wave, django_user_model):
    TARGET_URL = f'/waves/{wave.pk}/delete/'

    # Test NO AUTH request
    response = client.get(TARGET_URL, follow=True)
    assertRedirects(response, f'/login/?next={TARGET_URL}')

    # Test delete wave with no wave author
    user = baker.make(django_user_model)
    client.force_login(user)
    response = client.get(TARGET_URL, follow=True)
    assert response.status_code == 403
    echo = Wave.objects.get(pk=wave.pk)
    assert echo is not None, 'El "wave" no se ha borrado tras la petición.'

    # Test delete echo with echo author
    client.force_login(wave.user)
    response = client.get(TARGET_URL, follow=True)
    assert response.status_code == 200
    with pytest.raises(Wave.DoesNotExist):
        Wave.objects.get(pk=wave.pk)


@pytest.mark.django_db
def test_user_list(client, user, django_user_model):
    TARGET_URL = '/users/'
    USER_DETAIL_URL = '/{username}/'

    # Test NO AUTH request
    response = client.get(TARGET_URL, follow=True)
    assertRedirects(response, f'/login/?next={TARGET_URL}')

    # Test AUTH request
    users = baker.make(django_user_model, _quantity=10)
    client.force_login(user)
    response = client.get(TARGET_URL)
    assert response.status_code == 200
    for user in users:
        assertContains(response, user)
        assertContains(response, USER_DETAIL_URL.format(username=user.username))


@pytest.mark.django_db
def test_user_detail(client, user, django_user_model):
    another_user = baker.make(django_user_model)
    TARGET_URL = f'/users/{another_user}/'

    # Test NO AUTH request
    response = client.get(TARGET_URL, follow=True)
    assertRedirects(response, f'/login/?next={TARGET_URL}')

    # Test AUTH request
    client.force_login(user)
    echos = list(
        reversed(
            baker.make(
                Echo,
                user=another_user,
                _quantity=10,
            )
        )
    )
    response = client.get(TARGET_URL, follow=True)
    assert response.status_code == 200
    assertContains(response, another_user.username)
    assertContains(response, another_user.first_name)
    assertContains(response, another_user.last_name)
    assertContains(response, another_user.email)
    sliced_echos = echos[:5]
    for echo in sliced_echos:
        assertContains(response, echo.content, count=1)

    # Check if echos are sorted in the right way
    assert list(response.context['echos']) == sliced_echos, (
        'El listado de "echos" no coincide con el esperado.'
    )

    # Test user detail with ALL echos
    response = client.get(TARGET_URL + 'echos/', follow=True)
    assert response.status_code == 200
    for echo in echos:
        assertContains(response, echo.content, count=1)

    # Check if echos are sorted in the right way
    assert list(response.context['echos']) == echos, (
        'El listado de "echos" no coincide con el esperado.'
    )


@pytest.mark.django_db
def test_my_user_detail(client, user):
    TARGET_URL = '/users/@me/'

    # Test NO AUTH request
    response = client.get(TARGET_URL, follow=True)
    assertRedirects(response, f'/login/?next={TARGET_URL}')

    client.force_login(user)
    response = client.get(TARGET_URL)
    assertRedirects(response, f'/users/{user}/')


@pytest.mark.django_db
def test_profile_appears_in_user_detail(client, user):
    TARGET_URL = f'/users/{user}/'
    client.force_login(user)
    response = client.get(TARGET_URL)
    assertContains(response, user.profile.bio)
    assertContains(response, user.profile.avatar.url)


@pytest.mark.django_db
def test_profile_appears_in_user_echos(client, user):
    TARGET_URL = f'/users/{user}/echos/'
    client.force_login(user)
    response = client.get(TARGET_URL)
    assertContains(response, user.profile.bio)
    assertContains(response, user.profile.avatar.url)


@pytest.mark.django_db
def test_edit_profile_link_existence_in_user_detail(client, user, another_user):
    client.force_login(user)

    # Test if profile edit link appears on another user
    TARGET_URL = f'/users/{another_user}/'
    EDIT_PROFILE_URL = f'/users/{another_user}/edit/'
    response = client.get(TARGET_URL)
    assert re.search(rf'"{EDIT_PROFILE_URL}"', str(response.content)) is None, (
        'Aparece el botón de editar perfil cuando accedes a un usuario que no es el que está logeado.'
    )

    # Test if profile edit link does not appear on logged user
    TARGET_URL = f'/users/{user}/'
    EDIT_PROFILE_URL = f'/users/{user}/edit/'
    response = client.get(TARGET_URL)
    assert re.search(rf'"{EDIT_PROFILE_URL}"', str(response.content)) is not None, (
        'No aparece el botón de editar perfil cuando accedes al detalle del usuario logeado.'
    )


@pytest.mark.django_db
def test_edit_profile_link_existence_in_user_echos(client, user, another_user):
    client.force_login(user)

    # Test if profile edit link appears on another user
    TARGET_URL = f'/users/{another_user}/echos/'
    EDIT_PROFILE_URL = f'/users/{another_user}/edit/'
    response = client.get(TARGET_URL)
    assert re.search(rf'"{EDIT_PROFILE_URL}"', str(response.content)) is None, (
        'Aparece el botón de editar perfil cuando accedes a la lista de "echos" de un usuario que no es el que está logeado.'
    )

    # Test if profile edit link does not appear on logged user
    TARGET_URL = f'/users/{user}/echos/'
    EDIT_PROFILE_URL = f'/users/{user}/edit/'
    response = client.get(TARGET_URL)
    assert re.search(rf'"{EDIT_PROFILE_URL}"', str(response.content)) is not None, (
        'No aparece el botón de editar perfil cuando accedes a la lista de "echos" de un usuario logeado.'
    )


def test_edit_profile_with_get_request(client, user):
    TARGET_URL = f'/users/{user}/edit/'

    # Test NO AUTH request
    response = client.get(TARGET_URL, follow=True)
    assertRedirects(response, f'/login/?next={TARGET_URL}')

    # Test AUTH request
    client.force_login(user)
    response = client.get(TARGET_URL)
    assertContains(response, user.profile.avatar.url)
    assertContains(response, user.profile.bio)


def test_edit_profile_with_post_request(client, user, image, uploads_folder):  # noqa
    TARGET_URL = f'/users/{user}/edit/'
    EDITED_BIO = 'pytest'

    # Test NO AUTH request
    response = client.post(TARGET_URL)
    assertRedirects(response, f'/login/?next={TARGET_URL}')

    # Test AUTH request
    client.force_login(user)
    payload = dict(bio=EDITED_BIO, avatar=image)
    response = client.post(TARGET_URL, payload, follow=True)
    assert response.status_code == 200
    profile = Profile.objects.get(user=user)
    assert profile.bio == EDITED_BIO
    assert profile.avatar.size == image.size, (
        'La imagen de avatar que se ha subido no se ha guardado correctamente en el perfil.'
    )


@pytest.mark.django_db
def test_edit_profile_fails_when_no_author(client, user, another_user):
    TARGET_URL = f'/users/{another_user}/edit/'
    client.force_login(user)
    response = client.get(TARGET_URL)
    assert response.status_code == 403


@pytest.mark.django_db
def test_models_are_available_on_admin(admin_client):
    MODELS = ('echos.Echo', 'waves.Wave', 'users.Profile')

    for model in MODELS:
        url_model_path = model.replace('.', '/').lower()
        url = f'/admin/{url_model_path}/'
        response = admin_client.get(url)
        assert response.status_code == 200, f'El modelo <{model}> no está habilitado en el admin.'
