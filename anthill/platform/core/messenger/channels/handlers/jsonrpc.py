from anthill.framework.handlers import JSONRPCHandler
from anthill.platform.core.messenger.channels.handlers.base import ChannelHandlerMixin
from anthill.platform.core.messenger.channels.exceptions import InvalidChannelLayerError
from anthill.platform.core.messenger.channels.layers import get_channel_layer
from tornado.ioloop import IOLoop
import functools
import json


class JSONRPCChannelHandler(ChannelHandlerMixin, JSONRPCHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        IOLoop.current().add_callback(self.channel_receive_callback)

        self.channel_layer = None
        self.channel_name = None
        self.channel_receive = None
