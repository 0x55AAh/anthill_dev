from anthill.platform.core.messenger import handlers
from anthill.platform.core.messenger.client.backends import db


class MessengerHandler(handlers.MessengerHandler):
    client_class = db.Client
