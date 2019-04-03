"""
Example:

    from anthill.framework.core.management import Command, Option, Manager


    class YourCommand(Command):
        help = 'Some help text here.'
        name = None

        option_list = (
            Option('-f', '--foo', dest='foo', default=None,
                   help='some help text here.'),
        )

        def run(self, *args, **kwargs):
            # Your command here.
            pass


    class YourManager(Manager):
        name = None


    manager = YourManager(usage='Some help text here.')


    @manager.option('-f', '--foo', dest='foo', default=None,
                    help="some help text here.")
    def foo(*args, **kwargs):
        # Your command here.
        pass

"""
from anthill.framework.core.management import Command, Option, Manager


class ReplaceCommand(Command):
    help = 'Perform replace operations.'
    name = 'replace'

    option_list = (
        Option('-f', '--file', dest='file', default='replaces.json',
               help='JSON file with a list of replace pairs.'),
    )

    def run(self, *args, **kwargs):
        pass

