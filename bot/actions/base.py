from tornado.template import Template
from abc import ABC, abstractmethod
from typing import Callable


class BaseAction(ABC):
    @abstractmethod
    async def on_message(self, data: dict, emit: Callable) -> None:
        pass


class ResultFormatter:
    def __init__(self, template: str):
        self.template = template

    def format(self, data: dict) -> str:
        return Template(self.template).generate(**data)
