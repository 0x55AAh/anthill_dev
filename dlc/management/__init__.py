from microservices_framework.core.management import Command, Option, Manager
from microservices_framework.db import db


class DLCCommand(Command):
    help = 'Some help text here.'
    name = None

    option_list = (
        Option('-f', '--foo', dest='foo', default=None,
               help='some help text here'),
    )

    def run(self, *args, **kwargs):
        print('DLC command here')


class DLCManager(Manager):
    name = None


manager = DLCManager(usage='Some help text here.')


@manager.option('-f', '--foo', dest='foo', default=None,
                help="some help text here")
def foo(*args, **kwargs):
    print('DLC command here')
