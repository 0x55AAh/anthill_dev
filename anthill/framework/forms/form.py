from anthill.framework.forms.i18n import translations
from anthill.framework.conf import settings
from tornado.escape import to_unicode
from wtforms import form
from wtforms.meta import DefaultMeta


class InputWrapper:
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
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(Form, self).__init__(formdata, obj, prefix, **kwargs)

    class Meta(DefaultMeta):
        def get_translations(self, form):
            if not settings.USE_I18N:
                return super(Form.Meta, self).get_translations(form)
            return translations

    def process(self, formdata=None, obj=None, **kwargs):
        if formdata is not None and not hasattr(formdata, 'getlist'):
            formdata = InputWrapper(formdata)
        super(Form, self).process(formdata, obj, **kwargs)
