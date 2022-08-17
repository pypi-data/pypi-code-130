from w.tests.helpers import service_test_helper

from w.services.technical.key_generator_service import KeyGeneratorService
from w.tests.mixins.testcase_mixin import TestCaseMixin


class TestKeyGeneratorService(TestCaseMixin):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.left = "left"
        cls.right = "right"

    @staticmethod
    def _get_generate_secret_key_mock_config():
        return {
            "service": KeyGeneratorService,
            "method_name": "generate_secret_key",
            "return_value": "IGmACdiN.LHqgrtu7Q9CnUDNrkCZec8a0A5p57ph5",
        }

    """
    _concatenate
    """

    def test__concatenate_with_success_return_str(self):
        """Ensure method return the concatenation of the two values passed
        in parameter
        """
        assert (
            KeyGeneratorService._concatenate(self.left, self.right)
            == f"{self.left}.{self.right}"
        )

    """
    generate_secret_key
    """

    def test_generate_secret_key_with_success_return_str(self):
        """Ensure method return random secret key"""
        with service_test_helper.mock_service(
            **self._get_generate_secret_key_mock_config()
        ):
            assert (
                KeyGeneratorService.generate_secret_key()
                == "IGmACdiN.LHqgrtu7Q9CnUDNrkCZec8a0A5p57ph5"
            )
