import ujson
from .base import BaseSerializer


class JSONSerializer(BaseSerializer):
    def dumps(self, value):
        return ujson.dumps(value).encode()

    def loads(self, value):
        return ujson.loads(value.decode())
