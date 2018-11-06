#!/usr/bin/env python3
from anthill.framework.core.exceptions import ImproperlyConfigured
from anthill.framework.core.management import Manager
import importlib
import os
import sys


class ArgvParser:
    @staticmethod
    def get_app_name():
        return sys.argv[2] if sys.argv[1] == 'app' else ''

    @staticmethod
    def clean_app_name():
        del sys.argv[1:3]


def get_settings_module(default=''):
    try:
        app_name = ArgvParser.get_app_name()
        app_manage = ('%s.manage' % app_name) if app_name else ''
        try:
            app_manage_mod = importlib.import_module(app_manage)
            return app_manage_mod.ANTHILL_SETTINGS_MODULE
        except (ValueError, ImportError):
            pass
        finally:
            app_mod = importlib.import_module(app_name)
            sys.path.insert(0, app_mod.__path__[0])
            os.chdir(app_mod.__path__[0])
    except IndexError:
        pass
    return default


if __name__ == '__main__':
    os.environ['ANTHILL_SETTINGS_MODULE'] = get_settings_module()

    try:
        import anthill.framework
        anthill.framework.setup()
    except (ImportError, ImproperlyConfigured):
        app = None
    else:
        from anthill.framework.apps import app
        ArgvParser.clean_app_name()

    kwargs = dict(app=app)

    if app is None:
        try:
            conf = importlib.import_module('conf')
            kwargs.update(root_templates_mod=getattr(conf, 'ROOT_TEMPLATES_MODULE'))
        except (ImportError, AttributeError):
            pass

    manager = Manager(**kwargs)
    manager.run()
