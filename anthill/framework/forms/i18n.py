from anthill.framework.conf import settings
from tornado import locale


class Translations:
    def __init__(self, code):
        self.locale = locale.get(code)

    # noinspection SpellCheckingInspection
    def gettext(self, string):
        return self.locale.translate(string)

    # noinspection SpellCheckingInspection
    def ngettext(self, singular, plural, n):
        return self.locale.translate(singular, plural, n)


translations = Translations(code=settings.LOCALE)
