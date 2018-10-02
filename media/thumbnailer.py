from anthill.framework.conf import settings
from moar import Thumbnailer, WandEngine, Storage

THUMBNAILS_DIR = getattr(settings, 'THUMBNAILS_DIR', 'thumbs')

options = {
    'resize': 'fill',
    'upscale': True,
    'format': None,
    'quality': 90,
    'progressive': True,
    'orientation': True,
    'optimize': False,
}

default_storage = Storage(
    base_path=settings.MEDIA_ROOT,
    base_url=settings.MEDIA_URL,
    thumbsdir=THUMBNAILS_DIR
)

thumbnail = Thumbnailer(
    source_storage=default_storage,
    thumbs_storage=default_storage,
    engine=WandEngine,
    filters=None,
    echo=settings.DEBUG,
    **options
)

# t = thumbnail('ZzN6KuF5zfQ.jpg', '200x100', ('crop', 50, 50))
