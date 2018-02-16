from microservices_framework.core.management import Command, Option, Manager


class EventCommand(Command):
    help = 'Some help text here.'
    name = None

    option_list = (
        Option('-f', '--foo', dest='foo', default=None,
               help='some help text here'),
    )

    def run(self, *args, **kwargs):
        print('Event command here')


class EventManager(Manager):
    name = None


manager = EventManager(usage='Some help text here.')


@manager.option('-f', '--foo', dest='foo', default=None,
                help="some help text here")
def foo(*args, **kwargs):
    print('Event command here')
