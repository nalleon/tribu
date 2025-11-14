import io
import shutil

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker
from PIL import Image

# ==============================================================================
# URL Patterns
# ==============================================================================

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
SIGNUP_URL = '/signup/'

ECHO_LIST_URL = '/echos/'
ECHO_DETAIL_URL = '/echos/{echo_pk}/'
ECHO_ADD_URL = '/echos/add/'
ECHO_WAVES_URL = '/echos/{echo_pk}/waves/'
ECHO_EDIT_URL = '/echos/{echo_pk}/edit/'
ECHO_DELETE_URL = '/echos/{echo_pk}/delete/'

WAVE_ADD_URL = '/echos/{echo_pk}/waves/add/'
WAVE_EDIT_URL = '/waves/{wave_pk}/edit/'
WAVE_DELETE_URL = '/waves/{wave_pk}/delete/'

USER_LIST_URL = '/users/'
USER_DETAIL_URL = '/users/{username}/'
USER_ECHOS_URL = '/users/{username}/echos/'

PROFILE_ME_URL = '/users/@me/'
PROFILE_EDIT_URL = '/users/{username}/edit/'

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def user():
    user = baker.make_recipe('tests.user')
    baker.make_recipe('tests.profile', user=user)
    return user


@pytest.fixture
def user_without_profile():
    return baker.make_recipe('tests.user')


@pytest.fixture
def another_user():
    user = baker.make_recipe('tests.user')
    baker.make_recipe('tests.profile', user=user)
    return user


@pytest.fixture
def another_user_without_profile():
    return baker.make_recipe('tests.user')


@pytest.fixture
def echo(user):
    return baker.make_recipe('tests.echo', user=user)


@pytest.fixture
def wave(echo, user):
    return baker.make_recipe('tests.wave', echo=echo, user=user)


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
