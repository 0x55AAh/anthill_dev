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
from typing import List, Optional, Dict, Any
import tqdm
import json
import re


class ReplaceCommand(Command):
    help = 'Perform replace operations.'
    name = 'replace'

    option_list = (
        Option('-f', '--file', dest='file', default='replaces.json',
               help='JSON file with a list of replace pairs.'),
        Option('-t', '--target', dest='target', default='$',
               help='Target path of json tree.'),
        Option('-u', '--users', dest='users', default=None,
               help='User id list separated by comma.'),
    )

    @staticmethod
    def load_replaces(path: str) -> Dict[Any, Any]:
        with open(path) as f:
            replaces = json.load(f)
        return dict(replaces)

    @staticmethod
    def parse_users(raw_users: Optional[str] = None) -> List[str]:
        if raw_users is not None:
            return re.split(r'\s*,\s*', raw_users)
        return []

    @staticmethod
    def get_profiles(users: Optional[List[str]] = None) -> List[Profile]:
        query = Profile.query
        if users:
            query = query.filter(Profile.user_id.in_(users))
        return query.all()

    @staticmethod
    def replace(profile: Profile, target: str, replaces: Dict[Any, Any]) -> None:
        matches = profile.find_payload(target, lambda x: x.value in replaces)
        for match in matches:
            new_value = replaces[match.value]
            # do replace operation without committing to database
            profile.update_payload(match.full_path, new_value, commit=False)
        if matches:
            # finally commit changes to database
            profile.save()

    def run(self, file: str, target: str, users: Optional[str] = None) -> None:
        try:
            replaces = self.load_replaces(file)
        except FileNotFoundError as e:
            self.stderr.write(str(e))
            return

        if not replaces:
            self.stdout.write('No replaces to perform.')
            return

        users = self.parse_users(users)
        profiles = self.get_profiles(users)

        with tqdm.tqdm(total=len(profiles), unit=' profile') as pb:
            for profile in profiles:
                self.replace(profile, target, replaces)
                pb.update()
