from anthill.framework.handlers import WebSocketHandler


class Client:
    def create_message(self, message, to_):
        pass

    def receive_message(self, message):
        pass

    def delete_message(self, message):
        pass

    def update_message(self, message):
        pass

    def list_messages(self, from_=None):
        pass

    def read_message(self, message):
        pass


class MessengerMixin:
    pass


class MessengerHandler(MessengerMixin, WebSocketHandler):
    pass
