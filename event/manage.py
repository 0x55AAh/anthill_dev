#!/usr/bin/env python3
import os

SERVICE_SETTINGS_MODULE = "event.settings"

if __name__ == "__main__":
    if "SERVICE_SETTINGS_MODULE" not in os.environ:
        os.environ["SERVICE_SETTINGS_MODULE"] = SERVICE_SETTINGS_MODULE
    try:
        import microservices_framework
        microservices_framework.setup()
    except ImportError:
        raise ImportError(
            "Couldn't import micro-services framework. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
    from microservices_framework.apps import app
    from microservices_framework.core.management import Manager

    manager = Manager(app)
    manager.run()
