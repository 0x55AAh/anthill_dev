#!/usr/bin/env python3
import os

SERVICE_SETTINGS_MODULE = os.getenv("SERVICE_SETTINGS_MODULE", "admin.settings")

if __name__ == "__main__":
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
    from microservices_framework.apps.builder import app
    from microservices_framework.core.management import build_manager

    build_manager(app).run()
