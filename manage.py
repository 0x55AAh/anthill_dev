#!/usr/bin/env python3
import os
import sys
import importlib

if __name__ == '__main__':
    app_manage_mod = None
    try:
        app_name = sys.argv[3] if sys.argv[1] == 'app' and sys.argv[2] in ('-n', '--name') else ''
        app_manage = ('%s.manage' % app_name) if app_name else ''
        try:
            app_manage_mod = importlib.import_module(app_manage)
            os.environ["SERVICE_SETTINGS_MODULE"] = app_manage_mod.SERVICE_SETTINGS_MODULE
        except (ValueError, ImportError):
            pass
    except IndexError:
        pass

    from microservices_framework.core.exceptions import ImproperlyConfigured
    try:
        import microservices_framework
        microservices_framework.setup()
    except (ImportError, ImproperlyConfigured):
        app = None
    else:
        from microservices_framework.apps import app
        del sys.argv[1:4]

    from microservices_framework.core.management import EmptyManager, Manager
    if not app:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        manager = EmptyManager(base_dir=BASE_DIR)
    else:
        manager = Manager(app=app)

    manager.run()
