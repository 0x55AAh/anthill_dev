from anthill.framework.conf import settings
from tornado import locale


default_locale = locale.get(settings.LANGUAGE_CODE)
translate = default_locale.translate
