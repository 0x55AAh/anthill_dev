from anthill.framework.conf import settings
from tornado import locale


default_locale = locale.get(settings.LOCALE)
translate = default_locale.translate
pgettext = default_locale.pgettext
