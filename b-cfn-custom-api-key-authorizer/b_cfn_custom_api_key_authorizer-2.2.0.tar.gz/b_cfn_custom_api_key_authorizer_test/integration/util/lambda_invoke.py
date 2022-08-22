import json
from typing import Any, Dict, Optional

from b_aws_testing_framework.credentials import Credentials


class LambdaInvoke:
    def __init__(self, function_name: str):
        self.__function_name = function_name

    def invoke(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        kwargs = dict(
            FunctionName=self.__function_name,
            InvocationType='RequestResponse'
        )

        if payload is not None:
            kwargs['Payload'] = json.dumps(payload).encode()

        response = Credentials().boto_session.client('lambda').invoke(**kwargs)

        return json.loads(response['Payload'].read())
