from django.db import connection
from django.utils.datastructures import DictWrapper
from django.db.models import PositiveSmallIntegerField


class UnsupportedBackend(Exception):
    """
    A unsupported backend was used with this field.
    """
    pass


class ISONumericField(PositiveSmallIntegerField):
    """
    PositiveSmallIntegerField with a max_value of 999.
    """

    def get_internal_type(self):
        return "PositiveSmallIntegerField"

    def formfield(self, **kwargs):
        """
        Set maximum value in *formfield* to 999.
        """
        defaults = {'min_value': 0, 'max_value': 999}
        defaults.update(kwargs)
        return super(PositiveSmallIntegerField, self).formfield(**defaults)
