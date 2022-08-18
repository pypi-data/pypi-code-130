from django.test import TestCase, override_settings

from patternfly.patternfly import get_patternfly_setting, include_jquery, jquery_slim_url, jquery_url

class SettingsTest(TestCase):
    def test_get_patternfly_setting(self):
        self.assertIsNone(get_patternfly_setting("SETTING_DOES_NOT_EXIST"))
        self.assertEqual("not none", get_patternfly_setting("SETTING_DOES_NOT_EXIST", "not none"))
        # Override a setting
        with self.settings(PATTERNFLY={"SETTING_DOES_NOT_EXIST": "exists now"}):
            self.assertEqual(get_patternfly_setting("SETTING_DOES_NOT_EXIST"), "exists now")

    def test_jquery_url(self):
        self.assertEqual(
            jquery_url(),
            {
                "url": "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js",
                "integrity": "sha512-bLT0Qm9VnAYZDflyKcBaQ2gg0hSYNQrJ8RilYldYQ1FxQYoCLtUjuuRuZo+fjqhx/qtq/1itJ0C2ejDxltZVFg==",
                "crossorigin": "anonymous",
            },
        )

    @override_settings(
        PATTERNFLY={
            "jquery_url": {
                "url": "https://example.com/jquery.js",
                "integrity": "we-want-a-different-jquery",
                "crossorigin": "anonymous",
            },
        }
    )
    def test_jquery_url_from_settings(self):
        self.assertEqual(
            jquery_url(),
            {
                "url": "https://example.com/jquery.js",
                "integrity": "we-want-a-different-jquery",
                "crossorigin": "anonymous",
            },
        )

    def test_jquery_slim_url(self):
        self.assertEqual(
            jquery_slim_url(),
            {
                "url": "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.slim.min.js",
                "integrity": "sha512-/DXTXr6nQodMUiq+IUJYCt2PPOUjrHJ9wFrqpJ3XkgPNOZVfMok7cRw6CSxyCQxXn6ozlESsSh1/sMCTF1rL/g==",
                "crossorigin": "anonymous",
            },
        )

    def test_include_jquery(self):
        self.assertEqual(include_jquery(), False)
        with self.settings(PATTERNFLY={"include_jquery": False}):
            self.assertEqual(include_jquery(), False)
        with self.settings(PATTERNFLY={"include_jquery": True}):
            self.assertEqual(include_jquery(), True)
        with self.settings(PATTERNFLY={"include_jquery": "full"}):
            self.assertEqual(include_jquery(), "full")
        with self.settings(PATTERNFLY={"include_jquery": "slim"}):
            self.assertEqual(include_jquery(), "slim")
