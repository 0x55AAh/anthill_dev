from anthill.framework.utils.crypto import get_random_string
from anthill.framework.utils.encoding import DEFAULT_LOCALE_ENCODING
from subprocess import PIPE, Popen
import random
import os


def popen_wrapper(args, stdout_encoding='utf-8'):
    """
    Friendly wrapper around Popen.

    Return stdout output, stderr output, and OS status code.
    """
    try:
        p = Popen(args, shell=False, stdout=PIPE, stderr=PIPE, close_fds=os.name != 'nt')
    except OSError as err:
        from anthill.framework.core.management.commands import InvalidCommand
        raise InvalidCommand('Error executing %s' % args[0]) from err
    output, errors = p.communicate()
    return (
        output.decode(stdout_encoding),
        errors.decode(DEFAULT_LOCALE_ENCODING, errors='replace'),
        p.returncode
    )


def find_command(cmd, path=None, pathext=None):
    if path is None:
        path = os.environ.get('PATH', '').split(os.pathsep)
    if isinstance(path, str):
        path = [path]
    # check if there are funny path extensions for executables, e.g. Windows
    if pathext is None:
        pathext = os.environ.get('PATHEXT', '.COM;.EXE;.BAT;.CMD').split(os.pathsep)
    # don't use extensions if the command ends with one of them
    for ext in pathext:
        if cmd.endswith(ext):
            pathext = ['']
            break
    # check if we find the command on PATH
    for p in path:
        f = os.path.join(p, cmd)
        if os.path.isfile(f):
            return f
        for ext in pathext:
            fext = f + ext
            if os.path.isfile(fext):
                return fext
    return None


def get_random_secret_key():
    """
    Return a 50 character random string usable as a SECRET_KEY setting value.
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)


def get_random_color():
    colors = [
        'primary', 'danger', 'success', 'warning', 'info',
        'pink', 'violet', 'purple', 'indigo', 'blue', 'teal',
        'green', 'orange', 'brown', 'grey', 'slate'
    ]
    return random.choice(colors)
