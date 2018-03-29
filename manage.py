#!/usr/bin/env python3
import os
import sys
import importlib
from microservices_framework.core import exceptions, management


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
        import microservices_framework
        microservices_framework.setup()
    except (ImportError, exceptions.ImproperlyConfigured):
        app = None
    else:
        from microservices_framework.apps import app
        del sys.argv[1:4]

    if app is None:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        manager = management.EmptyManager(base_dir=BASE_DIR)
    else:
        manager = management.Manager(app=app)

    manager.run()
