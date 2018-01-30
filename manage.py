#!/usr/bin/env python3
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    # from microservices_framework.utils.service import get_apps
    import ujson
    with open(os.path.join(BASE_DIR, 'apps.json')) as f:
        app_mods = ujson.load(f)['managed_apps']
    # apps = get_apps(BASE_DIR)
    app_manages = [__import__(mod + '.manage') for mod in app_mods]
    app_manages = [getattr(man, 'manage') for man in app_manages]
    apps = [getattr(man, 'SERVICE_SETTINGS_MODULE') for man in app_manages]
    for app in apps:
        os.environ["SERVICE_SETTINGS_MODULE"] = app
        # try:
        #     import microservices_framework
        #     microservices_framework.setup()
        # except ImportError:
        #     raise ImportError(
        #         "Couldn't import micro-services framework. Are you sure it's installed and "
        #         "available on your PYTHONPATH environment variable? Did you "
        #         "forget to activate a virtual environment?"
        #     )
        from microservices_framework.apps.builder import AppBuilder
        app = AppBuilder().build()
        print(app)
