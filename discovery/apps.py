from anthill.platform.apps import BaseAnthillApplication
from anthill.framework.utils.encoding import force_text
from anthill.framework.conf import settings
import logging
import json

logger = logging.getLogger('anthill.application')


class AnthillApplication(BaseAnthillApplication):
    """Anthill application."""
    
    def __init__(self):
        super().__init__()
        self.registry = getattr(settings, 'REGISTERED_SERVICES', {})
        if not self.registry:
            self.load_services_from_file()

    def load_services_from_file(self):
        fn = getattr(settings, 'REGISTERED_SERVICES_EXTERNAL', None)
        try:
            if fn is not None:
                with open(fn) as _f:
                    self.registry = json.load(_f)
        except Exception as e:
            logging.warning(force_text(e))
