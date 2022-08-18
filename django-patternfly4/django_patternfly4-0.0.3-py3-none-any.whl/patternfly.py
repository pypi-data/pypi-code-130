from importlib import import_module

from django.conf import settings

PATTERNFLY_DEFAULTS = {
    "css_url": {
        "href": "https://unpkg.com/@patternfly/patternfly@4.70.2/patternfly.min.css",
        "integrity": "sha512-bWjWdYITpRYUxiU5mbATJFGaSyto6l6uH4PM5NBxampYLIcLgZX14nk5h/GE6dchDNsB+VAPyMojw4YCtX9qow==",
        "crossorigin": "anonymous",
    },
    "css_additions_url": {
        "href": "https://unpkg.com/@patternfly/patternfly@4.70.2/patternfly-addons.css",
        "integrity": "sha512-/ro7O/bI1XeUpeB7asSaO9HPv6WBcYRptbvXfgRSoEZXR7aUiy28I7fPRm6gYrlujT6sHO3tDr+rKPuqswAgpA==",
        "crossorigin": "anonymous",
    },
    "javascript_url": {
        "url": "https://cdnjs.cloudflare.com/ajax/libs/patternfly/4.0.0-rc.1/js/patternfly.min.js",
        "integrity": "sha512-6EtzFp0bsGbfrLipEVta4ZaVZioYzJPZidyoGUO3EGy0cI7n7CSKhfJJIvDFWl0ma5p6rT4FdGULk3SYpYgmyQ==",
        "crossorigin": "anonymous",
    },
    "theme_url": None,
    "jquery_url": {
        "url": "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js",
        "integrity": "sha512-bLT0Qm9VnAYZDflyKcBaQ2gg0hSYNQrJ8RilYldYQ1FxQYoCLtUjuuRuZo+fjqhx/qtq/1itJ0C2ejDxltZVFg==",
        "crossorigin": "anonymous",
    },
    "jquery_slim_url": {
        "url": "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.slim.min.js",
        "integrity": "sha512-/DXTXr6nQodMUiq+IUJYCt2PPOUjrHJ9wFrqpJ3XkgPNOZVfMok7cRw6CSxyCQxXn6ozlESsSh1/sMCTF1rL/g==",
        "crossorigin": "anonymous",
    },
    "javascript_in_head": False,
    "include_jquery": False,
    "use_i18n": False
}


def get_patternfly_setting(name, default=None):
    """Read a setting."""
    # Start with a copy of default settings
    PATTERNFLY = PATTERNFLY_DEFAULTS.copy()

    # Override with user settings from settings.py
    PATTERNFLY.update(getattr(settings, "PATTERNFLY", {}))

    # Update use_i18n
    PATTERNFLY["use_i18n"] = i18n_enabled()

    return PATTERNFLY.get(name, default)


def jquery_url():
    """Return the full url to jQuery library file to use."""
    return get_patternfly_setting("jquery_url")


def jquery_slim_url():
    """Return the full url to slim jQuery library file to use."""
    return get_patternfly_setting("jquery_slim_url")


def include_jquery():
    """
    Return whether to include jquery.

    Setting could be False, True|'full', or 'slim'
    """
    return get_patternfly_setting("include_jquery")

def javascript_url():
    """Return the full url to the Bootstrap JavaScript file."""
    return get_patternfly_setting("javascript_url")


def css_url():
    """Return the full url to the Bootstrap CSS file."""
    return get_patternfly_setting("css_url")

def css_additions_url():
    """Return the full url to the Bootstrap CSS file."""
    return get_patternfly_setting("css_additions_url")

def theme_url():
    """Return the full url to the theme CSS file."""
    return get_patternfly_setting("theme_url")


def i18n_enabled():
    """Return the projects i18n setting."""
    return getattr(settings, "USE_I18N", False)


def get_renderer(renderers, **kwargs):
    layout = kwargs.get("layout", "")
    path = renderers.get(layout, renderers["default"])
    mod, cls = path.rsplit(".", 1)
    return getattr(import_module(mod), cls)


def get_formset_renderer(**kwargs):
    renderers = get_patternfly_setting("formset_renderers")
    return get_renderer(renderers, **kwargs)


def get_form_renderer(**kwargs):
    renderers = get_patternfly_setting("form_renderers")
    return get_renderer(renderers, **kwargs)


def get_field_renderer(**kwargs):
    renderers = get_patternfly_setting("field_renderers")
    return get_renderer(renderers, **kwargs)
