"""Test create app."""

from service import App, create, UserSettings


def test_default():
    """Test create default."""

    assert isinstance(create(), App)


def test_with_proxy_kw():
    """Test create with proxy kwargs for super class."""

    kw = {'debug': True}
    app = create(kw=kw)
    assert app.debug


def test_with_user_settings():
    """Test create with user settings."""

    class ThirdPartySettings(UserSettings): setting = 'yeap'  # noqa
    app = create(settings=ThirdPartySettings)
    assert app.settings == ThirdPartySettings()
