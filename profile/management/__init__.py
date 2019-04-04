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
from profile.models import Profile
from typing import List
import json
import re


class ReplaceCommand(Command):
    help = 'Perform replace operations.'
    name = 'replace'

    option_list = (
        Option('-f', '--file', dest='file', default='replaces.json',
               help='JSON file with a list of replace pairs.'),
        Option('-t', '--target', dest='target',
               help='Target path of json tree.'),
        Option('-u', '--users', dest='users', default=None,
               help='User id list separated by comma.'),
    )

    @staticmethod
    def load_replaces(path: str):
        with open(path) as f:
            replaces = json.load(f)
        return replaces

    @staticmethod
    def parse_users(raw_users: str) -> List[str]:
        return re.split(r'\s*,\s*', raw_users)

    def replace(self, profile, target, replaces) -> None:
        replaces_from = (r[0] for r in replaces)
        result = profile.find_payload(target, lambda x: x.value in replaces_from)
        # targets = (r.full_path for r in result)
        for rep in replaces:
            # TODO: profile.update_payload(path, value)
            pass

    def run(self, file, target, users) -> None:
        users = self.parse_users(users)
        replaces = self.load_replaces(file)
        profiles = Profile.query.filter(Profile.user_id.in_(users)).all()
        for profile in profiles:
            self.replace(profile, target, replaces)

