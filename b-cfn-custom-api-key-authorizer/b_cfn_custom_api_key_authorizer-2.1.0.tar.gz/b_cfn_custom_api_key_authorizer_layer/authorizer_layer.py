from typing import Optional, List

from aws_cdk.aws_lambda import Runtime, LayerVersion, AssetCode
from aws_cdk.core import Stack


class AuthorizerLayer(LayerVersion):
    def __init__(self, scope: Stack) -> None:
        """
        Constructor.

        :param scope: CloudFormation stack.
        """
        super().__init__(
            scope=scope,
            id='AuthorizerLayer',
            code=AssetCode(self.get_source_path()),
            compatible_runtimes=self.runtimes()
        )

    @staticmethod
    def get_source_path() -> str:
        from . import layer_root
        return f'{layer_root}/source'

    @staticmethod
    def runtimes() -> Optional[List[Runtime]]:
        return [
            Runtime.PYTHON_3_8
        ]
