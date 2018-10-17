from anthill.framework.core.management.commands.base import (
    Command, Option, InvalidCommand)
from anthill.framework.core.management.utils import (
    get_random_secret_key, get_random_color)
from tornado.escape import to_unicode
from tornado.template import Template
import shutil
import os


class StartApplication(Command):
    help = description = 'Start new application.'

    # Rewrite the following suffixes when determining the target filename.
    rewrite_template_suffixes = (
        # Allow shipping invalid .py files without byte-compilation.
        ('.py-tpl', '.py'),
    )

    def __init__(self, base_dir, config_mod=None):
        super().__init__()
        self.base_dir = base_dir
        self.config_mod = config_mod
        self.default_host = 'localhost'

    def get_options(self):
        options = (
            Option('-n', '--name', dest='name', required=True, help='Name of the application.'),
            Option('-h', '--host', dest='host', default=self.default_host, help='Server hostname.'),
            Option('-p', '--port', dest='port', required=True, help='Server port number.'),
            Option('-e', '--extension', dest='extensions', default=['py'], action='append',
                   help='The file extension(s) to render (default: "py"). '
                        'Separate multiple extensions with commas, or use '
                        '-e multiple times.'),
        )
        return options

    def run(self, name, host, port, extensions):
        try:
            from importlib import import_module
            _conf = import_module(self.config_mod)
        except (ImportError, AttributeError):
            from anthill.framework import conf
            _conf = conf

        template_dir = os.path.join(_conf.__path__[0], 'app_template')

        app_dir = os.path.join(self.base_dir, name)

        try:
            os.mkdir(app_dir)
        except FileExistsError:
            raise InvalidCommand("'%s' already exists" % app_dir)
        except OSError as e:
            raise InvalidCommand(e)

        # Create a random SECRET_KEY to put it in the main settings.
        secret_key = get_random_secret_key()

        app_color = get_random_color()

        secret_key_name = 'secret_key'
        base_name = 'app_name'
        base_directory = 'app_directory'
        camel_case_name = 'camel_case_app_name'
        camel_case_value = ''.join(x for x in name.title() if x != '_')
        app_color_name = 'app_color'
        server_port_name = 'server_port'
        server_host_name = 'server_hostname'

        context = {
            base_name: name,
            base_directory: app_dir,
            camel_case_name: camel_case_value,
            secret_key_name: secret_key,
            app_color_name: app_color,
            server_port_name: port,
            server_host_name: host
        }

        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):
            path_rest = root[prefix_length:]
            relative_dir = path_rest.replace(base_name, name)

            if relative_dir:
                target_dir = os.path.join(app_dir, relative_dir)
                if not os.path.exists(target_dir):
                    os.mkdir(target_dir)

            for dirname in dirs[:]:
                if dirname.startswith('.') or dirname == '__pycache__':
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith(('.pyo', '.pyc', '.py.class')):
                    # Ignore some files as they cause various breakages.
                    continue
                old_path = os.path.join(root, filename)
                new_path = os.path.join(app_dir, relative_dir,
                                        filename.replace(base_name, name))
                for old_suffix, new_suffix in self.rewrite_template_suffixes:
                    if new_path.endswith(old_suffix):
                        new_path = new_path[:-len(old_suffix)] + new_suffix
                        break  # Only rewrite once

                if os.path.exists(new_path):
                    raise InvalidCommand("%s already exists, overlaying a "
                                         "project or app into an existing "
                                         "directory won't replace conflicting "
                                         "files" % new_path)

                # Only render the Python files, as we don't want to
                # accidentally render templates files
                if new_path.endswith(tuple(extensions)):
                    with open(old_path, 'r', encoding='utf-8') as template_file:
                        content = template_file.read()
                    template = Template(content)
                    content = template.generate(**context)
                    with open(new_path, 'w', encoding='utf-8') as new_file:
                        new_file.write(to_unicode(content))
                else:
                    shutil.copyfile(old_path, new_path)
