from anthill.platform.core.messenger.handlers.transports import websocket, socketio
from anthill.platform.core.messenger.client.backends import db


class MessengerNamespace(socketio.MessengerNamespace):
    client_class = db.Client


class MessengerHandler(websocket.MessengerHandler):
    client_class = db.Client
