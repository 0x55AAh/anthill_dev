import os
import sys
import code
import inspect
import argparse
import shutil
from tornado.escape import to_unicode
from tornado.template import Template
from microservices_framework.core.management.utils import get_random_secret_key


class InvalidCommand(Exception):
    """
    This is a generic error for "bad" commands.
    It is not used in Flask-Script itself, but you should throw
    this error (or one derived from it) in your command handlers,
    and your main code should display this error's message without
    a stack trace.

    This way, we maintain interoperability if some other plug-in code
    supplies Flask-Script hooks.
    """


class Group:
    """
    Stores argument groups and mutually exclusive groups for
    `ArgumentParser.add_argument_group
    <http://argparse.googlecode.com/svn/trunk/doc/other-methods.html#argument-groups>`
    or `ArgumentParser.add_mutually_exclusive_group
    <http://argparse.googlecode.com/svn/trunk/doc/other-methods.html#add_mutually_exclusive_group>`.

    Note: The title and description params cannot be used with the exclusive
    or required params.

    :param options: A list of Option classes to add to this group
    :param title: A string to use as the title of the argument group
    :param description: A string to use as the description of the argument group
    :param exclusive: A boolean indicating if this is an argument group or a
                      mutually exclusive group
    :param required: A boolean indicating if this mutually exclusive group
                     must have an option selected
    """

    def __init__(self, *options, **kwargs):
        self.option_list = options

        self.title = kwargs.pop("title", None)
        self.description = kwargs.pop("description", None)
        self.exclusive = kwargs.pop("exclusive", None)
        self.required = kwargs.pop("required", None)

        if ((self.title or self.description) and
                (self.required or self.exclusive)):
            raise TypeError("title and/or description cannot be used with "
                            "required and/or exclusive.")

        super(Group, self).__init__(**kwargs)

    def get_options(self):
        """
        By default, returns self.option_list. Override if you
        need to do instance-specific configuration.
        """
        return self.option_list


class Option:
    """
    Stores positional and optional arguments for `ArgumentParser.add_argument
    <http://argparse.googlecode.com/svn/trunk/doc/add_argument.html>`_.

    :param name_or_flags: Either a name or a list of option strings,
                          e.g. foo or -f, --foo
    :param action: The basic type of action to be taken when this argument
                   is encountered at the command-line.
    :param nargs: The number of command-line arguments that should be consumed.
    :param const: A constant value required by some action and nargs selections.
    :param default: The value produced if the argument is absent from
                    the command-line.
    :param type: The type to which the command-line arg should be converted.
    :param choices: A container of the allowable values for the argument.
    :param required: Whether or not the command-line option may be omitted
                     (optionals only).
    :param help: A brief description of what the argument does.
    :param metavar: A name for the argument in usage messages.
    :param dest: The name of the attribute to be added to the object
                 returned by parse_args().
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Command:
    """
    Base class for creating commands.
    :param func:  Initialize this command by introspecting the function.
    """

    option_list = ()
    help_args = None

    def __init__(self, func=None):
        self.parser = None
        self.parent = None

        if func is None:
            if not self.option_list:
                self.option_list = []
            return

        args, varargs, keywords, defaults = inspect.getargspec(func)
        # args, varargs, keywords, defaults, *_ = inspect.getfullargspec(func)
        if inspect.ismethod(func):
            args = args[1:]

        options = []

        # first arg is always "app" : ignore

        defaults = defaults or []
        kwargs = dict(zip(*[reversed(l) for l in (args, defaults)]))

        for arg in args:
            if arg in kwargs:
                default = kwargs[arg]
                if isinstance(default, bool):
                    options.append(Option('-%s' % arg[0],
                                          '--%s' % arg,
                                          action="store_true",
                                          dest=arg,
                                          required=False,
                                          default=default))
                else:
                    options.append(Option('-%s' % arg[0],
                                          '--%s' % arg,
                                          dest=arg,
                                          type=str,
                                          required=False,
                                          default=default))
            else:
                options.append(Option(arg, type=str))

        self.run = func
        self.__doc__ = func.__doc__
        self.option_list = options

    @property
    def description(self):
        description = self.__doc__ or ''
        return description.strip()

    def add_option(self, option):
        """
        Adds Option to option list.
        """
        self.option_list.append(option)

    def get_options(self):
        """
        By default, returns self.option_list. Override if you
        need to do instance-specific configuration.
        """
        return self.option_list

    def create_parser(self, *args, **kwargs):
        func_stack = kwargs.pop('func_stack', ())
        parent = kwargs.pop('parent', None)
        parser = argparse.ArgumentParser(*args, add_help=False, **kwargs)
        help_args = self.help_args

        while help_args is None and parent is not None:
            help_args = parent.help_args
            parent = getattr(parent, 'parent', None)

        if help_args:
            from microservices_framework.core.management import add_help
            add_help(parser, help_args)

        for option in self.get_options():
            if isinstance(option, Group):
                if option.exclusive:
                    group = parser.add_mutually_exclusive_group(required=option.required)
                else:
                    group = parser.add_argument_group(title=option.title, description=option.description)
                for opt in option.get_options():
                    group.add_argument(*opt.args, **opt.kwargs)
            else:
                parser.add_argument(*option.args, **option.kwargs)

        parser.set_defaults(func_stack=func_stack+(self,))

        self.parser = parser
        self.parent = parent

        return parser

    def __call__(self, app=None, *args, **kwargs):
        """
        Handles the command with the given app.
        Default behaviour is to call ``self.run`` within a test request context.
        """
        return self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        """
        Runs a command. This must be implemented by the subclass. Should take
        arguments as configured by the Command options.
        """
        raise NotImplementedError


class Shell(Command):
    """
    Runs a Python shell inside application context.

    :param banner: banner appearing at top of shell when started
    :param make_context: a callable returning a dict of variables
                         used in the shell namespace. By default
                         returns a dict consisting of just the app.
    :param use_ptipython: use PtIPython shell if available, ignore if not.
                          The PtIPython shell can be turned off in command
                          line by passing the **--no-ptipython** flag.
    :param use_ptpython: use PtPython shell if available, ignore if not.
                         The PtPython shell can be turned off in command
                         line by passing the **--no-ptpython** flag.
    :param use_bpython: use BPython shell if available, ignore if not.
                        The BPython shell can be turned off in command
                        line by passing the **--no-bpython** flag.
    :param use_ipython: use IPython shell if available, ignore if not.
                        The IPython shell can be turned off in command
                        line by passing the **--no-ipython** flag.
    """

    banner = ''

    help = description = 'Runs a Python shell inside application context.'

    def __init__(self, banner=None, make_context=None, use_ipython=True,
                 use_bpython=True, use_ptipython=True, use_ptpython=True):

        self.banner = banner or self.banner
        self.use_ipython = use_ipython
        self.use_bpython = use_bpython
        self.use_ptipython = use_ptipython
        self.use_ptpython = use_ptpython

        from microservices_framework.apps import app

        if make_context is None:
            make_context = lambda: dict(app=app)

        self.make_context = make_context

        if not self.banner:
            self.banner = 'Application %s_v%s' % (app.label, app.version)

    def get_options(self):
        return (
            Option('--no-ipython', action="store_true", dest='no_ipython', default=(not self.use_ipython),
                   help="Do not use the IPython shell"),
            Option('--no-bpython', action="store_true", dest='no_bpython', default=(not self.use_bpython),
                   help="Do not use the BPython shell"),
            Option('--no-ptipython', action="store_true", dest='no_ptipython', default=(not self.use_ptipython),
                   help="Do not use the PtIPython shell"),
            Option('--no-ptpython', action="store_true", dest='no_ptpython', default=(not self.use_ptpython),
                   help="Do not use the PtPython shell"),
        )

    def get_context(self):
        """
        Returns a dict of context variables added to the shell namespace.
        """
        return self.make_context()

    def run(self, no_ipython, no_bpython, no_ptipython, no_ptpython):
        """
        Runs the shell.
        If no_ptipython is False or use_ptipython is True, then a PtIPython shell is run (if installed).
        If no_ptpython is False or use_ptpython is True, then a PtPython shell is run (if installed).
        If no_bpython is False or use_bpython is True, then a BPython shell is run (if installed).
        If no_ipython is False or use_python is True then a IPython shell is run (if installed).
        """

        context = self.get_context()

        if not no_ptipython:
            # Try PtIPython
            try:
                from ptpython.ipython import embed
                history_filename = os.path.expanduser('~/.ptpython_history')
                embed(banner1=self.banner, user_ns=context, history_filename=history_filename)
                return
            except ImportError:
                ...

        if not no_ptpython:
            # Try PtPython
            try:
                from ptpython.repl import embed
                history_filename = os.path.expanduser('~/.ptpython_history')
                embed(globals=context, history_filename=history_filename)
                return
            except ImportError:
                ...

        if not no_bpython:
            # Try BPython
            try:
                from bpython import embed
                embed(banner=self.banner, locals_=context)
                return
            except ImportError:
                ...

        if not no_ipython:
            # Try IPython
            try:
                from IPython import embed
                embed(banner1=self.banner, user_ns=context)
                return
            except ImportError:
                ...

        # Use basic python shell
        code.interact(self.banner, local=context)


class Server(Command):
    """
    Runs the server i.e. app.run()
    """

    help = description = 'Runs the server i.e. app.run().'

    def __call__(self, app=None, *args, **kwargs):
        app.run(**kwargs)

    def run(self, *args, **kwargs):
        ...


class Clean(Command):
    """
    Remove *.pyc and *.pyo files recursively starting at current directory
    """

    def run(self):
        for dirpath, dirnames, filenames in os.walk('.'):
            for filename in filenames:
                if filename.endswith('.pyc') or filename.endswith('.pyo'):
                    full_pathname = os.path.join(dirpath, filename)
                    print('Removing %s' % full_pathname)
                    os.remove(full_pathname)


class Version(Command):
    """Show app version and exit"""

    help = description = 'Show app version and exit.'

    def __call__(self, app):
        print('Application %s v%s' % (app.label, app.version))

    def run(self, *args, **kwargs):
        ...


class StartApplication(Command):
    """Start new application"""

    help = description = 'Start new application.'

    # Rewrite the following suffixes when determining the target filename.
    rewrite_template_suffixes = (
        # Allow shipping invalid .py files without byte-compilation.
        ('.py-tpl', '.py'),
    )

    def __init__(self, base_dir):
        self.base_dir = base_dir

    def get_options(self):
        options = (
            Option('-n', '--name', dest='name', required=True, help='Name of the application.'),
            Option('-e', '--extension', dest='extensions', default=['py'], action='append',
                   help='The file extension(s) to render (default: "py"). '
                        'Separate multiple extensions with commas, or use '
                        '-e multiple times.'),
        )
        return options

    def run(self, name, extensions):
        # Use conf.__path__[0] because
        # the microservices_framework install directory isn't known.
        from microservices_framework import conf
        template_dir = os.path.join(conf.__path__[0], 'app_template')

        app_dir = os.path.join(self.base_dir, name)

        try:
            os.mkdir(app_dir)
        except FileExistsError:
            raise InvalidCommand("'%s' already exists" % app_dir)
        except OSError as e:
            raise InvalidCommand(e)

        # Create a random SECRET_KEY to put it in the main settings.
        secret_key = get_random_secret_key()

        secret_key_name = 'secret_key'
        base_name = 'app_name'
        base_directory = 'app_directory'
        camel_case_name = 'camel_case_app_name'
        camel_case_value = ''.join(x for x in name.title() if x != '_')

        context = {
            base_name: name,
            base_directory: app_dir,
            camel_case_name: camel_case_value,
            secret_key_name: secret_key
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


class ApplicationChooser(Command):
    """Application chooser"""

    help = description = 'Choose application to admin.'

    def get_options(self):
        options = (
            Option('-n', '--name', dest='name', required=True, help='Name of the application.'),
        )
        return options

    def run(self, *args, **kwargs):
        pass
