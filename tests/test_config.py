# tests/test_config.py
import pytest
from django.conf import settings

def test_django_configuration():
    """Verifica que Django esté configurado correctamente"""
    assert settings.configured
    assert hasattr(settings, 'AUTH_USER_MODEL')
    assert hasattr(settings, 'INSTALLED_APPS')