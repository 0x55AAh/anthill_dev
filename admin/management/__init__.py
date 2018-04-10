from microservices_framework.core.management import Command, Option, Manager
from microservices_framework.db import db


class AdminCommand(Command):
    help = 'Some help text here.'
    name = None

    option_list = (
        Option('-f', '--foo', dest='foo', default=None,
               help='some help text here'),
    )

    def run(self, *args, **kwargs):
        print('Admin command here')


class AdminManager(Manager):
    name = None


manager = AdminManager(usage='Some help text here.')


@manager.option('-f', '--foo', dest='foo', default=None,
                help="some help text here")
def foo(*args, **kwargs):
    print('Admin command here')
