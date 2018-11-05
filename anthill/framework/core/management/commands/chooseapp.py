from anthill.framework.core.management import Command, Option


class ApplicationChooser(Command):
    help = description = 'Choose application for administration.'

    def get_options(self):
        options = (
            Option('name', help='Name of the application.'),
        )
        return options

    def run(self, *args, **kwargs):
        pass
