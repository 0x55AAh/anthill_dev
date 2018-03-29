#!/usr/bin/env python3
import os
from microservices_framework.core import management

if __name__ == '__main__':
    manager = management.EmptyManager(
        base_dir=os.path.dirname(os.path.abspath(__file__)))
    manager.run()
