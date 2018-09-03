from wtforms_alchemy import ModelForm
from dlc.models import Bundle


class BundleForm(ModelForm):
    class Meta:
        model = Bundle
