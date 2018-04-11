import logging
from anthill.common.apps import BaseAnthillApplication
from anthill.framework.conf import settings
from anthill.framework.utils.json import json

from anthill.framework.utils.encoding import force_text

logger = logging.getLogger('app')


class AnthillApplication(BaseAnthillApplication):
    """Anthill application"""
    
    def __init__(self):
        super(AnthillApplication, self).__init__()
        self.registered_services = getattr(settings, 'REGISTERED_SERVICES', {})
        try:
            if getattr(settings, 'REGISTERED_SERVICES_EXTERNAL', None):
                with open(settings.REGISTERED_SERVICES_EXTERNAL) as f:
                    self.registered_services = json.load(f)
        except Exception as e:
            logging.warning(force_text(e))
