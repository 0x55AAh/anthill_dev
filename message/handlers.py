from anthill.platform.core.messenger.handlers.transports import websocket, socketio
from anthill.platform.core.messenger.client.backends import db


class MessengerHandler(websocket.MessengerHandler):
    client_class = db.Client
