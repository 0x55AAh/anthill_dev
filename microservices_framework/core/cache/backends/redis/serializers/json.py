from microservices_framework.utils.json import json
from .base import BaseSerializer


class JSONSerializer(BaseSerializer):
    def dumps(self, value):
        return json.dumps(value).encode()

    def loads(self, value):
        return json.loads(value.decode())
