#!/usr/bin/env python3
from anthill.framework.core.management import EmptyManager
import os

if __name__ == '__main__':
    manager = EmptyManager(
        base_dir=os.path.dirname(os.path.abspath(__file__)))
    manager.run()
