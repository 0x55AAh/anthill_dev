from anthill.framework.core.management import Command, Option
from profile.models import Profile
from typing import List, Optional, Dict, Any
from json.decoder import JSONDecodeError
import tqdm
import json
import re
import sys


NO_REPLACES_ERROR = 1
GET_REPLACES_ERROR = 2


class ReplaceCommand(Command):
    help = 'Perform replace operations.'
    name = 'replace'

    option_list = (
        Option('-f', '--file', dest='file', default='replaces.json',
               help='JSON file with a list of replace pairs.'),
        Option('-t', '--target', dest='target', default='$',
               help='Target path of json tree.'),
        Option('-u', '--users', dest='users', default=None,
               help='User id list separated by commas.'),
    )

    @staticmethod
    def _load_replaces(path: str) -> Dict[Any, Any]:
        """Load replace pairs from JSON file."""
        with open(path) as f:
            replaces = json.load(f)
        return dict(replaces)

    def get_replaces(self, path: str) -> Dict[Any, Any]:
        try:
            replaces = self._load_replaces(path)
            if not replaces:
                self.stdout.write('No replaces to perform.')
                sys.exit(NO_REPLACES_ERROR)
        except (FileNotFoundError, JSONDecodeError) as e:
            self.stderr.write(str(e))
            sys.exit(GET_REPLACES_ERROR)
        return replaces

    @staticmethod
    def parse_users(raw_users: Optional[str] = None) -> List[str]:
        """
        Parse string of user ids list separated by commas.
        :return: user ids list.
        """
        if raw_users is not None:
            return re.split(r'\s*,\s*', raw_users)
        return []

    @staticmethod
    def get_profiles(users: Optional[List[str]] = None) -> List[Profile]:
        """Load profiles from database."""
        query = Profile.query
        if users:
            query = query.filter(Profile.user_id.in_(users))
        return query.all()

    @staticmethod
    def replace(profile: Profile, target: str, replaces: Dict[Any, Any]) -> None:
        """Apply all replace operations on profile payload."""
        matches = profile.find_payload(target, lambda x: x.value in replaces)
        for match in matches:
            new_value = replaces[match.value]
            # do replace operation without committing to database
            profile.update_payload(match.full_path, new_value, commit=False)
        if matches:
            # finally commit changes to database
            profile.save()

    def run(self, file: str, target: str, users: Optional[str] = None) -> None:
        replaces = self.get_replaces(file)
        profiles = self.get_profiles(users=self.parse_users(users))

        with tqdm.tqdm(total=len(profiles), unit=' profile') as pb:
            for profile in profiles:
                self.replace(profile, target, replaces)
                pb.update()
