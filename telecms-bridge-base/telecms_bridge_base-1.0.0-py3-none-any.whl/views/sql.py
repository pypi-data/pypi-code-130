from telecms_bridge_base.exceptions.sql import SqlError
from telecms_bridge_base.permissions import HasProjectPermissions
from telecms_bridge_base.responses.json import JSONResponse
from telecms_bridge_base.serializers.sql import SqlSerializer, SqlsSerializer
from telecms_bridge_base.views.base.api import APIView
from telecms_bridge_base.status import HTTP_400_BAD_REQUEST


class SqlView(APIView):
    permission_classes = (HasProjectPermissions,)

    def post(self, *args, **kwargs):
        if 'queries' in self.request.data:
            serializer = SqlsSerializer(data=self.request.data, context={'request': self.request})
        else:
            serializer = SqlSerializer(data=self.request.data, context={'request': self.request})

        serializer.is_valid(raise_exception=True)

        try:
            return JSONResponse(serializer.execute(serializer.validated_data))
        except SqlError as e:
            return JSONResponse({'error': e.detail.string}, status=HTTP_400_BAD_REQUEST)
