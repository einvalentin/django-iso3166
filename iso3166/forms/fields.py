from django.forms.models import ModelChoiceField, smart_unicode


class CountryChoiceField(ModelChoiceField):
    """
    Instead of giving back the `pk` it will return the default language name.
    """

    def label_from_instance(self, obj):
        return smart_unicode(obj.get_name())
