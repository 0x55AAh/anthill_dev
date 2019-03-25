import requests
import logging


logger = logging.Logger(__name__)


def get(url, params=None, **kwargs):
    pass


def post(url, data=None, **kwargs):
    pass


class ServiceError(Exception):
    pass


class Service:
    def get(self, url, params):
        pass

    def post(self, url, data):
        pass
