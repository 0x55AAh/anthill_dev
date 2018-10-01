from anthill.framework.conf import settings
from moar import Thumbnailer, WandEngine
import os


THUMBNAILS_BASE_PATH = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
THUMBNAILS_URL = settings.MEDIA_URL

OPTIONS = {
    'resize': 'fill',
    'upscale': True,
    'format': None,
    'quality': 90,
    'progressive': True,
    'orientation': True,
    'optimize': False,
}

thumbnail = Thumbnailer(
    base_path=THUMBNAILS_BASE_PATH,
    base_url=THUMBNAILS_URL,
    engine=WandEngine,
    filters=None,
    echo=settings.DEBUG,
    **OPTIONS
)
