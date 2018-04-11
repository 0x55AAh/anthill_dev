#!/usr/bin/env python3
import os
import sys
import importlib
from anthill.framework.core.exceptions import ImproperlyConfigured
from anthill.framework.core.management import Manager, EmptyManager


def get_settings_module(default=''):
    try:
        has_app_context = sys.argv[1] == 'app' and sys.argv[2] in ('-n', '--name')
        app_name = sys.argv[3] if has_app_context else ''
        app_manage = ('%s.manage' % app_name) if app_name else ''
        try:
            app_manage_mod = importlib.import_module(app_manage)
            return app_manage_mod.SERVICE_SETTINGS_MODULE
        except (ValueError, ImportError):
            pass
    except IndexError:
        pass
    return default


if __name__ == '__main__':
    os.environ['SERVICE_SETTINGS_MODULE'] = get_settings_module()

    try:
        import anthill.framework
        anthill.framework.setup()
    except (ImportError, ImproperlyConfigured):
        app = None
    else:
        from anthill.framework.apps import app
        del sys.argv[1:4]

    if app is None:
        kwargs = dict(base_dir=os.path.dirname(os.path.abspath(__file__)))
        try:
            config = importlib.import_module('config')
            kwargs.update(config_mod=getattr(config, 'CONFIG_MODULE', None))
        except ImportError:
            pass
        manager = EmptyManager(**kwargs)
    else:
        manager = Manager(app=app)

    manager.run()
