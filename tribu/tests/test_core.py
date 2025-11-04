import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

from echos.models import Echo
from users.models import Profile
from waves.models import Wave

User = get_user_model()


@pytest.mark.django_db
def test_required_apps_are_installed():
    REQUIRED_APPS = ('shared', 'accounts', 'echos', 'waves', 'users')

    custom_apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django')]
    for app in REQUIRED_APPS:
        app_config = f'{app}.apps.{app.title()}Config'
        assert app_config in custom_apps, (
            f'La aplicación <{app}> no está "creada/instalada" en el proyecto.'
        )
    assert len(custom_apps) >= len(REQUIRED_APPS), (
        'El número de aplicaciones propias definidas en el proyecto no es correcto.'
    )


@pytest.mark.django_db
def test_echo_model_is_correctly_configured():
    assert (content := Echo._meta.get_field('content')), (
        'El campo <content> no está en el modelo Echo.'
    )
    assert content.get_internal_type() == 'TextField', (
        'El campo <content> del modelo Echo no es del tipo esperado.'
    )
    assert (created_at := Echo._meta.get_field('created_at')), (
        'El campo <created_at> no está en el modelo Echo.'
    )
    assert created_at.get_internal_type() == 'DateTimeField', (
        'El campo <created_at> del modelo Echo no es del tipo esperado.'
    )
    assert created_at.auto_now_add, (
        'El campo <created_at> del modelo Echo no tiene auto_now_add configurado.'
    )
    assert (updated_at := Echo._meta.get_field('updated_at')), (
        'El campo <updated_at> no está en el modelo Echo.'
    )
    assert updated_at.get_internal_type() == 'DateTimeField', (
        'El campo <updated_at> del modelo Echo no es del tipo esperado.'
    )
    assert updated_at.auto_now, (
        'El campo <updated_at> del modelo Echo no tiene auto_now configurado.'
    )
    assert (user := Echo._meta.get_field('user')), 'El campo <user> no está en el modelo Echo.'
    assert user.get_internal_type() == 'ForeignKey', (
        'El campo <user> del modelo Echo no es del tipo esperado.'
    )
    assert user.remote_field.model == User, (
        'El campo <user> del modelo Echo no tiene la relación correcta con el modelo de usuario.'
    )
    assert user.remote_field.on_delete.__name__ == 'CASCADE', (
        'El campo <user> del modelo Echo no tiene la opción on_delete correcta.'
    )
    assert user.remote_field.related_name == 'echos', (
        'El campo <user> del modelo Echo no tiene el related_name correcto.'
    )


@pytest.mark.django_db
def test_wave_model_is_correctly_configured():
    assert (content := Wave._meta.get_field('content')), (
        'El campo <content> no está en el modelo Wave.'
    )
    assert content.get_internal_type() == 'TextField', (
        'El campo <content> del modelo Wave no es del tipo esperado.'
    )
    assert (created_at := Wave._meta.get_field('created_at')), (
        'El campo <created_at> no está en el modelo Wave.'
    )
    assert created_at.get_internal_type() == 'DateTimeField', (
        'El campo <created_at> del modelo Wave no es del tipo esperado.'
    )
    assert created_at.auto_now_add, (
        'El campo <created_at> del modelo Wave no tiene auto_now_add configurado.'
    )
    assert (updated_at := Wave._meta.get_field('updated_at')), (
        'El campo <updated_at> no está en el modelo Wave.'
    )
    assert updated_at.get_internal_type() == 'DateTimeField', (
        'El campo <updated_at> del modelo Wave no es del tipo esperado.'
    )
    assert updated_at.auto_now, (
        'El campo <updated_at> del modelo Wave no tiene auto_now configurado.'
    )
    assert (user := Wave._meta.get_field('user')), 'El campo <user> no está en el modelo Wave.'
    assert user.get_internal_type() == 'ForeignKey', (
        'El campo <user> del modelo Wave no es del tipo esperado.'
    )
    assert user.remote_field.model == User, (
        'El campo <user> del modelo Wave no tiene la relación correcta con el modelo de usuario.'
    )
    assert user.remote_field.on_delete.__name__ == 'CASCADE', (
        'El campo <user> del modelo Wave no tiene la opción on_delete correcta.'
    )
    assert user.remote_field.related_name == 'waves', (
        'El campo <user> del modelo Wave no tiene el related_name correcto.'
    )
    assert (echo := Wave._meta.get_field('echo')), 'El campo <echo> no está en el modelo Wave.'
    assert echo.get_internal_type() == 'ForeignKey', (
        'El campo <echo> del modelo Wave no es del tipo esperado.'
    )
    assert echo.remote_field.model == Echo, (
        'El campo <echo> del modelo Wave no tiene la relación correcta con el modelo Echo.'
    )
    assert echo.remote_field.on_delete.__name__ == 'CASCADE', (
        'El campo <echo> del modelo Wave no tiene la opción on_delete correcta.'
    )
    assert echo.remote_field.related_name == 'waves', (
        'El campo <echo> del modelo Wave no tiene el related_name correcto.'
    )


@pytest.mark.django_db
def test_profile_model_is_correctly_configured():
    assert (user := Profile._meta.get_field('user')), (
        'El campo <user> no está en el modelo Profile.'
    )
    assert user.get_internal_type() == 'OneToOneField', (
        'El campo <user> del modelo Profile no es del tipo esperado.'
    )
    assert user.remote_field.model == User, (
        'El campo <user> del modelo Profile no tiene la relación correcta con el modelo de usuario.'
    )
    assert user.remote_field.on_delete.__name__ == 'CASCADE', (
        'El campo <user> del modelo Profile no tiene la opción on_delete correcta.'
    )

    assert (avatar := Profile._meta.get_field('avatar')), (
        'El campo <avatar> no está en el modelo Profile.'
    )
    assert avatar.get_internal_type() in ['FileField', 'ImageField'], (
        'El campo <avatar> del modelo Profile no es del tipo esperado.'
    )
    assert avatar.upload_to == 'avatars', (
        'El campo <avatar> del modelo Profile no tiene el upload_to correcto.'
    )
    assert avatar.default == 'avatars/noavatar.png', (
        'El campo <avatar> del modelo Profile no tiene el valor por defecto correcto.'
    )

    assert (bio := Profile._meta.get_field('bio')), 'El campo <bio> no está en el modelo Profile.'
    assert bio.get_internal_type() == 'TextField', (
        'El campo <bio> del modelo Profile no es del tipo esperado.'
    )
    assert bio.blank, 'El campo <bio> del modelo Profile no tiene su opcionalidad bien definida.'
    assert not bio.null, 'El campo <bio> del modelo Profile no tiene su opcionalidad bien definida.'
