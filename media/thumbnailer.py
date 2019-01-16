"""
Usage:
    await thumbnail(source, geometry, *filters, **options)
"""
from anthill.framework.conf import settings
from anthill.framework.utils.asynchronous import as_future
from moar import Thumbnailer, WandEngine, Storage

__all__ = ['thumbnail', 'load_alias']

THUMBNAIL_DIR = getattr(settings, 'THUMBNAIL_DIR', 'thumbs')

default_options = {
    'resize': 'fill',  # 'fill', 'fit', 'stretch'
    'upscale': True,
    'format': None,  # 'JPEG', 'PNG'
    'quality': 90,
    'progressive': True,
    'orientation': True,
    'optimize': False,
}
THUMBNAIL_DEFAULT_OPTIONS = getattr(settings, 'THUMBNAIL_DEFAULT_OPTIONS', default_options)
THUMBNAIL_ALIASES = getattr(settings, 'THUMBNAIL_ALIASES', {})

default_storage = Storage(
    base_path=settings.MEDIA_ROOT,
    base_url=settings.MEDIA_URL,
    thumbsdir=THUMBNAIL_DIR
)

thumbnail = Thumbnailer(
    source_storage=default_storage,
    thumbs_storage=default_storage,
    engine=WandEngine,
    filters=None,
    echo=False,
    **THUMBNAIL_DEFAULT_OPTIONS
)
thumbnail = as_future(thumbnail)


def load_alias(alias):
    conf = THUMBNAIL_ALIASES.get(alias, None)
    if conf is not None:
        geometry = conf.get('geometry', None)
        filters = conf.get('filters', [])
        options = conf.get('options', {})
        return geometry, filters, options
