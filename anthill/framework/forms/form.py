from anthill.framework.forms.i18n import Translations
from anthill.framework.conf import settings
from tornado.escape import to_unicode
from wtforms import form
from wtforms.meta import DefaultMeta


class TornadoInputWrapper:
    def __init__(self, multidict):
        self._wrapped = multidict

    def __iter__(self):
        return iter(self._wrapped)

    def __len__(self):
        return len(self._wrapped)

    def __contains__(self, name):
        return name in self._wrapped

    def __getitem__(self, name):
        return self._wrapped[name]

    def __getattr__(self, name):
        return self.__getitem__(name)

    def getlist(self, name):
        try:
            return list(map(to_unicode, self._wrapped[name]))
        except KeyError:
            return []


class Form(form.Form):
    """
    A :class:`~wtforms.form.Form` that uses the Anthill's I18N
    support for translations.
    """
    _anthill_translations = Translations()

    def process(self, formdata=None, obj=None, data=None, **kwargs):
        if formdata is not None and not hasattr(formdata, 'getlist'):
            formdata = TornadoInputWrapper(formdata)
        super().process(formdata, obj, **kwargs)

    def _get_translations(self):
        if settings.USE_I18N:
            return self._anthill_translations
        return super()._get_translations()
