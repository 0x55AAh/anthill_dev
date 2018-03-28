#!/usr/bin/env python3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    from microservices_framework.core.management import EmptyManager

    manager = EmptyManager(base_dir=BASE_DIR)
    manager.run()
