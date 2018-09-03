from anthill.framework.forms.orm import (
    ModelForm, ModelUpdateForm, ModelCreateForm, ModelSearchForm)
from wtforms_alchemy import ClassMap
from wtforms.fields import TextAreaField
from sqlalchemy_jsonfield import JSONField
from dlc.models import Bundle


class BundleForm(ModelForm):
    class Meta:
        type_map = ClassMap({
            JSONField: TextAreaField,
        })
        model = Bundle
